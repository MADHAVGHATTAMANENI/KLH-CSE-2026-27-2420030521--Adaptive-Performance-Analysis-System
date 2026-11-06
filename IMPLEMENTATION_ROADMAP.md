# CompilerX — Implementation Roadmap & Sprint Plan
**AI-Powered Adaptive Code Optimization and Performance Analysis System**

---

| Field | Value |
|---|---|
| **Document Version** | 1.0.0 |
| **Status** | APPROVED — Execution Plan |
| **Author** | Principal Software Architect & Technical Lead |
| **Target Course** | Adaptive Software Engineering (24CI3201), KL University |
| **Phases** | 6 Independently Testable Engineering Milestones |
| **Last Updated** | 2026-11-06 |

---

## 1. Roadmap Overview & Phasing Strategy

To ensure architectural consistency, avoid regression cascades, and maintain strict alignment with **Course Outcome CO1 (Agile Methodologies)**, the implementation is partitioned into six sequential, independently testable phases. 

Each phase yields an observable, verifiable engineering milestone with associated acceptance tests before advancing to the next layer.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Core Foundation & Infrastructure Scaffold                     │
│ [FastAPI Skeleton, DB Models, Docker Compose, CI Pipeline, C Runner]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Phase 2: Compiler & Benchmarking Engine                                │
│ [Clang Invocation, Flag Sanitizer, POSIX Measurement, Stats Engine]    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Phase 3: Adaptive Machine Learning Subsystem (MLOps)                  │
│ [16D Feature Extractor, 50-Program Corpus, Random Forest Pipeline]    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Phase 4: Frontend Workbench & Code Editor                              │
│ [React 18 SPA, Monaco Editor, Zustand Stores, Compiler Terminal]       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Phase 5: Visual Analytics & Reporting Engine                           │
│ [Recharts Speedup Visuals, Regression Banners, Markdown/JSON Reports]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Phase 6: SecOps Hardening, Integration Testing & Defense Prep          │
│ [Trivy Scans, E2E Workflows, High-Variance Stress Tests, Demos]        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Phase 1: Core Foundation & Infrastructure Scaffold

### 2.1 Objective
Establish the project skeleton, containerized runtime environments, asynchronous database persistence, basic health check endpoints, and the automated CI workflow.

### 2.2 Files & Modules Involved
- `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/logging.py`
- `backend/app/db/session.py`, `backend/app/models/base.py`, `backend/app/models/project.py`, `backend/app/models/source_file.py`
- `backend/Dockerfile`, `backend/requirements.txt`
- `sandbox/Dockerfile`, `sandbox/runner.c`
- `docker-compose.yml`
- `.github/workflows/ci.yml`

### 2.3 Dependencies
- Docker Engine & Docker Compose installed.
- Python 3.12 with `fastapi`, `uvicorn`, `sqlalchemy`, `aiosqlite`, `pydantic-settings`.

### 2.4 Implementation Tasks
1. Initialize FastAPI application factory with lifespan management and structured JSON logging (`structlog`).
2. Implement declarative SQLAlchemy models for `Project` and `SourceFile` with UUIDv4 primary keys.
3. Configure SQLite with WAL mode connection pragmas and async session factory.
4. Author `sandbox/runner.c` utilizing `clock_gettime(CLOCK_MONOTONIC_RAW)` and `getrusage(RUSAGE_CHILDREN)`.
5. Build the `compilerx-sandbox` Docker image containing Clang 17 and the compiled runner.
6. Configure `docker-compose.yml` orchestrating backend and database volumes.
7. Set up GitHub Actions workflow (`.github/workflows/ci.yml`) executing `pytest` and `ruff`.

### 2.5 Acceptance Criteria
- `GET /api/v1/health` returns `200 OK` with database and Docker daemon status `CONNECTED`.
- `docker compose up --build` launches services without errors.
- SQLite database initializes with `projects` and `source_files` tables.
- Running `/usr/local/bin/compilerx-runner /bin/ls` inside the sandbox prints valid JSON metrics.

### 2.6 Test Cases
- `test_health_endpoint`: Verifies HTTP 200 and schema validity.
- `test_db_session_lifecycle`: Confirms async session commit and rollback.
- `test_sandbox_runner_execution`: Runs a test executable through `runner` and parses stdout JSON.

### 2.7 Potential Risks & Mitigation
- **Risk:** Docker socket permissions on macOS vs. Linux.
- **Mitigation:** Use conditional socket path binding and test locally on both host architectures.

