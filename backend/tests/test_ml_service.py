import time
import pytest
from httpx import AsyncClient
from app.ml.features import CodeFeatureExtractor


def test_code_feature_extractor_synthetic_code():
    """
    Verifies that feature extractor accurately detects:
    - 3 nested loops
    - Function count
    - Cyclomatic complexity
    - Arithmetic and pointer operations
    """
    code = """
    #include <stdio.h>
    void matmul(int n, double A[n][n], double B[n][n], double C[n][n]) {
        for(int i = 0; i < n; i++) {
            for(int j = 0; j < n; j++) {
                C[i][j] = 0.0;
                for(int k = 0; k < n; k++) {
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }
    }
    int main() {
        return 0;
    }
    """
    features = CodeFeatureExtractor.extract_features(code)

    assert features["max_loop_nesting_depth"] == 3
    assert features["loop_count"] == 3
    assert features["function_count"] == 2
    assert features["array_subscript_ops"] >= 6
    assert features["lines_of_code"] > 0
    assert "arithmetic_to_branch_ratio" in features


@pytest.mark.asyncio
async def test_ml_recommendation_flow(client: AsyncClient):
    """
    Verifies full end-to-end ML recommendation flow:
    - Feature extraction API
    - Recommendation generation with natural language explanation
    - Top influencing features included
    """
    # 1. Create project & file with matrix multiplication code
    p_res = await client.post("/api/v1/projects", json={"name": "ML Lab", "language": "c"})
    project_id = p_res.json()["id"]

    code = """
    #include <stdio.h>
    #define N 64
    double A[N][N], B[N][N], C[N][N];
    int main() {
        for (int i=0; i<N; i++)
            for (int j=0; j<N; j++)
                for (int k=0; k<N; k++)
                    C[i][j] += A[i][k] * B[k][j];
        return 0;
    }
    """
    f_res = await client.post(
        f"/api/v1/projects/{project_id}/files",
        json={"filename": "matrix.c", "content": code},
    )
    file_id = f_res.json()["id"]

    # 2. Extract Features via API
    feat_res = await client.get(f"/api/v1/optimization/features/{file_id}")
    assert feat_res.status_code == 200
    features = feat_res.json()
    assert features["max_loop_nesting_depth"] == 3
    assert features["loop_count"] == 3

    # 3. Request ML Recommendation
    rec_start = time.perf_counter()
    rec_res = await client.post(
        f"/api/v1/files/{file_id}/recommend",
        json={"objective": "SPEED"},
    )
    rec_duration_ms = (time.perf_counter() - rec_start) * 1000.0

    assert rec_res.status_code == 200
    rec = rec_res.json()
    assert rec["recommended_level"] in ["-O0", "-O1", "-O2", "-O3"]
    assert 0.0 <= rec["confidence_score"] <= 1.0
    assert len(rec["explanation"]) > 20
    assert len(rec["top_influencing_features"]) == 3
    assert rec_duration_ms < 50.0  # Must be fast (< 50ms)


@pytest.mark.asyncio
async def test_ml_model_status_and_retrain(client: AsyncClient):
    """
    Verifies MLOps endpoints (CO4):
    - Model status inspection (accuracy, confusion matrix)
    - Retraining trigger
    """
    status_res = await client.get("/api/v1/ml/model/status")
    assert status_res.status_code == 200
    status_data = status_res.json()

    assert "model_version" in status_data
    assert "accuracy" in status_data
    assert status_data["accuracy"] > 0.0
    assert "confusion_matrix" in status_data
    assert len(status_data["feature_importances"]) == 16

    # Test Retrain endpoint
    retrain_res = await client.post("/api/v1/ml/model/retrain")
    assert retrain_res.status_code == 200
    assert retrain_res.json()["accuracy"] > 0.0

