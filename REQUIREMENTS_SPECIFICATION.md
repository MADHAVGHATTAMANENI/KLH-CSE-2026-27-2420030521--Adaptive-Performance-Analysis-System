# CompilerX — Requirements Specification Document
**AI-Powered Adaptive Code Optimization and Performance Analysis System**

---

| Field | Value |
|---|---|
| **Document Version** | 1.0.0 |
| **Status** | APPROVED — Baseline Requirements |
| **Author** | Principal Software Architect & Technical Lead |
| **Target Course** | Adaptive Software Engineering (24CI3201), KL University |
| **Course Outcomes Covered** | CO1 (Agile/SDLC), CO2 (DevOps/CI-CD/Docker), CO3 (SecOps/Sandboxing), CO4 (MLOps/Cloud-Ready ML), CO5 (Teamwork/Reviews) |
| **Last Updated** | 2026-11-06 |

---

## 1. Document Overview & Metadata

### 1.1 Purpose
This document establishes the formal software requirements specification (SRS) for **CompilerX**. It details the functional, non-functional, security, and operational requirements demanded by the academic syllabus for **Adaptive Software Engineering (24CI3201)**, while establishing enterprise-grade engineering criteria that elevate the platform to a professional developer product.

### 1.2 Categorization Framework
To prevent scope creep and ensure explicit academic grading alignment, every requirement is tagged with two taxonomy axes:

1. **Course Outcome Mapping:** Mapped directly to Course Outcomes **CO1**, **CO2**, **CO3**, **CO4**, or **CO5**.
2. **Requirement Category:**
   - **[MANDATORY COURSE REQUIREMENT]**: Direct fulfillment of core ASE syllabus components (Docker containerization, CI/CD automation, static analysis, MLOps model deployment, Git workflow, testability).
   - **[PROPOSED PRODUCT ENHANCEMENT]**: Architectural and product capabilities designed to deliver a high-grade developer experience (Monaco editor integration, Recharts visual analytics, multi-run statistical outlier rejection, explainable ML rationales).

3. **Priority Levels:**
   - **P0 (Critical / Blocker):** Core capabilities required for MVP and passing evaluation criteria.
   - **P1 (High):** Complete system functionality expected for full marks in practical project evaluation.
   - **P2 (Medium / Polish):** Advanced optimizations, export options, and usability polish.

---

## 2. Course Syllabus Alignment Matrix

The table below maps the official 24CI3201 Course Outcomes (COs) and Bloom's Taxonomy Levels (BTL) from the course handout directly to the CompilerX system components.

| Course Outcome | BTL | Syllabus Focus | Mandatory System Deliverables in CompilerX |
|---|---|---|---|
| **CO1: Software Engineering Foundations & Agile** | BTL-2 | SDLC models, Scrum framework, user stories, backlog grooming, estimation, team velocity. | • Formal Agile user story breakdown with acceptance criteria.<br>• Phase-gated sprint roadmap (6 distinct milestones).<br>• Work item tracking and velocity estimation schema. |
| **CO2: DevOps Fundamentals** | BTL-3 | Git workflows, CI/CD concepts, Docker containerization, Kubernetes/Minikube concepts, observability. | • Multi-container Docker Compose architecture.<br>• Automated GitHub Actions CI/CD pipeline (lint, unit tests, integration tests, Docker build).<br>• Gitflow branching strategy with branch protection rules. |
| **CO3: Security Operations (SecOps)** | BTL-3 | Static code analysis, vulnerability scanning, secrets management, secure coding, OWASP Top 10 compliance. | • Ephemeral Docker sandbox with non-root user, dropped capabilities (`CAP_DROP_ALL`), read-only rootfs, and strict `seccomp` filter.<br>• Zero-trust compiler flag whitelisting.<br>• Automated static analysis via SonarQube / Ruff / Trivy container scanning. |
| **CO4: MLOps and Cloud Deployment** | BTL-3 | MLOps lifecycle: data collection, model training, versioning, deployment, monitoring, model inference. | • Reproducible ML training pipeline for compiler optimization recommendation.<br>• Feature extraction engine (16 lexical & structural AST descriptors).<br>• Model versioning, evaluation metrics (accuracy, confusion matrix, F1), and low-latency inference API.<br>• Periodic automated retraining capability. |
| **CO5: Teamwork and Peer Code Review** | BTL-3 | Collaborative development, code review practices, modular ownership, team coordination. | • Modular codebase with clean service boundaries enabling independent subsystem ownership.<br>• Standardized pull request templates, linting automation, and review checklists. |