---

## 3. Phase 2: Compiler & Benchmarking Engine

### 3.1 Objective
Implement real Clang compilation across `-O0` to `-O3`, strict flag whitelisting, sandboxed execution, and multi-run statistical aggregation.

### 3.2 Files & Modules Involved
- `backend/app/services/compiler_service.py`
- `backend/app/services/benchmark_service.py`
- `backend/app/models/compilation.py`, `backend/app/models/benchmark.py`
- `backend/app/schemas/compilation.py`, `backend/app/schemas/benchmark.py`
- `backend/app/api/v1/compiler.py`, `backend/app/api/v1/benchmark.py`

### 3.3 Dependencies
- Phase 1 completed (DB tables, Docker sandbox runner available).

### 3.4 Implementation Tasks
1. Implement `CompilerService.compile_file()` with flag whitelist verification and programmatic argument vector creation.
2. Capture Clang compilation duration, binary size, exit codes, and ANSI diagnostics.
3. Implement `BenchmarkService.run_benchmark()` executing the compiled binary inside an ephemeral Docker container.
4. Implement `BenchmarkService.run_suite()` orchestrating compilation and $N$-run benchmarking across `-O0`, `-O1`, `-O2`, and `-O3`.
5. Implement statistical calculations: Mean, Median, Sample StdDev, Min, Max, and $CV\%$.
6. Wire API endpoints `POST /files/{id}/compile`, `POST /compilations/{id}/benchmark`, and `POST /files/{id}/benchmark-suite`.

### 3.5 Acceptance Criteria
- Valid C program compiles cleanly and produces recorded binary size and compilation time.
- Syntax error in C code returns HTTP 400 with structured diagnostic errors.
- Unwhitelisted flag (e.g. `-Xclang`) is rejected with HTTP 422.
- Benchmark suite returns aggregated results showing empirical execution time across all 4 levels.
- High variance runs ($CV > 15\%$) are flagged with `has_high_variance = true`.

### 3.6 Test Cases
- `test_compile_valid_c_program`: Verifies exit code 0 and binary size $> 0$.
- `test_compile_syntax_error`: Verifies Clang error message extraction and HTTP 400.
- `test_flag_whitelist_rejection`: Passes malicious flags and asserts HTTP 422.
- `test_benchmark_statistical_aggregation`: Feeds known runtime arrays and validates $\mu$, $\sigma$, and median calculations.

### 3.7 Potential Risks & Mitigation
- **Risk:** Benchmark noise caused by host CPU throttling or background OS tasks.
- **Mitigation:** Outlier filtering and explicit Coefficient of Variation ($CV$) computation to alert the user.

---

## 4. Phase 3: Adaptive Machine Learning Subsystem (MLOps)

### 4.1 Objective
Build the static code feature extraction engine, curate a 50-program synthetic training corpus, train a Random Forest classifier, and expose recommendation and evaluation endpoints (**CO4**).

### 4.2 Files & Modules Involved
- `backend/app/ml/features.py`
- `backend/app/ml/dataset.py`
- `backend/app/ml/train.py`
- `backend/app/services/ml_service.py`
- `backend/app/models/recommendation.py`
- `backend/app/api/v1/ml.py`

### 4.3 Dependencies
- Phase 2 completed (benchmarking available to label the training corpus).
- `scikit-learn`, `numpy`, `joblib`.

### 4.4 Implementation Tasks
1. Implement `extract_features(code: str) -> dict` in `features.py` computing all 16 lexical and structural metrics.
2. Curate 50 canonical C microbenchmarks in `dataset.py` spanning dense math, sorting, recursion, pointer chasing, and bit operations.
3. Implement `train.py`: benchmarks all 50 programs, labels optimal levels, fits a `RandomForestClassifier(n_estimators=100)`, and serializes `model.joblib`.
4. Implement `MLService.recommend()` returning the predicted level, confidence score, and natural-language explanation.
5. Wire API endpoints: `GET /optimization/features/{id}`, `POST /files/{id}/recommend`, `GET /ml/model/status`, and `POST /ml/model/retrain`.

### 4.5 Acceptance Criteria
- Feature extraction completes in $< 50\text{ms}$ for standard C files.
- Random Forest model achieves $> 70\%$ classification accuracy on held-out test split.
- `GET /api/v1/ml/model/status` returns accuracy, F1 score, and $4 \times 4$ confusion matrix.
- `POST /api/v1/files/{id}/recommend` outputs clear justifications referencing top features.

