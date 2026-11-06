# CompilerX — Comprehensive Testing Strategy
**AI-Powered Adaptive Code Optimization and Performance Analysis System**

---

| Field | Value |
|---|---|
| **Document Version** | 1.0.0 |
| **Status** | APPROVED — Quality Assurance Standard |
| **Author** | Principal Software Architect & Technical Lead |
| **Target Course** | Adaptive Software Engineering (24CI3201), KL University |
| **Testing Harness** | `pytest` + `pytest-asyncio` (Backend); `vitest` + React Testing Library (Frontend) |
| **Target Coverage** | $\ge 75\%$ Service Layer & Critical Path Coverage |
| **Last Updated** | 2026-11-06 |

---

## 1. Testing Philosophy & Objectives

CompilerX is an engineering tool where execution correctness, numerical integrity, and security sandboxing are critical. The testing framework is designed around three foundational principles:

1. **Zero Empirical Fabrication:** Every test validating compiler metrics or benchmark statistics must either execute actual binaries through the test harness or feed mathematically known synthetic arrays to statistical verification functions.
2. **Defensive SecOps Validation (CO3):** Malicious user payloads (fork bombs, infinite loops, memory exhausters, shell injections) must be systematically executed against the sandbox in automated test suites to verify that isolation boundaries hold.
3. **Reproducible Fast Feedback (CO2):** The test suite is separated into fast in-memory unit tests (executing in $< 10\text{ seconds}$ during local development and PR checks) and comprehensive integration tests (executing with Docker in CI).

---

## 2. Test Pyramid & Scope

```
                ┌───────────────────┐
                │   Adversarial /   │
                │   Security Tests  │  (Fork bombs, OOM, Syscalls)
                └─────────┬─────────┘
                          │
              ┌───────────▼───────────┐
              │      End-to-End       │
              │   Integration Tests   │  (Full Lifecycle Workflows)
              └───────────┬───────────┘
                          │
            ┌─────────────▼─────────────┐
            │   Service & API Route     │
            │       Integration         │  (FastAPI + SQLite Async)
            └─────────────┬─────────────┘
                          │
          ┌───────────────▼───────────────┐
          │      Pure Unit Tests          │
          │ (Feature Extractor, Stats,    │  (Sub-millisecond execution)
          │  Flag Sanitizer, ML Pipeline) │
          └───────────────────────────────┘
```

| Layer | Tools | Execution Scope | Target Coverage |
|---|---|---|---|
| **Unit Tests** | `pytest`, `vitest` | Feature extractor, math formulas, Pydantic schemas, Zustand stores. | $> 85\%$ |
| **API & Service Tests**| `httpx.AsyncClient` | FastAPI routes, database transactions, compilation orchestrator. | $> 75\%$ |
| **Sandbox & Harness** | `pytest` + Docker SDK | Ephemeral container execution, C runner output verification. | $> 70\%$ |
| **Security / Adversarial**| `pytest` | Hostile C programs (infinite recursion, fork bombs, network). | $100\%$ of threat vectors |
| **End-to-End (E2E)** | `pytest` integration | Full workflow from code upload to report export. | Key user flows |

---

## 3. Unit Testing Specifications

### 3.1 Feature Extractor Validation (`test_features.py`)
Tests verify that `backend/app/ml/features.py` accurately quantifies C/C++ syntactic and structural properties:

```python
# Sample Unit Test Case
def test_feature_extractor_on_nested_loops():
    code = """
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
    """
    features = extract_features(code)
    assert features["max_loop_nesting_depth"] == 3
    assert features["loop_count"] == 3
    assert features["float_arithmetic_ops"] >= 2
    assert features["pointer_dereferences"] == 0
```

### 3.2 Statistical Aggregation Engine (`test_statistics.py`)
Validates that `BenchmarkService` computes mathematically exact metrics across $N$ iterations:

```python
def test_statistical_aggregation_exact_values():
    # Known dataset: [10.0, 12.0, 14.0, 16.0, 18.0]
    # Mean = 14.0, Median = 14.0, Sample Variance = 10.0, Sample StdDev = sqrt(10) ≈ 3.162277
    runtimes = [10.0, 12.0, 14.0, 16.0, 18.0]
    stats = compute_statistics(runtimes)
    
    assert math.isclose(stats["mean"], 14.0, rel_tol=1e-5)
    assert math.isclose(stats["median"], 14.0, rel_tol=1e-5)
    assert math.isclose(stats["stddev"], 3.162277, rel_tol=1e-5)
    assert stats["min"] == 10.0
    assert stats["max"] == 18.0
    assert math.isclose(stats["variance_cv_percent"], (3.162277 / 14.0) * 100.0, rel_tol=1e-3)
```

### 3.3 Compiler Flag Sanitizer (`test_security.py`)
Verifies strict whitelist enforcement:

```python
@pytest.mark.parametrize("flag", [
    "-Wall", "-Wextra", "-pedantic", "-std=c11", "-ffast-math", "-funroll-loops"
])
def test_allowed_flags_pass(flag):
    assert sanitize_flags("-O2", [flag]) == ["-O2", flag]

@pytest.mark.parametrize("malicious_flag", [
    "-Xclang", "-load", "-plugin", "; rm -rf /", "-I/etc", "--sysroot=/dev"
])
def test_disallowed_flags_raise_validation_error(malicious_flag):
    with pytest.raises(InvalidFlagError):
        sanitize_flags("-O2", [malicious_flag])
```

