# CompilerX — AI-Powered Adaptive Code Optimization and Performance Analysis System

[![CI Pipeline](https://github.com/compilerx/compilerx/actions/workflows/ci.yml/badge.svg)](https://github.com/compilerx/compilerx/actions/workflows/ci.yml)
[![Security Scan](https://github.com/compilerx/compilerx/actions/workflows/security-scan.yml/badge.svg)](https://github.com/compilerx/compilerx/actions/workflows/security-scan.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/Frontend-React%2018%20%7C%20TypeScript-61DAFB.svg)](https://react.dev/)
[![LLVM / Clang](https://img.shields.io/badge/Compiler-LLVM%20%2F%20Clang-red.svg)](https://clang.llvm.org/)
[![Code Coverage](https://img.shields.io/badge/Coverage-74%25-brightgreen.svg)]()

> **Undergraduate Advanced Software Engineering (ASE — 24CI3201) Capstone Project**  
> Department of Computer Science & Engineering, KL University  
> Architected, developed, and verified to professional engineering specifications.

---

## 1. System Overview

**CompilerX** is a developer platform that bridges compiler technology, empirical performance benchmarking, and offline machine learning to recommend adaptive compiler optimization flags (`-O0`, `-O1`, `-O2`, `-O3`, `-Os`).

Instead of blindly applying `-O3` (which can induce instruction-cache thrashing, branch mispredictions, or binary code bloat), CompilerX extracts 16 static Abstract Syntax Tree (AST) code features, runs controlled multi-iteration benchmarking via high-resolution native C instrumentation (`clock_gettime(CLOCK_MONOTONIC_RAW)`), detects optimization regressions, calculates the speed vs. size Pareto frontier, and serves explainable ML recommendations using a trained Random Forest classifier.

### Key Capabilities
- **Code Workbench:** Dark-first Monaco editor with real-time C/C++ syntax highlighting, dirty state tracking, and project-based multi-file tree.
- **Clang Compiler Engine:** Subprocess compilation with strict argument whitelisting, diagnostic capturing, exit code tracking, and binary byte size calculation.
- **Microsecond Benchmarking Harness:** Isolated C runner (`sandbox/runner.c`) capturing wall-clock duration, user/kernel CPU times, and peak resident set size (RSS) memory without Python runtime contamination.
- **Adaptive AI Optimization Subsystem:** 16-dimensional static code feature extractor paired with an offline Scikit-Learn Random Forest model (100 estimators, 83.3% test accuracy) explaining decision weights.
- **Comparative Visual Analytics:** Interactive Recharts dashboard visualizing mean runtimes with sample standard deviation error bounds, speedup multipliers, binary size footprints, and high-variance flags ($CV > 10\%$).
- **Performance Regression Detection:** Automatic alert generation when aggressive optimization levels cause execution slowdowns (e.g. `-O3` slower than `-O2`).
- **Pareto Trade-off Analysis:** Mathematical non-dominated set calculation balancing runtime minimization and binary size compactness.
- **Audit Report Generator:** One-click export to comprehensive Markdown and JSON performance audit reports complete with host platform specs, compiler version, and verification metadata.

---

## 2. Mapping to Course Outcomes (CO1 – CO5)

| Course Outcome | Handout Domain | CompilerX Implementation Component |
| :--- | :--- | :--- |
| **CO1** | Agile SDLC & Planning | 6-phase roadmap, user story acceptance criteria, Jira-compatible issue structure documented in `IMPLEMENTATION_ROADMAP.md`. |
| **CO2** | DevOps & CI/CD Pipelines | GitHub Actions workflows (`.github/workflows/ci.yml`), automated pytest runner, type checks, Vite build, and multi-stage Docker builds. |
| **CO3** | SecOps & Isolation | Defense-in-depth architecture: restricted non-root execution, cgroups CPU/memory quotas, Seccomp syscall filtering (`sandbox/seccomp.json`), Trivy scanning (`.github/workflows/security-scan.yml`). |
| **CO4** | MLOps & Model Serving | Offline feature extraction (`backend/app/ml/features.py`), reproducible synthetic corpus (`dataset.py`), model serialization (`model.joblib`), live metrics snapshot (`metrics.json`), sub-millisecond CPU inference. |
| **CO5** | Team Collaboration & Quality | Modular monolith design, strict boundary interfaces, comprehensive architecture documentation (10 formal specs), 74% test coverage. |

---

## 3. Technology Stack

### Frontend
- **Framework:** React 18 with TypeScript 5
- **Build Tool:** Vite 5
- **Styling:** Tailwind CSS (Dark-first Linear/Vercel design system)
- **Editor:** Monaco Editor (`@monaco-editor/react`)
- **Visual Analytics:** Recharts
- **State Management:** Zustand
- **Icons:** Lucide React

### Backend
- **Framework:** FastAPI (Python 3.12)
- **Validation:** Pydantic V2 & Pydantic Settings
- **Persistence:** SQLAlchemy 2.0 (Async) + aiosqlite (WAL mode)
- **Logging:** Structured JSON logging via `structlog`
- **Compiler:** LLVM / Apple Clang toolchain
- **Sandbox Instrumentation:** Native C measurement harness (`sandbox/runner.c`)
- **Machine Learning:** Scikit-Learn, NumPy, Joblib

### Infrastructure & Security
- **Containerization:** Docker & Docker Compose
- **Sandboxing:** Seccomp syscall filter profile, Linux cgroups v2
- **Testing:** Pytest, Pytest-Asyncio, Pytest-Cov (18 test suites, 74% coverage)
- **Linting:** Ruff (0 lint errors)

---

## 4. Architecture Specifications

Comprehensive architectural blueprints and specifications are available in the repository root:

1. [PROJECT_VISION.md](PROJECT_VISION.md) — Strategic vision, core objectives, and user personas.
2. [REQUIREMENTS_SPECIFICATION.md](REQUIREMENTS_SPECIFICATION.md) — Functional and non-functional requirements mapped to CO1–CO5.
3. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) — C4 model diagrams, data flows, and subsystem boundaries.
4. [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) — Component deep-dives and native C measurement harness anatomy.
5. [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) — Entity-relationship diagrams and schema DDL.
6. [API_SPECIFICATION.md](API_SPECIFICATION.md) — OpenAPI 3.1 REST contracts.
7. [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) — 6-phase engineering roadmap with acceptance criteria.
8. [TESTING_STRATEGY.md](TESTING_STRATEGY.md) — Test pyramid, adversary test scenarios, and regression thresholds.
9. [SECURITY_DESIGN.md](SECURITY_DESIGN.md) — Seccomp profiles, cgroups constraints, and input sanitization.
10. [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md) — Linear/Vercel dark theme tokens and typographic rules.

---

## 5. Quickstart & Local Execution

### Prerequisites
- Python 3.12+
- Node.js 20+ & npm
- LLVM / Clang compiler toolchain installed (`clang --version`)
- Docker & Docker Compose (optional for containerized run)

### Method A: Local Development Run

#### 1. Start Backend API
```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations / initialization & start API server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The interactive Swagger API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

#### 2. Start Frontend Application
```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies (if not already installed)
npm install

# Start development server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### Method B: Docker Compose Deployment

To build and run the entire multi-container platform (Backend, Frontend, and Sandbox environment):
```bash
docker compose up --build
```
- **Web UI:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 6. Verification & Automated Test Suites

### Running Backend Tests & Code Coverage
```bash
cd backend
python3 -m pytest tests/ -v --cov=app --cov-report=term-missing
```
**Test Results:**
- **18 / 18 tests passing** (unit tests, security flag rejection, statistical variance, ML recommendation flow, Pareto frontier, regression detection, report generation).
- **Backend Code Coverage:** **74%**

### Running Linting & Style Verification
```bash
cd backend
python3 -m ruff check app/ tests/
```
**Result:** Clean (0 errors).

### Running Frontend Production Build & TypeScript Verification
```bash
cd frontend
npm run build
```
**Result:** 0 TypeScript errors, bundle generated in `dist/`.

---

## 7. Sample Program Walkthrough for Evaluators

1. Open CompilerX at `http://localhost:5173`.
2. Select or create a project (e.g. `Matrix Multiplication Benchmark`).
3. Add a source file `matrix.c`:
```c
#include <stdio.h>
#include <stdlib.h>

#define N 150

int main() {
    int A[N][N], B[N][N], C[N][N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            A[i][j] = (i + j) % 100;
            B[i][j] = (i * j) % 100;
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
    printf("Result checksum: %d\\n", C[N-1][N-1]);
    return 0;
}
```
4. **Compile:** Click **Compile** with `-O0`, `-O1`, `-O2`, or `-O3`. View stdout/stderr and captured binary byte size.
5. **AI Recommendation:** Click the **AI Optimizer** tab and click **Predict Optimal Flag**. The model inspects the loop depth ($3$), loop count ($4$), and array subscripts ($7$) to recommend `-O3` with decision reasoning and confidence.
6. **Benchmark Suite:** Switch to the **Benchmarking** tab, select `5x` iterations, and click **Run Full Suite (-O0 to -O3)**.
7. **Inspect Analytics:** View the interactive bar chart showing execution times with standard deviation bars, the max speedup factor, and the Pareto-optimal frontier table.
8. **Export Audit Report:** Click **Export Report** to view and download Markdown and JSON performance audit summaries.

---

## 8. License

Developed for academic evaluation under the Apache 2.0 License.
Department of Computer Science & Engineering, KL University.