### 4.6 Test Cases
- `test_feature_extraction_accuracy`: Tests sample C snippets with known loops, branches, and arithmetic counts.
- `test_ml_inference_latency`: Validates inference execution in $< 10\text{ms}$.
- `test_model_retrain_endpoint`: Verifies model retraining and metric updates.

### 4.7 Potential Risks & Mitigation
- **Risk:** Small dataset leading to class imbalance (e.g. `-O2` dominating).
- **Mitigation:** Stratified train/test splitting and intentional corpus curation covering distinct workload profiles.

---

## 5. Phase 4: Frontend Workbench & Code Editor

### 5.1 Objective
Construct the modern dark-mode developer workbench featuring the Monaco Editor, project sidebar, compilation controls, live ANSI terminal, and benchmark trigger UI.

### 5.2 Files & Modules Involved
- `frontend/src/App.tsx`, `frontend/src/main.tsx`, `frontend/src/pages/WorkspacePage.tsx`
- `frontend/src/components/editor/CodeEditor.tsx`
- `frontend/src/components/compiler/CompilerPanel.tsx`
- `frontend/src/components/benchmark/BenchmarkRunner.tsx`
- `frontend/src/components/ml/MLRecommendationCard.tsx`
- `frontend/src/stores/useEditorStore.ts`, `frontend/src/services/api.ts`

### 5.3 Dependencies
- Phase 2 & 3 completed (working backend APIs).
- React 18, Vite, Tailwind CSS, Monaco Editor, Zustand, TanStack Query, Axios.

### 5.4 Implementation Tasks
1. Initialize Vite + React + TypeScript project with Tailwind CSS dark theme tokens.
2. Integrate Monaco Editor with C/C++ syntax highlighting, dirty state tracking, and keyboard save shortcuts.
3. Build Project and File management sidebar (create, select, delete, upload).
4. Implement Compiler Panel with optimization level selectors and real-time ANSI terminal output.
5. Implement ML Recommendation badge rendering predicted flags and explanatory rationales.
6. Integrate Benchmark Suite runner with progress polling indicator.

### 5.5 Acceptance Criteria
- Code editor loads and renders C/C++ code with full syntax highlighting.
- Clicking "Compile" dispatches API request and updates terminal output within 1 second.
- Errors returned by Clang display in the terminal and highlight corresponding editor lines.
- Recommendation badge renders dynamically when a file is selected.

### 5.6 Test Cases
- `test_editor_mounts_and_updates`: Mounts Monaco and tests state updates.
- `test_compiler_panel_actions`: Mocks compilation API and verifies terminal output rendering.
- `test_zustand_store_persistence`: Confirms store updates upon file selection.

### 5.7 Potential Risks & Mitigation
- **Risk:** Monaco Editor bundle size causing slow initial load.
- **Mitigation:** Utilize Monaco web-worker splitting and lazy loading via `@monaco-editor/react`.

---

## 6. Phase 5: Visual Analytics & Reporting Engine

### 6.1 Objective
Build the Recharts visual analytics suite, speedup KPI cards, binary size comparisons, regression detection banners, and the academic Markdown/JSON report export engine.

### 6.2 Files & Modules Involved
- `frontend/src/components/analytics/AnalyticsDashboard.tsx`
- `frontend/src/components/analytics/SpeedupBarChart.tsx`
- `frontend/src/components/analytics/BinarySizeChart.tsx`
- `frontend/src/components/reports/ReportExporter.tsx`
- `backend/app/services/analytics_service.py`
- `backend/app/services/report_service.py`
- `backend/app/api/v1/analytics.py`, `backend/app/api/v1/reports.py`

### 6.3 Dependencies
- Phase 4 completed (Frontend SPA operational).
- Recharts 2.12+, Markdown rendering components.

### 6.4 Implementation Tasks
1. Implement Recharts grouped bar chart displaying mean wall-clock execution time with standard deviation error bars.
2. Implement Speedup Factor comparison cards relative to `-O0`.
3. Implement Binary Size vs. Runtime trade-off visualization.
4. Implement regression detection banner: triggers if $\bar{T}_{O(k+1)} > \bar{T}_{Ok} \times 1.05$.
5. Implement `ReportService.generate_report()` stamping CPU model, kernel version, Clang build, full statistics, and ML explanations.
6. Build frontend Report export modal with Markdown preview and download triggers.