---

## 4. Integration & Service Layer Testing

### 4.1 Database & API Route Fixture (`conftest.py`)
Integration tests utilize an isolated in-memory SQLite database configured with async support (`sqlite+aiosqlite:///:memory:`):

```python
@pytest.fixture
async def async_client():
    # Create in-memory test engine & schema
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
```

### 4.2 End-to-End API Workflow Test (`test_e2e_workflow.py`)
Validates the complete user lifecycle from creation to report generation:

```python
@pytest.mark.asyncio
async def test_complete_platform_workflow(async_client):
    # 1. Create Project
    resp = await async_client.post("/api/v1/projects", json={"name": "Sort Demo", "language": "c"})
    assert resp.status_code == 201
    project_id = resp.json()["id"]

    # 2. Upload Source Code
    code = "#include <stdio.h>\nint main(){ printf(\"OK\\n\"); return 0; }"
    resp = await async_client.post(f"/api/v1/projects/{project_id}/files", json={"filename": "main.c", "content": code})
    assert resp.status_code == 201
    file_id = resp.json()["id"]

    # 3. Compile Program
    resp = await async_client.post(f"/api/v1/files/{file_id}/compile", json={"optimization_level": "-O2"})
    assert resp.status_code == 201
    assert resp.json()["success"] is True

    # 4. Request ML Recommendation
    resp = await async_client.post(f"/api/v1/files/{file_id}/recommend", json={"objective": "SPEED"})
    assert resp.status_code == 200
    assert resp.json()["recommended_level"] in ["-O0", "-O1", "-O2", "-O3"]

    # 5. Generate Report
    resp = await async_client.post(f"/api/v1/projects/{project_id}/reports", json={"title": "Test Report", "format": "MARKDOWN"})
    assert resp.status_code == 200
    assert "# CompilerX Performance Evaluation Report" in resp.json()["content"]
```

---

## 5. Security & Adversarial Testing (SecOps — CO3)

Hostile C programs are executed in automated test suites to guarantee that the sandbox enforces strict isolation.

### 5.1 Hostile Test Matrix

| Threat Test | Attack Code Snippet | Expected Sandbox Behavior |
|---|---|---|
| **Fork Bomb** | `while(1) { fork(); }` | Terminated via `--pids-limit=64`. Returns `PIDS_EXHAUSTED` or exit status 1. Host unaffected. |
| **Infinite Loop (DoS)** | `volatile int x=0; while(1) x++;` | Hard wall-clock timeout ($10.0\text{s}$). Process killed via `SIGKILL`. Status: `TIMEOUT`. |
| **Memory Exhaustion (OOM)**| `char *p = malloc(1024*1024*1024); memset(p, 1, 1024*1024*1024);` | Terminated by Linux cgroups OOM killer at $256\text{MB}$. Status: `OOM_KILLED`. |
| **Filesystem Wipe Attempt**| `system("rm -rf /"); unlink("/etc/passwd");` | Blocked: Read-only root filesystem (`--read-only`) triggers `EROFS` (Read-only file system). |
| **Network Exfiltration** | `socket(AF_INET, SOCK_STREAM, 0); connect(...);` | Blocked: `--network none` drops all virtual interfaces. Sycall returns `ENETUNREACH`. |

### 5.2 Adversarial Test Implementation Example
```python
@pytest.mark.asyncio
async def test_fork_bomb_resilience(compiler_service, benchmark_service):
    code = """
    #include <unistd.h>
    int main() {
        while(1) { fork(); }
        return 0;
    }
    """
    compilation = await compiler_service.compile_code(code, "-O0")
    assert compilation.success is True
    
    # Run in sandbox
    run_result = await benchmark_service.execute_binary(compilation.binary_path)
    # Process must not hang or freeze host machine
    assert run_result.exit_code != 0
```

---

## 6. MLOps Validation & Regression Testing (CO4)

Tests verify the reproducibility, accuracy, and latency of the Machine Learning pipeline:

1. **Inference Latency Budget:** 100 consecutive predictions must complete with $p_{99} < 10\text{ms}$.
2. **Deterministic Output:** Identical source code must always produce identical extracted feature vectors.
3. **Model Accuracy Baseline:** The trained Random Forest model must achieve $\ge 70\%$ test accuracy on the synthetic benchmark dataset.
4. **Explainability Integrity:** Every recommendation must return a non-empty explanation string containing the name of at least one extracted feature.

---

## 7. CI/CD Automated Test Pipeline Configuration

Automated validation runs on every commit and pull request via GitHub Actions:

```yaml
# .github/workflows/ci.yml (Excerpt)
name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install Dependencies
        run: |
          pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install pytest pytest-asyncio pytest-cov ruff mypy
      - name: Lint & Static Code Analysis (SecOps - CO3)
        run: |
          ruff check backend/
          mypy backend/app
      - name: Execute Backend Tests with Coverage
        run: |
          pytest backend/tests/ --cov=backend/app --cov-report=term-missing --cov-fail-under=75

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install Frontend Dependencies
        working-directory: frontend
        run: npm ci
      - name: TypeScript Compile & Lint
        working-directory: frontend
        run: |
          npm run typecheck
          npm run lint
      - name: Execute Vitest
        working-directory: frontend
        run: npm run test:run
```

---

*This document establishes the official testing strategy for CompilerX.*