---

## 3. Functional Requirements (FR)

### 3.1 Module A: Code Management & Workbench (FR-100)

#### FR-101: Monaco Source Code Editor Integration
- **Category:** [PROPOSED PRODUCT ENHANCEMENT]
- **Priority:** P0
- **Course Mapping:** CO1, CO5
- **Description:** The system shall provide an in-browser code editor powered by Monaco Editor (`@monaco-editor/react`), supporting C (C99/C11) and C++ (C++14/C++17/C++20) syntax highlighting, code folding, bracket matching, line numbers, and minimap navigation.
- **Acceptance Criteria:**
  1. Editor mounts within $< 500\text{ms}$ upon navigating to a project workspace.
  2. Language mode automatically toggles based on file extension (`.c` vs. `.cpp`).
  3. Supports dirty-state tracking; uncommitted changes display an unsaved indicator.
  4. Supports keyboard shortcuts (`Cmd+S` / `Ctrl+S` to trigger file save).

#### FR-102: Source File Management & Upload
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO1, CO3
- **Description:** The system shall support creating, updating, viewing, and uploading single-file C and C++ source code files up to a maximum size of 1 MB.
- **Acceptance Criteria:**
  1. Users can upload `.c` and `.cpp` files via drag-and-drop or file picker.
  2. The backend enforces a strict 1 MB file size limit and returns HTTP 413 if exceeded.
  3. The backend calculates a SHA-256 digest of file content to enable deduplication and caching.
  4. Rejects binary, non-UTF-8, or malicious multipart payloads with HTTP 422.

#### FR-103: Project Workspace & Organization
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P1
- **Course Mapping:** CO1, CO5
- **Description:** The system shall allow users to organize code into named projects with descriptions and target language tags.
- **Acceptance Criteria:**
  1. Users can create, list, inspect, and delete projects.
  2. Deleting a project cascades deletion to all associated source files, compilations, benchmark records, and reports.
  3. Project listing returns total file counts and last-modified timestamps.

#### FR-104: Built-in Benchmark Algorithm Templates
- **Category:** [PROPOSED PRODUCT ENHANCEMENT]
- **Priority:** P1
- **Course Mapping:** CO1, CO4
- **Description:** The system shall provide a curated library of pre-loaded C/C++ benchmark programs representing diverse algorithmic workloads (Matrix Multiply, Quicksort, Sieve of Eratosthenes, Fibonacci recursion, Binary Search).
- **Acceptance Criteria:**
  1. Users can select and load any template into the editor with one click.
  2. Each template includes standard POSIX headers, self-contained workload execution, and standard validation output.

---

### 3.2 Module B: Compiler Engine & Diagnostics (FR-200)

#### FR-201: Real Clang Compilation Execution
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO2, CO3
- **Description:** The system shall invoke an actual LLVM/Clang compiler instance to compile user-submitted C/C++ code at optimization levels `-O0`, `-O1`, `-O2`, and `-O3`.
- **Acceptance Criteria:**
  1. Compilation executes inside the designated isolated sandbox environment.
  2. Compilation completes within a hard timeout limit of 15 seconds.
  3. Compiler commands are passed as discrete argument arrays (no `shell=True` execution).
  4. Returns the exact exit code, compilation duration (in milliseconds), and generated binary artifact path upon success.

#### FR-202: Compiler Flag Whitelisting & Custom Configurations
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO3
- **Description:** The system shall allow users to supply auxiliary compiler flags, strictly constrained to an immutable security whitelist.
- **Acceptance Criteria:**
  1. Whitelisted flags include: `-Wall`, `-Wextra`, `-pedantic`, `-std=c11`, `-std=c17`, `-std=c++17`, `-std=c++20`, `-ffast-math`, `-funroll-loops`.
  2. Any unapproved flag (e.g., `-Xclang`, `-load`, `-include`, `-I/etc`, paths) triggers an HTTP 422 validation error with an explicit rejection explanation.

#### FR-203: Diagnostic Parsing & Compiler Error Reporting
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO1, CO3
- **Description:** The system shall capture compiler `stdout` and `stderr` streams, parsing Clang diagnostics into structured warning and error objects.
- **Acceptance Criteria:**
  1. On compilation failure (exit code $\ne 0$), HTTP 400 is returned with structured diagnostic lines containing file, line number, column, severity, and error message.
  2. The frontend terminal component renders raw compiler output with ANSI syntax styling.
  3. Line-level errors map to visual annotations in the Monaco editor gutter.

