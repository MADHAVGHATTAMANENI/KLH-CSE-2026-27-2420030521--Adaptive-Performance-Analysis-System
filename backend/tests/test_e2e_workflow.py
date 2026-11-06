import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_platform_e2e_workflow(client: AsyncClient):
    """
    End-to-End Full System Integration Test
    Validates the entire user flow:
    Project -> File -> Compile -> Features -> ML Recommendation -> Benchmark Suite -> Analytics -> Reports
    """
    # 1. Create a project
    create_proj_resp = await client.post(
        "/api/v1/projects",
        json={
            "name": "E2E Dense Matrix Project",
            "description": "End-to-end integration test workspace",
            "language": "c",
        },
    )
    assert create_proj_resp.status_code == 201
    proj_data = create_proj_resp.json()
    project_id = proj_data["id"]
    assert proj_data["name"] == "E2E Dense Matrix Project"

    # 2. Upload/Create a C source file (Matrix multiplication)
    matrix_c_code = """
#include <stdio.h>
#define N 60

int A[N][N];
int B[N][N];
int C[N][N];

int main() {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            A[i][j] = (i + j) % 10;
            B[i][j] = (i * j) % 10;
            C[i][j] = 0;
        }
    }

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    printf("Checksum: %d\\n", C[N-1][N-1]);
    return 0;
}
"""
    create_file_resp = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "matrix_dense.c", "content": matrix_c_code},
    )
    assert create_file_resp.status_code == 201
    file_data = create_file_resp.json()
    file_id = file_data["id"]

    # 3. Compile the file at -O0 and -O3
    compile_o0_resp = await client.post(
        f"/api/v1/files/{file_id}/compile",
        json={"optimization_level": "-O0", "compiler_flags": ["-Wall"]},
    )
    assert compile_o0_resp.status_code == 201
    comp_o0 = compile_o0_resp.json()
    assert comp_o0["success"] is True
    assert comp_o0["binary_size_bytes"] > 0
    assert comp_o0["exit_code"] == 0

    compile_o3_resp = await client.post(
        f"/api/v1/files/{file_id}/compile",
        json={"optimization_level": "-O3", "compiler_flags": []},
    )
    assert compile_o3_resp.status_code == 201
    comp_o3 = compile_o3_resp.json()
    assert comp_o3["success"] is True

    # 4. Extract 16-Dimensional Static AST Features
    feat_resp = await client.get(f"/api/v1/optimization/features/{file_id}")
    assert feat_resp.status_code == 200
    feats = feat_resp.json()
    assert feats["loop_count"] >= 3
    assert feats["max_loop_nesting_depth"] == 3
    assert feats["lines_of_code"] > 10

    # 5. Query Adaptive AI Recommendation (Random Forest)
    rec_resp = await client.post(
        f"/api/v1/files/{file_id}/recommend",
        json={"objective": "SPEED"},
    )
    assert rec_resp.status_code == 200
    rec = rec_resp.json()
    assert rec["recommended_level"] in ["-O2", "-O3"]
    assert 0.0 <= rec["confidence_score"] <= 1.0
    assert len(rec["explanation"]) > 10
    assert len(rec["top_influencing_features"]) > 0

    # 6. Execute Controlled Benchmark Suite (3 runs per level)
    suite_resp = await client.post(
        f"/api/v1/files/{file_id}/benchmark-suite",
        json={"runs_per_level": 3},
    )
    assert suite_resp.status_code == 201
    suite_data = suite_resp.json()
    suite_id = suite_data["suite_id"]
    assert suite_data["status"] == "COMPLETED"
    assert len(suite_data["results"]) == 4  # -O0, -O1, -O2, -O3

    # Verify speedup calculations relative to -O0
    o0_res = next(r for r in suite_data["results"] if r["optimization_level"] == "-O0")
    assert o0_res["speedup_vs_o0"] == 1.0

    # 7. Query Comparative Analytics
    analytics_resp = await client.get(f"/api/v1/benchmarks/suite/{suite_id}/analytics")
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()
    assert analytics["suite_id"] == suite_id
    assert "optimal_for_speed" in analytics
    assert "optimal_for_size" in analytics
    assert analytics["overall_efficiency_score"] > 0
    assert len(analytics["pareto_frontier"]) == 4

    # 8. Query Longitudinal File Analytics
    file_analytics_resp = await client.get(f"/api/v1/files/{file_id}/analytics")
    assert file_analytics_resp.status_code == 200
    file_analytics = file_analytics_resp.json()
    assert file_analytics["total_suites_run"] >= 1
    assert file_analytics["latest_suite_id"] == suite_id

    # 9. Export Audit Reports (Markdown & JSON)
    md_resp = await client.get(f"/api/v1/benchmarks/suite/{suite_id}/report?format=markdown")
    assert md_resp.status_code == 200
    assert "# CompilerX — Performance Audit & Optimization Report" in md_resp.text
    assert "System & Execution Environment" in md_resp.text
    assert "Pareto Optimization Analysis" in md_resp.text

    json_resp = await client.get(f"/api/v1/benchmarks/suite/{suite_id}/report?format=json")
    assert json_resp.status_code == 200
    json_report = json_resp.json()
    assert json_report["suite_id"] == suite_id
    assert "environment" in json_report
    assert len(json_report["results"]) == 4


