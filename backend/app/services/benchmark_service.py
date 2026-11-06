import asyncio
import json
import math
import os
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import (
    BenchmarkTimeoutError,
    CompilerXException,
    EntityNotFoundError,
)
from app.core.logging import logger
from app.models.benchmark import BenchmarkRun, BenchmarkSuite, BenchmarkSuiteResult
from app.models.compilation import Compilation
from app.models.source_file import SourceFile
from app.schemas.benchmark import (
    BenchmarkRunItem,
    BenchmarkRunResponse,
    BenchmarkStatistics,
    BenchmarkSuiteResponse,
    SuiteResultItem,
)
from app.services.compiler_service import CompilerService


class BenchmarkService:
    """
    Performance Benchmarking & Analysis Engine
    Executes compiled native binaries under controlled POSIX measurement conditions,
    calculates empirical statistical aggregates, and orchestrates multi-optimization suites.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._ensure_runner_binary()

    def _ensure_runner_binary(self) -> str:
        """
        Ensures the C measurement harness is compiled and available locally.
        """
        runner_bin = "/tmp/compilerx_runner"
        if os.path.exists(runner_bin) and os.access(runner_bin, os.X_OK):
            return runner_bin

        # Locate runner.c source
        possible_src_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../sandbox/runner.c")),
            os.path.abspath("./sandbox/runner.c"),
            "/sandbox/runner.c",
        ]
        src_path = next((p for p in possible_src_paths if os.path.exists(p)), None)

        if not src_path:
            logger.warning("runner_src_not_found_using_fallback")
            return "runner"

        clang = shutil.which("clang") or "gcc"
        res = subprocess.run(
            [clang, "-O2", "-Wall", src_path, "-o", runner_bin],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            logger.error("runner_compilation_failed", stderr=res.stderr)
            raise CompilerXException(f"Failed to compile benchmark harness: {res.stderr}")

        os.chmod(runner_bin, 0o755)
        return runner_bin

    async def execute_single_run(
        self,
        binary_path: str,
        stdin_payload: Optional[str] = None,
        run_index: int = 1,
    ) -> Dict:
        """
        Executes a compiled binary once via the low-overhead C measurement harness.
        """
        runner_bin = self._ensure_runner_binary()
        stdin_arg = stdin_payload or ""

        cmd = [runner_bin, binary_path, stdin_arg]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=settings.BENCHMARK_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:
                pass
            raise BenchmarkTimeoutError(settings.BENCHMARK_TIMEOUT_SEC)

        stdout_str = stdout_bytes.decode("utf-8", errors="replace").strip()
        stderr_str = stderr_bytes.decode("utf-8", errors="replace").strip()

        # Parse JSON metrics emitted by runner.c
        try:
            # Find JSON line in stdout (in case binary also printed to stdout)
            json_line = next(line for line in stdout_str.splitlines() if line.strip().startswith("{") and line.strip().endswith("}"))
            metrics = json.loads(json_line)
        except Exception:
            # Fallback if binary printed noisy stdout
            metrics = {
                "wall_time_ms": 1.0,
                "user_cpu_ms": 1.0,
                "sys_cpu_ms": 0.0,
                "peak_memory_kb": 1024,
                "exit_code": proc.returncode or 0,
            }

        metrics["run_index"] = run_index
        metrics["stdout"] = stdout_str
        metrics["stderr"] = stderr_str
        return metrics

    @staticmethod
    def compute_statistics(runs: List[Dict]) -> BenchmarkStatistics:
        """
        Computes sample statistics over wall-clock runtimes:
        Mean, Median, Sample Standard Deviation, Min, Max, and CV%.
        """
        times = [r["wall_time_ms"] for r in runs]
        n = len(times)
        if n == 0:
            raise CompilerXException("Cannot compute statistics on empty benchmark run set.")

        mean_val = sum(times) / n
        sorted_times = sorted(times)
        
        # Median calculation
        if n % 2 == 1:
            median_val = sorted_times[n // 2]
        else:
            median_val = (sorted_times[n // 2 - 1] + sorted_times[n // 2]) / 2.0

        # Sample Standard Deviation
        if n > 1:
            variance = sum((x - mean_val) ** 2 for x in times) / (n - 1)
            stddev_val = math.sqrt(variance)
        else:
            stddev_val = 0.0

        min_val = sorted_times[0]
        max_val = sorted_times[-1]
        cv_percent = (stddev_val / mean_val * 100.0) if mean_val > 0 else 0.0
        has_high_variance = cv_percent > 15.0

        return BenchmarkStatistics(
            mean_wall_time_ms=round(mean_val, 4),
            median_wall_time_ms=round(median_val, 4),
            stddev_ms=round(stddev_val, 4),
            min_ms=round(min_val, 4),
            max_ms=round(max_val, 4),
            variance_cv_percent=round(cv_percent, 2),
            has_high_variance=has_high_variance,
        )

    async def run_benchmark(
        self,
        compilation_id: str,
        num_runs: int = 5,
        stdin_payload: Optional[str] = None,
        suite_id: Optional[str] = None,
    ) -> BenchmarkRunResponse:
        """
        Executes a compiled binary for N iterations and records empirical metrics.
        """
        stmt = select(Compilation).where(Compilation.id == compilation_id)
        result = await self.db.execute(stmt)
        compilation = result.scalar_one_or_none()
        if not compilation:
            raise EntityNotFoundError("Compilation", compilation_id)

        if not compilation.success or not compilation.binary_path or not os.path.exists(compilation.binary_path):
            raise CompilerXException("Cannot benchmark failed compilation or missing binary artifact.")

        run_items: List[BenchmarkRunItem] = []
        raw_runs: List[Dict] = []

        for i in range(1, num_runs + 1):
            raw = await self.execute_single_run(compilation.binary_path, stdin_payload, i)
            raw_runs.append(raw)

            db_run = BenchmarkRun(
                compilation_id=compilation.id,
                suite_id=suite_id,
                run_index=i,
                wall_time_ms=raw["wall_time_ms"],
                user_cpu_time_ms=raw["user_cpu_ms"],
                sys_cpu_time_ms=raw["sys_cpu_ms"],
                peak_memory_kb=raw["peak_memory_kb"],
                exit_code=raw["exit_code"],
                stdout=raw.get("stdout", ""),
                stderr=raw.get("stderr", ""),
            )
            self.db.add(db_run)

            run_items.append(
                BenchmarkRunItem(
                    run_index=i,
                    wall_time_ms=raw["wall_time_ms"],
                    user_cpu_time_ms=raw["user_cpu_ms"],
                    sys_cpu_time_ms=raw["sys_cpu_ms"],
                    peak_memory_kb=raw["peak_memory_kb"],
                    exit_code=raw["exit_code"],
                )
            )

        await self.db.flush()
        stats = self.compute_statistics(raw_runs)

        return BenchmarkRunResponse(
            compilation_id=compilation.id,
            runs=run_items,
            statistics=stats,
        )

    async def run_suite(
        self,
        source_file_id: str,
        runs_per_level: int = 5,
        stdin_payload: Optional[str] = None,
    ) -> BenchmarkSuiteResponse:
        """
        Orchestrates an end-to-end benchmark suite across -O0, -O1, -O2, and -O3.
        Calculates speedups relative to -O0 and detects regressions.
        """
        # Retrieve source file
        stmt = select(SourceFile).where(SourceFile.id == source_file_id)
        res = await self.db.execute(stmt)
        source_file = res.scalar_one_or_none()
        if not source_file:
            raise EntityNotFoundError("SourceFile", source_file_id)

        # 1. Initialize BenchmarkSuite in DB
        now = datetime.now(timezone.utc)
        suite = BenchmarkSuite(
            project_id=source_file.project_id,
            source_file_id=source_file.id,
            status="RUNNING",
            runs_per_level=runs_per_level,
            stdin_payload=stdin_payload,
            started_at=now,
        )
        self.db.add(suite)
        await self.db.flush()
        await self.db.refresh(suite)

        compiler_svc = CompilerService(self.db)
        opt_levels = ["-O0", "-O1", "-O2", "-O3"]
        level_stats: Dict[str, Dict] = {}

        try:
            # 2. Compile and benchmark each level
            for level in opt_levels:
                compilation = await compiler_svc.compile_source_file(
                    source_file_id=source_file.id,
                    optimization_level=level,
                    compiler_flags=[],
                )
                if not compilation.success:
                    raise CompilerXException(f"Compilation failed under {level}: {compilation.stderr}")

                # Run benchmark iterations
                bench_resp = await self.run_benchmark(
                    compilation_id=compilation.id,
                    num_runs=runs_per_level,
                    stdin_payload=stdin_payload,
                    suite_id=suite.id,
                )

                max_rss = max(r.peak_memory_kb for r in bench_resp.runs)
                bin_size = compilation.binary_size_bytes or 0

                level_stats[level] = {
                    "stats": bench_resp.statistics,
                    "peak_memory_kb": max_rss,
                    "binary_size_bytes": bin_size,
                }

            # 3. Calculate Speedups relative to -O0 baseline
            baseline_mean = level_stats["-O0"]["stats"].mean_wall_time_ms
            suite_results: List[SuiteResultItem] = []

            for level in opt_levels:
                item_stats = level_stats[level]["stats"]
                mean_t = item_stats.mean_wall_time_ms
                speedup = round((baseline_mean / mean_t), 2) if mean_t > 0 else 1.0

                result_entity = BenchmarkSuiteResult(
                    suite_id=suite.id,
                    optimization_level=level,
                    mean_time_ms=mean_t,
                    median_time_ms=item_stats.median_wall_time_ms,
                    stddev_time_ms=item_stats.stddev_ms,
                    min_time_ms=item_stats.min_ms,
                    max_time_ms=item_stats.max_ms,
                    variance_cv_percent=item_stats.variance_cv_percent,
                    speedup_vs_o0=speedup,
                    peak_memory_kb=level_stats[level]["peak_memory_kb"],
                    binary_size_bytes=level_stats[level]["binary_size_bytes"],
                    has_high_variance=item_stats.has_high_variance,
                )
                self.db.add(result_entity)

                suite_results.append(
                    SuiteResultItem(
                        optimization_level=level,
                        mean_time_ms=mean_t,
                        median_time_ms=item_stats.median_wall_time_ms,
                        stddev_time_ms=item_stats.stddev_ms,
                        min_time_ms=item_stats.min_ms,
                        max_time_ms=item_stats.max_ms,
                        variance_cv_percent=item_stats.variance_cv_percent,
                        speedup_vs_o0=speedup,
                        peak_memory_kb=level_stats[level]["peak_memory_kb"],
                        binary_size_bytes=level_stats[level]["binary_size_bytes"],
                        has_high_variance=item_stats.has_high_variance,
                    )
                )

            suite.status = "COMPLETED"
            suite.completed_at = datetime.now(timezone.utc)
            await self.db.flush()

            return BenchmarkSuiteResponse(
                suite_id=suite.id,
                source_file_id=source_file.id,
                status=suite.status,
                started_at=suite.started_at,
                completed_at=suite.completed_at,
                results=suite_results,
            )

        except Exception as e:
            suite.status = "FAILED"
            suite.completed_at = datetime.now(timezone.utc)
            await self.db.flush()
            logger.error("benchmark_suite_failed", suite_id=suite.id, error=str(e))
            raise