#### FR-204: Binary Artifact Inspection
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P1
- **Course Mapping:** CO2, CO3
- **Description:** The system shall inspect generated executable binaries to extract physical byte size and section breakdown (`.text`, `.data`, `.bss`).
- **Acceptance Criteria:**
  1. Total binary size in bytes is recorded for every successful compilation.
  2. Binary size differences across optimization levels are computed and persisted.
  3. Binaries are stored in an ephemeral build cache and purged according to retention policy.

---

### 3.3 Module C: Performance Analysis & Benchmarking Engine (FR-300)

#### FR-301: Sandboxed Program Execution
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO2, CO3
- **Description:** The system shall execute compiled binaries inside an ephemeral, resource-constrained Docker container isolated from the host machine and network.
- **Acceptance Criteria:**
  1. Container environment parameters: `--network none`, `--memory 256m`, `--cpus 1.0`, `--pids-limit 64`, read-only rootfs.
  2. Program execution is terminated with `SIGKILL` if wall-clock runtime exceeds 10.0 seconds.
  3. User-provided `stdin` input is piped securely to the executing process.
  4. Process termination states (Normal exit, Timeout, OOM-Killed, Segmentation Fault) are correctly captured and reported.

#### FR-302: Precision Runtime & Memory Measurement
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO2, CO3
- **Description:** The system shall record wall-clock execution time, user/kernel CPU time, and peak resident memory usage for every benchmark run using low-overhead OS measurement primitives.
- **Acceptance Criteria:**
  1. Wall-clock time is measured via monotonic hardware clock (`CLOCK_MONOTONIC_RAW`) with microsecond resolution.
  2. CPU time is recorded via `getrusage(RUSAGE_CHILDREN)`.
  3. Peak Resident Set Size (RSS) is recorded in kilobytes.
  4. Zero hardcoded, fabricated, or simulated figures; all data points must derive from actual process execution.

#### FR-303: Multi-Run Statistical Aggregation
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P1
- **Course Mapping:** CO1, CO2
- **Description:** The system shall support repeated benchmark runs ($N \in [3, 10]$) for a compiled binary and compute statistical metrics to account for OS scheduling variance.
- **Acceptance Criteria:**
  1. Computes Arithmetic Mean ($\mu$), Median, Sample Standard Deviation ($\sigma$), Minimum, and Maximum.
  2. Computes the Coefficient of Variation ($CV = \frac{\sigma}{\mu} \times 100\%$).
  3. If $CV > 15\%$, flags the benchmark run with a "High Variance / Noisy Environment" warning in the UI.

#### FR-304: Automated Multi-Optimization Benchmark Suite
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO2, CO4
- **Description:** The system shall provide a single-action workflow that compiles a source file across all four optimization levels (`-O0`, `-O1`, `-O2`, `-O3`), benchmarks each configuration for $N$ iterations, and produces a consolidated comparative result set.
- **Acceptance Criteria:**
  1. Endpoint `POST /api/v1/benchmarks/suite` orchestrates the complete matrix run.
  2. Returns a job tracking ID with `202 Accepted` status.
  3. Supports progress polling via `GET /api/v1/benchmarks/suite/{id}`.
  4. Automatically computes speedup multipliers relative to `-O0` baseline.

---

### 3.4 Module D: Adaptive AI Optimization Engine (FR-400)

#### FR-401: Static Code Feature Extraction
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO4
- **Description:** The system shall parse C/C++ source code to extract a 16-dimensional numeric feature vector characterizing structural, computational, and control-flow properties.
- **Acceptance Criteria:**
  1. Extracted features include: LOC, function count, cyclomatic complexity, loop count, maximum loop nesting depth, integer arithmetic count, float arithmetic count, pointer dereference count, array indexing count, branch count, recursive calls, bitwise operations, memory allocation calls, math library calls, global variables, and arithmetic-to-branch ratio.
  2. Feature extraction completes in $< 100\text{ms}$ for source files up to 1 MB.
  3. Returns raw feature vectors in JSON format via `GET /api/v1/optimization/features/{file_id}`.

