import math
import pytest
from httpx import AsyncClient
from app.services.benchmark_service import BenchmarkService


def test_benchmark_statistics_math():
    """
    Verifies that compute_statistics computes exact sample statistics:
    Mean, Median, Sample StdDev, and CV%.
    """
    sample_runs = [
        {"wall_time_ms": 10.0},
        {"wall_time_ms": 12.0},
        {"wall_time_ms": 14.0},
        {"wall_time_ms": 16.0},
        {"wall_time_ms": 18.0},
    ]
    stats = BenchmarkService.compute_statistics(sample_runs)

    assert stats.mean_wall_time_ms == 14.0
    assert stats.median_wall_time_ms == 14.0
    assert math.isclose(stats.stddev_ms, 3.1623, rel_tol=1e-3)
    assert stats.min_ms == 10.0
    assert stats.max_ms == 18.0
    assert stats.has_high_variance is True  # CV = (3.1623 / 14) * 100 ≈ 22.58% > 15%


@pytest.mark.asyncio
async def test_single_compilation_benchmark_flow(client: AsyncClient):
    """
    Verifies that a compiled binary can be benchmarked for N iterations:
    - Returns N run records with wall time, user time, sys time, memory
    - Calculates aggregated statistics
    """
    p_res = await client.post("/api/v1/projects", json={"name": "Bench Lab", "language": "c"})
    project_id = p_res.json()["id"]

    code = """
    #include <stdio.h>
    int main() {
        volatile long acc = 0;
        for (long i = 0; i < 500000; i++) acc += i;
        printf("Result: %ld\\n", acc);
        return 0;
    }
    """
    f_res = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "bench.c", "content": code},
    )
    file_id = f_res.json()["id"]

    # Compile
    c_res = await client.post(
        f"/api/v1/files/{file_id}/compile",
        json={"optimization_level": "-O2"},
    )
    assert c_res.status_code == 201
    compilation_id = c_res.json()["id"]

    # Benchmark 3 iterations
    b_res = await client.post(
        f"/api/v1/compilations/{compilation_id}/benchmark",
        json={"num_runs": 3},
    )
    assert b_res.status_code == 200
    bench_data = b_res.json()
    assert len(bench_data["runs"]) == 3
    assert bench_data["statistics"]["mean_wall_time_ms"] > 0
    assert bench_data["runs"][0]["peak_memory_kb"] > 0


@pytest.mark.asyncio
async def test_full_multi_level_benchmark_suite(client: AsyncClient):
    """
    Verifies that POST /files/{id}/benchmark-suite executes across -O0, -O1, -O2, -O3:
    - Calculates speedups relative to -O0
    - Records binary size per level
    - Returns completed suite with 4 result items
    """
    p_res = await client.post("/api/v1/projects", json={"name": "Suite Lab", "language": "c"})
    project_id = p_res.json()["id"]

    code = """
    #include <stdio.h>
    int main() {
        volatile int count = 0;
        for (int i = 0; i < 200000; i++) count += i;
        return 0;
    }
    """
    f_res = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "suite_test.c", "content": code},
    )
    file_id = f_res.json()["id"]

    # Run full suite (3 runs per level for test speed)
    s_res = await client.post(
        f"/api/v1/files/{file_id}/benchmark-suite",
        json={"runs_per_level": 3},
    )
    assert s_res.status_code == 201
    suite_data = s_res.json()
    assert suite_data["status"] == "COMPLETED"
    assert len(suite_data["results"]) == 4

    levels = [r["optimization_level"] for r in suite_data["results"]]
    assert levels == ["-O0", "-O1", "-O2", "-O3"]

    # -O0 speedup must be 1.0
    o0_result = next(r for r in suite_data["results"] if r["optimization_level"] == "-O0")
    assert o0_result["speedup_vs_o0"] == 1.0

    # Poll status by suite_id
    suite_id = suite_data["suite_id"]
    poll_res = await client.get(f"/api/v1/benchmarks/suite/{suite_id}")
    assert poll_res.status_code == 200
    assert poll_res.json()["status"] == "COMPLETED"
