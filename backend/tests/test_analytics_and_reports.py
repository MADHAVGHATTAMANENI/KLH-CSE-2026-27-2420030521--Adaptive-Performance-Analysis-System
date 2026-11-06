import pytest
from httpx import AsyncClient
from app.models.benchmark import BenchmarkSuiteResult
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService


def test_pareto_frontier_computation():
    # Construct mock suite results
    # -O0: 100ms, 50000 bytes (baseline)
    # -O1: 70ms, 45000 bytes (faster, smaller -> dominates -O0)
    # -O2: 40ms, 48000 bytes (faster than O1, slightly larger -> pareto optimal)
    # -O3: 50ms, 52000 bytes (slower and larger than O2 -> dominated!)
    results = [
        BenchmarkSuiteResult(
            optimization_level="-O0",
            mean_time_ms=100.0,
            median_time_ms=100.0,
            stddev_time_ms=1.0,
            min_time_ms=99.0,
            max_time_ms=101.0,
            variance_cv_percent=1.0,
            speedup_vs_o0=1.0,
            peak_memory_kb=1000,
            binary_size_bytes=50000,
            has_high_variance=False,
        ),
        BenchmarkSuiteResult(
            optimization_level="-O1",
            mean_time_ms=70.0,
            median_time_ms=70.0,
            stddev_time_ms=0.5,
            min_time_ms=69.0,
            max_time_ms=71.0,
            variance_cv_percent=0.7,
            speedup_vs_o0=1.43,
            peak_memory_kb=1000,
            binary_size_bytes=45000,
            has_high_variance=False,
        ),
        BenchmarkSuiteResult(
            optimization_level="-O2",
            mean_time_ms=40.0,
            median_time_ms=40.0,
            stddev_time_ms=0.5,
            min_time_ms=39.0,
            max_time_ms=41.0,
            variance_cv_percent=1.2,
            speedup_vs_o0=2.5,
            peak_memory_kb=1000,
            binary_size_bytes=48000,
            has_high_variance=False,
        ),
        BenchmarkSuiteResult(
            optimization_level="-O3",
            mean_time_ms=50.0,
            median_time_ms=50.0,
            stddev_time_ms=0.5,
            min_time_ms=49.0,
            max_time_ms=51.0,
            variance_cv_percent=1.0,
            speedup_vs_o0=2.0,
            peak_memory_kb=1000,
            binary_size_bytes=52000,
            has_high_variance=False,
        ),
    ]

    pareto_points = AnalyticsService.compute_pareto_frontier(results)
    assert len(pareto_points) == 4

    pareto_map = {p.optimization_level: p.is_pareto_optimal for p in pareto_points}
    # -O1 (smallest size: 45000) is Pareto optimal
    assert pareto_map["-O1"] is True
    # -O2 (fastest time: 40ms) is Pareto optimal
    assert pareto_map["-O2"] is True
    # -O0 (100ms, 50000 bytes) is strictly dominated by -O1 (70ms, 45000 bytes)
    assert pareto_map["-O0"] is False
    # -O3 (50ms, 52000 bytes) is strictly dominated by -O2 (40ms, 48000 bytes)
    assert pareto_map["-O3"] is False