#### FR-402: ML-Based Optimization Level Recommendation
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO4
- **Description:** The system shall utilize a trained machine learning model (`scikit-learn` Random Forest Classifier) to recommend the optimal compiler optimization flag based on the extracted feature vector and user-selected objective (`SPEED`, `SIZE`, or `BALANCED`).
- **Acceptance Criteria:**
  1. Model inference executes in $< 10\text{ms}$ on CPU.
  2. Returns the recommended level (`-O0`, `-O1`, `-O2`, or `-O3`) with an associated confidence score between $0.00$ and $1.00$.
  3. The model must be a real serialized model artifact (`model.joblib`), not an external LLM API call.

#### FR-403: Natural Language Model Explainability
- **Category:** [PROPOSED PRODUCT ENHANCEMENT]
- **Priority:** P1
- **Course Mapping:** CO4
- **Description:** The recommendation engine shall provide human-readable explanations indicating why a specific optimization level was recommended, referencing top contributing features.
- **Acceptance Criteria:**
  1. Explanations reference quantifiable code features (e.g., *"Deep loop nesting (level 3) and high float arithmetic density strongly favor -O3 auto-vectorization"*).
  2. If `-Os` or `-O1` is recommended for size, explanation cites binary bloat risks or low loop intensity.

#### FR-404: MLOps Training & Evaluation Pipeline
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P1
- **Course Mapping:** CO4
- **Description:** The system shall provide an automated training and evaluation pipeline capable of training the recommendation model on benchmark datasets and exposing validation metrics.
- **Acceptance Criteria:**
  1. Exposes an endpoint `POST /api/v1/ml/retrain` to trigger model retraining.
  2. Exposes an endpoint `GET /api/v1/ml/metrics` returning: overall test accuracy, F1-score (macro), per-class precision/recall, and the full multiclass confusion matrix.
  3. Automatically archives previous model versions with timestamped metadata.

#### FR-405: Predicted vs. Actual Performance Verification
- **Category:** [PROPOSED PRODUCT ENHANCEMENT]
- **Priority:** P1
- **Course Mapping:** CO4
- **Description:** After executing a benchmark suite on a file that received an ML recommendation, the system shall compare the predicted best level against the empirically observed fastest level.
- **Acceptance Criteria:**
  1. Stores verification record linking `recommendation_id` to `suite_result_id`.
  2. Computes recommendation accuracy (True Positive: predicted level was fastest).
  3. Renders verification badge in the UI ("Prediction Verified: Correct" vs. "Misprediction / Anomaly").

---

### 3.5 Module E: Benchmark Comparison & Analytics Dashboard (FR-500)

#### FR-501: Comparative Visualizations
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P0
- **Course Mapping:** CO1, CO2
- **Description:** The system shall render interactive comparative charts displaying execution time distributions, speedup ratios, memory utilization, and binary size across optimization levels using Recharts.
- **Acceptance Criteria:**
  1. Grouped bar chart comparing Mean Execution Time (ms) across `-O0`, `-O1`, `-O2`, `-O3` with error bars indicating standard deviation.
  2. Speedup indicator relative to baseline `-O0`:
     $$\text{Speedup} = \frac{\bar{T}_{O0}}{\bar{T}_{Ox}}$$
  3. Binary size delta comparison bar chart.
  4. Memory footprint (peak RSS KB) comparison.

#### FR-502: Performance Regression Detection
- **Category:** [PROPOSED PRODUCT ENHANCEMENT]
- **Priority:** P1
- **Course Mapping:** CO2
- **Description:** The system shall automatically detect and flag compiler optimization regressions where a higher optimization level yields slower execution time than a lower level (e.g., `-O3` slower than `-O2`).
- **Acceptance Criteria:**
  1. Flags regression warning banner if:
     $$\bar{T}_{O(k+1)} > \bar{T}_{Ok} \times 1.05$$
  2. Explains potential causes (e.g., instruction cache thrashing due to aggressive loop unrolling).

#### FR-503: Historical Project Analytics
- **Category:** [PROPOSED PRODUCT ENHANCEMENT]
- **Priority:** P2
- **Course Mapping:** CO1, CO2
- **Description:** The system shall provide a project-level analytics view showing compilation frequency, average speedup trends, and benchmark execution history over time.
- **Acceptance Criteria:**
  1. Renders historical timeline of benchmark suites executed for the active project.
  2. Summarizes overall project metrics: total compilations, average speedup achieved, fastest configuration.