### 6.5 Acceptance Criteria
- Analytics dashboard renders grouped charts immediately upon benchmark suite completion.
- Speedup multipliers match mathematical ground truth ($S = \frac{\mu_{O0}}{\mu_{Ox}}$).
- Regressions (e.g. `-O3` slower than `-O2`) display an explicit warning explaining potential cache effects.
- Generated Markdown report downloads cleanly and renders tables without formatting defects.

### 6.6 Test Cases
- `test_analytics_speedup_calculation`: Verifies accurate mathematical division and zero-division handling.
- `test_regression_detector`: Feeds artificial regression data and verifies warning trigger.
- `test_report_generation_markdown`: Generates report and verifies presence of all required sections.

### 6.7 Potential Risks & Mitigation
- **Risk:** Chart layout breaking on smaller laptop viewports.
- **Mitigation:** Use `ResponsiveContainer` from Recharts with minimum width constraints.

---

## 7. Phase 6: SecOps Hardening, Integration Testing & Defense Prep

### 7.1 Objective
Execute security hardening (seccomp filters, capability drops, Trivy container scanning), run end-to-end integration tests, and prepare demonstration scripts for course evaluation.

### 7.2 Files & Modules Involved
- `sandbox/seccomp.json`
- `backend/tests/test_e2e_workflow.py`
- `.github/workflows/security-scan.yml`
- `demo_script.md`, `README.md`

### 7.3 Dependencies
- All prior phases (Phases 1–5) fully functional.
- Docker, Trivy, SonarQube / static linters.

### 7.4 Implementation Tasks
1. Finalize and test the custom `seccomp.json` profile blocking unsafe syscalls.
2. Enforce container memory limits ($256\text{MB}$) and process limits ($64\text{ PIDs}$); verify fork-bomb and OOM handling.
3. Configure GitHub Actions automated Trivy vulnerability scan on Docker images.
4. Execute full end-to-end integration test: Project creation $\to$ File upload $\to$ Compile $\to$ Benchmark Suite $\to$ ML Recommendation $\to$ Report Export.
5. Author step-by-step evaluator demonstration walkthrough in `README.md`.

### 7.5 Acceptance Criteria
- Malicious C code attempting `fork()` bomb or `system("rm -rf /")` is neutralized without host impact.
- Zero high/critical vulnerabilities reported in dependencies by `pip-audit` or Trivy.
- Complete end-to-end integration test suite passes cleanly in CI.
- Single command `docker compose up --build` launches fully functional platform ready for presentation.

### 7.6 Test Cases
- `test_fork_bomb_resilience`: Submits recursive `fork()` C code; asserts container containment and `PIDS_EXHAUSTED` error.
- `test_infinite_loop_timeout`: Submits `while(1){}`; asserts 10-second termination via `SIGKILL`.
- `test_oom_resilience`: Submits 1 GB allocation; asserts container terminates gracefully with `OOM_KILLED`.

### 7.7 Potential Risks & Mitigation
- **Risk:** Live demonstration failure due to local Docker daemon latency.
- **Mitigation:** Pre-compile container images and pre-cache synthetic benchmark samples.

---

## 8. Milestone Timeline & Course Outcome Progress

| Milestone | Deliverable Phase | Estimated Sprint Duration | Course Outcomes Validated |
|---|---|---|---|
| **M1: Foundation** | Phase 1 (Infra, DB, C Runner, CI) | 3 Days | **CO2** (Docker, Git), **CO5** (Repo Setup) |
| **M2: Compiler & Benchmark**| Phase 2 (Clang, Sandbox, Stats) | 4 Days | **CO2** (DevOps), **CO3** (Isolation) |
| **M3: MLOps Subsystem** | Phase 3 (Features, Corpus, RF Model)| 4 Days | **CO4** (MLOps, Lifecycle, Training) |
| **M4: Developer Workbench**| Phase 4 (React, Monaco, Terminal) | 4 Days | **CO1** (User Experience, Agile) |
| **M5: Analytics & Reports** | Phase 5 (Recharts, Regressions, Export)| 3 Days | **CO1** (Analysis), **CO2** (Metrics) |
| **M6: Hardening & Defense**| Phase 6 (SecOps, Trivy, E2E Tests) | 3 Days | **CO3** (SecOps), **CO5** (Review, Docs) |

---

*This document establishes the official implementation roadmap for CompilerX.*

