from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.benchmark import BenchmarkSuite, BenchmarkSuiteResult
from app.models.source_file import SourceFile
from app.schemas.analytics import (
    ParetoPoint,
    RegressionAlert,
    SuiteAnalyticsResponse,
    FileAnalyticsOverview,
)
from app.core.exceptions import EntityNotFoundError


class AnalyticsService:
    @staticmethod
    def compute_pareto_frontier(
        results: List[BenchmarkSuiteResult],
    ) -> List[ParetoPoint]:
        """
        Calculates Pareto-optimal configurations balancing execution runtime
        (minimization) vs binary size (minimization).
        A configuration is Pareto-optimal if no other configuration achieves
        both lower or equal runtime and smaller or equal binary size.
        """
        points: List[ParetoPoint] = []
        if not results:
            return points

        raw_data = [
            {
                "level": r.optimization_level,
                "runtime": r.mean_time_ms,
                "size": r.binary_size_bytes,
                "speedup": r.speedup_vs_o0,
            }
            for r in results
        ]

        for p in raw_data:
            # Check if p is dominated by any other point q
            dominated = False
            for q in raw_data:
                if q["level"] == p["level"]:
                    continue
                # q dominates p if q has <= runtime and <= size, and at least one strictly better
                if (q["runtime"] <= p["runtime"] and q["size"] <= p["size"]) and (
                    q["runtime"] < p["runtime"] or q["size"] < p["size"]
                ):
                    dominated = True
                    break

            points.append(
                ParetoPoint(
                    optimization_level=p["level"],
                    speedup=round(p["speedup"], 2),
                    binary_size_bytes=p["size"],
                    runtime_ms=round(p["runtime"], 3),
                    is_pareto_optimal=not dominated,
                )
            )

        return points

    @staticmethod
    def detect_regressions(
        results: List[BenchmarkSuiteResult],
    ) -> List[RegressionAlert]:
        """
        Detects optimization performance regressions across flags.
        Example: -O3 executing slower than -O2, or -O2 executing slower than -O1.
        """
        alerts: List[RegressionAlert] = []
        result_map = {r.optimization_level: r for r in results}

        # Check O3 vs O2 regression
        if "-O3" in result_map and "-O2" in result_map:
            o3_time = result_map["-O3"].mean_time_ms
            o2_time = result_map["-O2"].mean_time_ms
            if o3_time > o2_time * 1.02:  # >2% slowdown
                factor = round(o3_time / max(o2_time, 0.0001), 2)
                alerts.append(
                    RegressionAlert(
                        level="-O3",
                        comparison_level="-O2",
                        slowdown_factor=factor,
                        reason=f"-O3 runtime ({o3_time:.3f}ms) is {factor}x slower than -O2 ({o2_time:.3f}ms). "
                        "Likely caused by loop unrolling or aggressive inlining exceeding L1 instruction cache.",
                    )
                )

        # Check O2 vs O1 regression
        if "-O2" in result_map and "-O1" in result_map:
            o2_time = result_map["-O2"].mean_time_ms
            o1_time = result_map["-O1"].mean_time_ms
            if o2_time > o1_time * 1.05:
                factor = round(o2_time / max(o1_time, 0.0001), 2)
                alerts.append(
                    RegressionAlert(
                        level="-O2",
                        comparison_level="-O1",
                        slowdown_factor=factor,
                        reason=f"-O2 runtime ({o2_time:.3f}ms) is {factor}x slower than -O1 ({o1_time:.3f}ms).",
                    )
                )

        return alerts

    @classmethod
    def analyze_suite_results(
        cls,
        suite_id: str,
        source_file_id: str,
        results: List[BenchmarkSuiteResult],
    ) -> SuiteAnalyticsResponse:
        """
        Produces deep comparative analytics for a suite run.
        """
        if not results:
            raise ValueError("Cannot analyze empty suite results.")

        # Baseline -O0
        o0_res = next((r for r in results if r.optimization_level == "-O0"), results[0])
        baseline_time = max(o0_res.mean_time_ms, 0.0001)
        baseline_size = max(o0_res.binary_size_bytes, 1)

        # Optimal for speed
        fastest = min(results, key=lambda r: r.mean_time_ms)
        # Optimal for size
        smallest = min(results, key=lambda r: r.binary_size_bytes)

        max_speedup = round(baseline_time / max(fastest.mean_time_ms, 0.0001), 2)
        max_size_reduction = round(
            max(0.0, (baseline_size - smallest.binary_size_bytes) / baseline_size * 100), 2
        )

        regressions = cls.detect_regressions(results)
        pareto_points = cls.compute_pareto_frontier(results)

        # Efficiency composite score (0 - 100):
        # Combines speedup contribution (up to 70 pts) + size reduction (up to 30 pts)
        speed_score = min(70.0, (max_speedup - 1.0) * 35.0) if max_speedup > 1.0 else 0.0
        size_score = min(30.0, max_size_reduction * 0.5)
        overall_score = round(max(10.0, 50.0 + speed_score + size_score), 1)

        return SuiteAnalyticsResponse(
            suite_id=suite_id,
            source_file_id=source_file_id,
            optimal_for_speed=fastest.optimization_level,
            optimal_for_size=smallest.optimization_level,
            max_speedup=max_speedup,
            max_size_reduction_pct=max_size_reduction,
            has_regression=len(regressions) > 0,
            regressions=regressions,
            pareto_frontier=pareto_points,
            overall_efficiency_score=overall_score,
        )

    @classmethod
    async def get_file_analytics(
        cls,
        session: AsyncSession,
        source_file_id: str,
    ) -> FileAnalyticsOverview:
        """
        Returns longitudinal analytics across all benchmark suites for a file.
        """
        file_obj = await session.get(SourceFile, source_file_id)
        if not file_obj:
            raise EntityNotFoundError("Source file", source_file_id)

        suites_query = (
            select(BenchmarkSuite)
            .where(
                BenchmarkSuite.source_file_id == source_file_id,
                BenchmarkSuite.status == "COMPLETED",
            )
            .order_by(BenchmarkSuite.created_at.desc())
        )
        suites_result = await session.execute(suites_query)
        suites = suites_result.scalars().all()

        if not suites:
            return FileAnalyticsOverview(
                source_file_id=source_file_id,
                filename=file_obj.filename,
                total_suites_run=0,
                latest_suite_id=None,
                best_speedup_observed=1.0,
                best_level=None,
                recent_regression_detected=False,
            )

        latest_suite = suites[0]
        all_results_query = select(BenchmarkSuiteResult).where(
            BenchmarkSuiteResult.suite_id == latest_suite.id
        )
        res = await session.execute(all_results_query)
        latest_results = res.scalars().all()

        best_speedup = 1.0
        best_level = None
        has_regression = False

        if latest_results:
            analytics = cls.analyze_suite_results(
                latest_suite.id, source_file_id, list(latest_results)
            )
            best_speedup = analytics.max_speedup
            best_level = analytics.optimal_for_speed
            has_regression = analytics.has_regression

        return FileAnalyticsOverview(
            source_file_id=source_file_id,
            filename=file_obj.filename,
            total_suites_run=len(suites),
            latest_suite_id=latest_suite.id,
            best_speedup_observed=best_speedup,
            best_level=best_level,
            recent_regression_detected=has_regression,
        )