def test_regression_detection():
    results = [
        BenchmarkSuiteResult(
            optimization_level="-O0",
            mean_time_ms=100.0,
            median_time_ms=100.0,
            stddev_time_ms=1.0,
            min_time_ms=99.0,
            max_time_ms=101.0,
            variance_cv_percent=1.0,
            speedup_vs_o0=1.0,
            peak_memory_kb=1000,
            binary_size_bytes=50000,
            has_high_variance=False,
        ),
        BenchmarkSuiteResult(
            optimization_level="-O2",
            mean_time_ms=30.0,
            median_time_ms=30.0,
            stddev_time_ms=0.5,
            min_time_ms=29.0,
            max_time_ms=31.0,
            variance_cv_percent=1.0,
            speedup_vs_o0=3.33,
            peak_memory_kb=1000,
            binary_size_bytes=48000,
            has_high_variance=False,
        ),
        BenchmarkSuiteResult(
            optimization_level="-O3",
            mean_time_ms=45.0,  # Slower than O2!
            median_time_ms=45.0,
            stddev_time_ms=0.5,
            min_time_ms=44.0,
            max_time_ms=46.0,
            variance_cv_percent=1.0,
            speedup_vs_o0=2.22,
            peak_memory_kb=1000,
            binary_size_bytes=55000,
            has_high_variance=False,
        ),
    ]

    alerts = AnalyticsService.detect_regressions(results)
    assert len(alerts) == 1
    assert alerts[0].level == "-O3"
    assert alerts[0].comparison_level == "-O2"
    assert alerts[0].slowdown_factor == 1.5


def test_system_environment_collection():
    env = ReportService.get_system_environment()
    assert "platform" in env
    assert "architecture" in env
    assert "cpu_cores" in env
    assert env["cpu_cores"] >= 1
    assert "compiler_version" in env


@pytest.mark.asyncio
async def test_analytics_and_report_api_endpoints(client: AsyncClient):
    # 1. Create a project
    proj_resp = await client.post(
        "/api/v1/projects",
        json={"name": "Analytics Test Project", "language": "c"},
    )
    assert proj_resp.status_code == 201
    project_id = proj_resp.json()["id"]

    # 2. Create a source file
    code = """#include <stdio.h>
int main() {
    long long sum = 0;
    for (int i = 0; i < 50000; i++) {
        sum += (i * 3) ^ (i & 7);
    }
    printf("%lld\\n", sum);
    return 0;
}
"""
    file_resp = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "compute.c", "content": code},
    )
    assert file_resp.status_code == 201
    file_id = file_resp.json()["id"]

    # 3. Run a benchmark suite (3 runs per level)
    suite_resp = await client.post(
        f"/api/v1/files/{file_id}/benchmark-suite",
        json={"runs_per_level": 3},
    )
    assert suite_resp.status_code == 201
    suite_data = suite_resp.json()
    suite_id = suite_data["suite_id"]

    # 4. Request suite analytics
    suite_analytics_resp = await client.get(
        f"/api/v1/benchmarks/suite/{suite_id}/analytics"
    )
    assert suite_analytics_resp.status_code == 200
    analytics_json = suite_analytics_resp.json()
    assert analytics_json["suite_id"] == suite_id
    assert "optimal_for_speed" in analytics_json
    assert "max_speedup" in analytics_json
    assert len(analytics_json["pareto_frontier"]) > 0

    # 5. Request longitudinal file analytics
    file_analytics_resp = await client.get(
        f"/api/v1/files/{file_id}/analytics"
    )
    assert file_analytics_resp.status_code == 200
    file_analytics_json = file_analytics_resp.json()
    assert file_analytics_json["source_file_id"] == file_id
    assert file_analytics_json["total_suites_run"] >= 1
    assert file_analytics_json["latest_suite_id"] == suite_id

    # 6. Export report as Markdown
    md_report_resp = await client.get(
        f"/api/v1/benchmarks/suite/{suite_id}/report?format=markdown"
    )
    assert md_report_resp.status_code == 200
    assert "text/markdown" in md_report_resp.headers["content-type"]
    assert "# CompilerX — Performance Audit & Optimization Report" in md_report_resp.text
    assert "Benchmark Measurement Matrix" in md_report_resp.text

    # 7. Export report as JSON
    json_report_resp = await client.get(
        f"/api/v1/benchmarks/suite/{suite_id}/report?format=json"
    )
    assert json_report_resp.status_code == 200
    report_json = json_report_resp.json()
    assert report_json["suite_id"] == suite_id
    assert "environment" in report_json
    assert "results" in report_json
    assert len(report_json["results"]) > 0