@pytest.mark.asyncio
async def test_security_adversarial_flag_injection(client: AsyncClient):
    """
    SecOps Test: Verifies rejection of illegal compiler flags or shell injection.
    """
    # 1. Create a project and file
    proj_resp = await client.post("/api/v1/projects", json={"name": "SecOps Test", "language": "c"})
    project_id = proj_resp.json()["id"]

    file_resp = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "safe.c", "content": "int main() { return 0; }"},
    )
    file_id = file_resp.json()["id"]

    # 2. Attempt shell injection in flag
    injection_resp = await client.post(
        f"/api/v1/files/{file_id}/compile",
        json={"optimization_level": "-O2", "compiler_flags": ["-Wall; rm -rf /"]},
    )
    assert injection_resp.status_code == 422
    err_data = injection_resp.json()
    assert err_data["error"] == "SECURITY_VIOLATION"


@pytest.mark.asyncio
async def test_compilation_syntax_error_resilience(client: AsyncClient):
    """
    Verifies graceful error capture and reporting for invalid C syntax.
    """
    proj_resp = await client.post("/api/v1/projects", json={"name": "Syntax Error Test", "language": "c"})
    project_id = proj_resp.json()["id"]

    file_resp = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "broken.c", "content": "int main() { syntax error here }"},
    )
    file_id = file_resp.json()["id"]

    comp_resp = await client.post(
        f"/api/v1/files/{file_id}/compile",
        json={"optimization_level": "-O0", "compiler_flags": []},
    )
    assert comp_resp.status_code == 201
    comp_data = comp_resp.json()
    assert comp_data["success"] is False
    assert comp_data["exit_code"] != 0
    assert "error:" in comp_data["stderr"]


@pytest.mark.asyncio
async def test_benchmark_non_zero_exit_code_capture(client: AsyncClient):
    """
    Verifies that the runner accurately captures non-zero program exits without crashing.
    """
    proj_resp = await client.post("/api/v1/projects", json={"name": "Exit Code Test", "language": "c"})
    project_id = proj_resp.json()["id"]

    file_resp = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "exit_val.c", "content": "int main() { return 42; }"},
    )
    file_id = file_resp.json()["id"]

    comp_resp = await client.post(
        f"/api/v1/files/{file_id}/compile",
        json={"optimization_level": "-O0"},
    )
    assert comp_resp.status_code == 201
    comp_id = comp_resp.json()["id"]

    bench_resp = await client.post(
        f"/api/v1/compilations/{comp_id}/benchmark",
        json={"num_runs": 2},
    )
    assert bench_resp.status_code == 200
    bench_data = bench_resp.json()
    for run in bench_data["runs"]:
        assert run["exit_code"] == 42