---

### 3.6 Module F: Report Generation & Export (FR-600)

#### FR-601: Academic & Engineering Report Generation
- **Category:** [MANDATORY COURSE REQUIREMENT]
- **Priority:** P1
- **Course Mapping:** CO1, CO2, CO3, CO4
- **Description:** The system shall compile and export comprehensive performance reports in structured JSON and publication-quality Markdown formats.
- **Acceptance Criteria:**
  1. Includes complete hardware & environment metadata: CPU model, core count, OS kernel, Clang toolchain version.
  2. Includes source code content hash and file size.
  3. Includes exact compiler commands and optimization flags used.
  4. Includes full statistical summary table ($\mu$, Median, $\sigma$, Min, Max, Speedup).
  5. Includes ML recommendation, confidence score, and feature explanation.
  6. Endpoint `POST /api/v1/reports/generate` returns downloadable file or structured JSON.

---

## 4. Non-Functional Requirements (NFR)

### 4.1 Performance & Latency (NFR-01 to NFR-04)

- **NFR-01 (Compilation Latency):** Typical C/C++ source files ($\le 500\text{ LOC}$) must compile in $< 3.0\text{ seconds}$ inside the sandbox container.
- **NFR-02 (Execution Timeout):** User program execution shall have a strict hard deadline of $10.0\text{ seconds}$ wall-clock time; background processes are terminated with `SIGKILL` upon expiration.
- **NFR-03 (Frontend Initialization):** The SPA initial load time shall be $< 2.0\text{ seconds}$ on standard broadband, with Monaco Editor mounting in $< 500\text{ms}$.
- **NFR-04 (API Responsiveness):** Non-compilation REST API endpoints (`/projects`, `/files`, `/features`, `/reports`) shall respond with $p_{95} < 100\text{ms}$.

### 4.2 Reliability & Concurrency (NFR-05 to NFR-06)

- **NFR-05 (Concurrent Workloads):** The system shall reliably support at least 5 concurrent compilation/benchmarking jobs on standard developer hardware without process leakage or container zombie state.
- **NFR-06 (Data Integrity & Crash Safety):** The persistence layer (SQLite WAL / PostgreSQL) shall ensure zero data corruption on abrupt server shutdown. File operations must be atomic.

### 4.3 Security & Sandboxing (NFR-07 to NFR-08)

- **NFR-07 (Host Isolation):** User-submitted code execution must be completely isolated from the host filesystem, environment variables, network stack, and process tree.
- **NFR-08 (Resource Containment):** Execution containers are hard-bounded: $\text{RAM} \le 256\text{ MB}$, $\text{CPU} \le 1.0\text{ core}$, $\text{PIDs} \le 64$. Fork bombs and memory leaks must not degrade host stability.

### 4.4 Software Engineering Quality & Maintainability (NFR-09 to NFR-11)

- **NFR-09 (Test Coverage):** Backend service layer unit and integration test coverage must exceed $75\%$ measured by `pytest-cov`.
- **NFR-10 (Type Safety):** 100% strict type safety enforced across frontend (TypeScript `strict: true`, no `any`) and backend (Python type annotations enforced via `mypy` and Pydantic).
- **NFR-11 (Reproducibility & DevOps):** The entire application stack (frontend, backend, sandbox) must build and run locally with a single command: `docker compose up --build`.

---

## 5. Constraints & Assumptions

### 5.1 Technical Constraints
1. **Host Environment:** Target development and evaluation platform is macOS (Apple Silicon / Intel) or Linux (x86_64 / arm64).
2. **Toolchain Requirement:** Requires Docker Engine / Docker Desktop installed and running on the host machine.
3. **Language Scope:** Single-file C (C99, C11) and C++ (C++14, C++17, C++20) programs only. Multi-file compilation and external custom libraries (beyond libc/libm/libc++) are explicitly out of scope.
4. **Execution Architecture:** Purely local execution via Docker Compose; no third-party cloud infrastructure required for standard evaluation.

### 5.2 Operating Assumptions
1. Submitted source programs are non-interactive after consuming provided `stdin` payloads (no infinite interactive CLI loops).
2. Evaluator has network access during initial `docker compose build` to pull base images and npm/pip packages.

---

*This document serves as the formal baseline requirement contract for CompilerX. All architectural designs, database schemas, and implementation milestones directly derive from the requirements specified herein.*

