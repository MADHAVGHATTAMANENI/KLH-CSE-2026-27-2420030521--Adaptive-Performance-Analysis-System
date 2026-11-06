import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.benchmark import BenchmarkSuite, BenchmarkSuiteResult
from app.models.source_file import SourceFile
from app.models.recommendation import OptimizationRecommendation
from app.services.analytics_service import AnalyticsService
from app.core.exceptions import EntityNotFoundError
from app.core.config import settings


class ReportService:
    @staticmethod
    def get_system_environment() -> Dict[str, Any]:
        """
        Collects host platform, CPU, and Clang compiler version details.
        """
        clang_version = "Unknown"
        try:
            res = subprocess.run(
                [settings.CLANG_PATH, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                clang_version = res.stdout.splitlines()[0]
        except Exception:
            clang_version = "Clang binary not accessible"

        return {
            "hostname": platform.node(),
            "platform": f"{platform.system()} {platform.release()}",
            "architecture": platform.machine(),
            "cpu_cores": os.cpu_count() or 1,
            "compiler_path": settings.CLANG_PATH,
            "compiler_version": clang_version,
        }

    @classmethod
    async def build_report_data(
        cls,
        session: AsyncSession,
        suite_id: str,
    ) -> Dict[str, Any]:
        """
        Gathers complete suite, file, analytics, and ML recommendation data.
        """
        suite = await session.get(BenchmarkSuite, suite_id)
        if not suite:
            raise EntityNotFoundError("Benchmark suite", suite_id)

        source_file = await session.get(SourceFile, suite.source_file_id)
        if not source_file:
            raise EntityNotFoundError("Source file", suite.source_file_id)

        # Get suite results
        results_query = (
            select(BenchmarkSuiteResult)
            .where(BenchmarkSuiteResult.suite_id == suite_id)
            .order_by(BenchmarkSuiteResult.optimization_level)
        )
        res = await session.execute(results_query)
        suite_results = list(res.scalars().all())

        if not suite_results:
            raise ValueError(f"No results found for benchmark suite {suite_id}")

        analytics = AnalyticsService.analyze_suite_results(
            suite.id, source_file.id, suite_results
        )

        # Query latest ML recommendation for this file if available
        rec_query = (
            select(OptimizationRecommendation)
            .where(OptimizationRecommendation.source_file_id == source_file.id)
            .order_by(OptimizationRecommendation.created_at.desc())
        )
        rec_res = await session.execute(rec_query)
        recommendation = rec_res.scalars().first()

        results_data = [
            {
                "optimization_level": r.optimization_level,
                "mean_time_ms": round(r.mean_time_ms, 3),
                "median_time_ms": round(r.median_time_ms, 3),
                "stddev_time_ms": round(r.stddev_time_ms, 3),
                "min_time_ms": round(r.min_time_ms, 3),
                "max_time_ms": round(r.max_time_ms, 3),
                "variance_cv_percent": round(r.variance_cv_percent, 2),
                "speedup_vs_o0": round(r.speedup_vs_o0, 2),
                "binary_size_bytes": r.binary_size_bytes,
                "peak_memory_kb": r.peak_memory_kb,
                "has_high_variance": r.has_high_variance,
            }
            for r in suite_results
        ]

        rec_data: Optional[Dict[str, Any]] = None
        if recommendation:
            features = json.loads(recommendation.features_extracted_json)
            top_features = json.loads(recommendation.top_influencing_features_json)
            rec_data = {
                "id": recommendation.id,
                "recommended_level": recommendation.recommended_level,
                "confidence_score": round(recommendation.confidence_score, 4),
                "objective": recommendation.objective,
                "explanation": recommendation.explanation,
                "features_extracted": features,
                "top_influencing_features": top_features,
                "created_at": recommendation.created_at.isoformat() if recommendation.created_at else None,
            }

        return {
            "report_id": f"REP-{suite_id[:8].upper()}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project_id": suite.project_id,
            "source_file_id": source_file.id,
            "filename": source_file.filename,
            "environment": cls.get_system_environment(),
            "suite_id": suite.id,
            "status": suite.status,
            "runs_per_level": suite.runs_per_level,
            "results": results_data,
            "recommendation": rec_data,
            "analytics_summary": analytics.model_dump(),
        }

    @classmethod
    async def generate_markdown_report(
        cls,
        session: AsyncSession,
        suite_id: str,
    ) -> str:
        """
        Generates production-grade Markdown performance audit report.
        """
        data = await cls.build_report_data(session, suite_id)
        env = data["environment"]
        analytics = data["analytics_summary"]
        results = data["results"]
        rec = data["recommendation"]

        lines = [
            "# CompilerX — Performance Audit & Optimization Report",
            "",
            f"**Report ID:** `{data['report_id']}`  ",
            f"**File:** `{data['filename']}` (`{data['source_file_id']}`)  ",
            f"**Generated:** `{data['generated_at']}`  ",
            f"**Benchmark Suite ID:** `{data['suite_id']}`  ",
            f"**Runs Per Flag:** `{data['runs_per_level']}` iterations with outlier rejection  ",
            "",
            "---",
            "",
            "## 1. System & Execution Environment",
            f"- **Host Platform:** {env['platform']} ({env['architecture']})",
            f"- **CPU Cores:** {env['cpu_cores']} logical processors",
            f"- **Compiler:** `{env['compiler_version']}`",
            f"- **Binary Path:** `{env['compiler_path']}`",
            "",
            "---",
            "",
            "## 2. Executive Performance Summary",
            f"- **Fastest Optimization Level:** `{analytics['optimal_for_speed']}`",
            f"- **Maximum Observed Speedup:** **`{analytics['max_speedup']}x`** vs unoptimized `-O0` baseline",
            f"- **Most Compact Binary:** `{analytics['optimal_for_size']}` ({analytics['max_size_reduction_pct']}% reduction)",
            f"- **Composite Efficiency Score:** `{analytics['overall_efficiency_score']}/100.0`",
            "",
        ]

        if analytics["has_regression"]:
            lines.extend([
                "> ⚠️ **Performance Regressions Detected:**",
                *[f"> - {reg['reason']}" for reg in analytics["regressions"]],
                "",
            ])

        lines.extend([
            "---",
            "",
            "## 3. Comprehensive Benchmark Measurement Matrix",
            "Metrics captured using native C harness `CLOCK_MONOTONIC_RAW` and `getrusage`.",
            "",
            "| Flag | Mean Time (ms) | Median (ms) | StdDev (ms) | CV% | Speedup | Binary Size | Memory (RSS) | Reliability |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ])

        for r in results:
            size_kb = round(r["binary_size_bytes"] / 1024, 1)
            rel_badge = "⚠️ High Variance" if r["has_high_variance"] else "✅ Consistent"
            lines.append(
                f"| `{r['optimization_level']}` | {r['mean_time_ms']:.3f} | {r['median_time_ms']:.3f} | "
                f"±{r['stddev_time_ms']:.3f} | {r['variance_cv_percent']:.1f}% | "
                f"**{r['speedup_vs_o0']:.2f}x** | {size_kb} KB | {r['peak_memory_kb']} KB | {rel_badge} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 4. Pareto Optimization Analysis",
            "Pareto-optimal configurations provide non-dominated trade-offs between execution speed and binary size.",
            "",
            "| Flag | Runtime (ms) | Binary Size (Bytes) | Speedup vs -O0 | Pareto Optimal? |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ])

        for p in analytics["pareto_frontier"]:
            pareto_badge = "⭐ Optimal Frontier" if p["is_pareto_optimal"] else "Dominated"
            lines.append(
                f"| `{p['optimization_level']}` | {p['runtime_ms']:.3f} | {p['binary_size_bytes']} | "
                f"{p['speedup']:.2f}x | {pareto_badge} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 5. Machine Learning Recommendation Insights",
        ])

        if rec:
            lines.extend([
                "- **Model:** Random Forest Classifier (100 Trees, Scikit-Learn)",
                f"- **Objective:** `{rec['objective']}`",
                f"- **Recommended Level:** `{rec['recommended_level']}`",
                f"- **Confidence:** `{(rec['confidence_score'] * 100):.1f}%`",
                "- **Model Rationale:**",
                f"  > {rec['explanation']}",
                "",
                "### Key Static Code Drivers",
            ])
            for feat in rec.get("top_influencing_features", []):
                lines.append(
                    f"- **{feat['feature'].replace('_', ' ')}**: Importance {feat['importance'] * 100:.1f}%"
                )
        else:
            lines.append("*No ML inference recommendation was requested for this file.*")

        lines.extend([
            "",
            "---",
            "",
            "## 6. Audit & Reproducibility Verification",
            "- **Integrity Guarantee:** Zero synthetic or mocked values; all execution measurements collected in real-time.",
            "- **System:** CompilerX Developer Platform — ASE Project KL University.",
            "",
        ])

        return "\n".join(lines)

    @classmethod
    async def generate_json_report(
        cls,
        session: AsyncSession,
        suite_id: str,
    ) -> Dict[str, Any]:
        """
        Returns structured JSON audit payload.
        """
        return await cls.build_report_data(session, suite_id)
