# CompilerX — Detailed Technical Design Document
**AI-Powered Adaptive Code Optimization and Performance Analysis System**

---

| Field | Value |
|---|---|
| **Document Version** | 1.0.0 |
| **Status** | APPROVED — Implementation Specification |
| **Author** | Principal Software Architect & Technical Lead |
| **Target Course** | Adaptive Software Engineering (24CI3201), KL University |
| **Architecture Pattern** | Three-Tier System with Modular Monolith Backend & Isolated Docker Sandbox |
| **Last Updated** | 2026-11-06 |

---

## 1. Complete Project Directory Structure

```
compilerx/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Automated linting, testing, and container build
│       └── security-scan.yml      # Trivy and static code analysis audit (CO3)
├── docker-compose.yml             # Orchestration for frontend, backend, and sandbox
├── .gitignore
├── README.md
│
├── frontend/                      # React 18 + TypeScript SPA
│   ├── public/
│   │   ├── favicon.svg
│   │   └── templates/             # Sample C/C++ benchmark files
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── layout/            # Header, Sidebar, StatusBar, ThemeToggle
│   │   │   ├── editor/            # Monaco Editor wrapper, gutter annotations
│   │   │   ├── compiler/          # Optimization controls, flag toggles, ANSI terminal
│   │   │   ├── benchmark/         # Suite runner, live progress, metric tiles
│   │   │   ├── analytics/         # Recharts speedup bar charts, size comparisons
│   │   │   ├── ml/                # Recommendation badge, feature importance view
│   │   │   ├── reports/           # Markdown report viewer, export controls
│   │   │   └── common/            # Button, Badge, Modal, Card, Toast primitives
│   │   ├── hooks/                 # Custom React hooks (useHotkeys, usePollSuite)
│   │   ├── services/              # Axios client, typed API calling functions
│   │   ├── stores/                # Zustand global stores (useEditorStore, useProjectStore)
│   │   ├── types/                 # TypeScript interfaces matching backend schemas
│   │   ├── utils/                 # Formatters (bytes, ms, ANSI parser)
│   │   ├── pages/                 # WorkspacePage, AnalyticsPage, ProjectsPage
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile                 # Multi-stage build serving static assets via Nginx
│
├── backend/                       # Python 3.12 FastAPI Modular Monolith
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── router.py      # Aggregated v1 APIRouter
│   │   │   │   ├── projects.py    # Project CRUD handlers
│   │   │   │   ├── files.py       # Source code CRUD & upload
│   │   │   │   ├── compiler.py    # Clang compilation triggers
│   │   │   │   ├── benchmark.py   # Suite runner & polling
│   │   │   │   ├── ml.py          # Recommendations & model evaluation
│   │   │   │   ├── analytics.py   # Regression detection & stats
│   │   │   │   ├── reports.py     # Markdown/JSON audit export
│   │   │   │   └── health.py      # Toolchain & container health checks
│   │   │   └── deps.py            # Database session & service dependency injection
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic Settings (.env management)
│   │   │   ├── security.py        # Flag whitelisting & token bucket limiter
│   │   │   ├── exceptions.py      # Domain exception hierarchy & HTTP handlers
│   │   │   └── logging.py         # Structlog JSON logger configuration
│   │   ├── models/                # SQLAlchemy 2.0 ORM entities
│   │   │   ├── base.py            # DeclarativeBase with UUID & timestamp mixins
│   │   │   ├── project.py
│   │   │   ├── source_file.py
│   │   │   ├── compilation.py
│   │   │   ├── benchmark.py
│   │   │   ├── recommendation.py
│   │   │   └── report.py
│   │   ├── schemas/               # Pydantic v2 validation contracts
│   │   │   ├── project.py
│   │   │   ├── source_file.py
│   │   │   ├── compilation.py
│   │   │   ├── benchmark.py
│   │   │   ├── ml.py
│   │   │   └── report.py
│   │   ├── services/              # Business domain services
│   │   │   ├── code_service.py
│   │   │   ├── compiler_service.py
│   │   │   ├── benchmark_service.py
│   │   │   ├── ml_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── report_service.py
│   │   ├── ml/                    # MLOps pipeline modules (CO4)
│   │   │   ├── features.py        # 16-dimensional AST/lexical feature extractor
│   │   │   ├── dataset.py         # 50-program synthetic benchmark corpus generator
│   │   │   ├── train.py           # Offline model training & evaluation script
│   │   │   ├── model.joblib       # Serialized Random Forest model artifact
│   │   │   └── metrics.json       # Model evaluation snapshot
│   │   ├── db/
│   │   │   └── session.py         # Async engine & sessionmaker
│   │   └── main.py                # FastAPI application factory & lifespan manager
│   ├── migrations/                # Alembic migration scripts
│   ├── tests/                     # Pytest test suite
│   │   ├── conftest.py            # Async test fixtures, SQLite in-memory DB
│   │   ├── test_code_service.py
│   │   ├── test_compiler_service.py
│   │   ├── test_benchmark_service.py
│   │   ├── test_ml_service.py
│   │   └── test_api_routes.py
│   ├── requirements.txt
│   ├── alembic.ini
│   └── Dockerfile                 # Python 3.12 slim container
│
└── sandbox/                       # Isolated Clang Execution Sandbox (CO2, CO3)
    ├── Dockerfile                 # Alpine/Ubuntu minimal image with Clang 17
    ├── seccomp.json               # Syscall filtration profile
    └── runner.c                   # Low-overhead C measurement harness
```

---

## 2. Frontend Technical Design

### 2.1 State Management Architecture

The frontend separates state into two distinct lifecycle tiers:
1. **Client/Transient UI State (Zustand):** Editor buffer, active project ID, selected optimization flags, open modal states, and dirty-status indicators.
2. **Server/Remote Cache State (TanStack Query):** Compilation history, benchmark suite results, project lists, and ML model performance metrics.

#### Zustand Editor Store Interface (`src/stores/useEditorStore.ts`):
```typescript
interface EditorState {
  activeFileId: string | null;
  filename: string;
  content: string;
  language: 'c' | 'cpp';
  isDirty: boolean;
  selectedOptLevel: '-O0' | '-O1' | '-O2' | '-O3';
  auxiliaryFlags: string[];
  
  // Actions
  setActiveFile: (file: { id: string; filename: string; content: string }) => void;
  updateContent: (newContent: string) => void;
  setOptLevel: (level: '-O0' | '-O1' | '-O2' | '-O3') => void;
  toggleFlag: (flag: string) => void;
  resetDirty: () => void;
}
```

### 2.2 Core UI Component Specifications

#### 1. CodeEditor Component (`src/components/editor/CodeEditor.tsx`)
- Encapsulates `@monaco-editor/react`.
- Subscribes to `useEditorStore`.
- On change, dispatches debounced updates to the store.
- Listens for compiler diagnostic errors and sets Monaco Editor markers (red squiggles with error messages in the gutter).
- Configures custom Monaco theme matching the dark developer-tool palette (`#0d1117` background, refined syntax tokens).

#### 2. CompilerPanel Component (`src/components/compiler/CompilerPanel.tsx`)
- Displays optimization level toggles (`-O0`, `-O1`, `-O2`, `-O3`) with visual indicators for the currently recommended level.
- Multi-select pill buttons for allowed flags (`-Wall`, `-pedantic`, `-ffast-math`).
- Primary "Compile" button with loading spinner.
- Collapsible terminal output container rendering ANSI-colored Clang outputs (`stdout`/`stderr`).

#### 3. BenchmarkRunner Component (`src/components/benchmark/BenchmarkRunner.tsx`)
- Houses the "Run Benchmark Suite" action.
- Configures iteration repetitions ($N \in [3, 10]$) and custom `stdin` test vectors.
- When triggered, initiates polling against `GET /api/v1/benchmarks/suite/{id}` using `useQuery` with `refetchInterval = 1000ms`.
- Displays real-time progress bar transitioning from `PENDING` $\to$ `RUNNING` $\to$ `COMPLETED`.

#### 4. AnalyticsDashboard Component (`src/components/analytics/AnalyticsDashboard.tsx`)
- Built using **Recharts**.
- **Execution Time Bar Chart:** Groups mean runtime across `-O0` to `-O3` with error bars indicating $\pm \sigma$ (standard deviation).
- **Speedup KPI Cards:** Calculates and highlights real speedup ($S = \frac{\mu_{O0}}{\mu_{Ox}}$).
- **Binary Size vs. Speedup Scatter/Bar:** Visualizes the tradeoff between binary bloat and execution speed.
- **Variance Warning Badge:** Emits an amber warning badge if any level shows $CV > 15\%$.

#### 5. MLRecommendationCard Component (`src/components/ml/MLRecommendationCard.tsx`)
- Fetches recommendation via `POST /api/v1/files/{id}/recommend`.
- Displays a pill badge (e.g. `Recommended: -O3` with confidence `88%`).
- Renders the generated natural-language explanation string.
- Expandable drawer displays the top-3 influential features derived from the Random Forest model.

---

## 3. Backend Technical Design

### 3.1 Application Lifespan & Dependency Injection

The FastAPI application (`app/main.py`) utilizes an asynchronous lifespan context manager to initialize the database engine, verify Docker connectivity, and load the pre-trained ML model into memory at startup:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables & connection pool
    await init_db()
    # Verify Docker Daemon connectivity
    app.state.docker_client = init_docker_client()
    # Load serialized scikit-learn model
    app.state.ml_model = load_model_artifact()
    yield
    # Shutdown: Close DB connections & clean lingering containers
    await close_db()
    app.state.docker_client.close()
```

### 3.2 Service Layer Deep Dives

#### 1. CompilerService (`app/services/compiler_service.py`)
- **Sanitization Protocol:**
  ```python
  def sanitize_flags(opt_level: str, extra_flags: list[str]) -> list[str]:
      if opt_level not in ALLOWED_OPTIMIZATION_LEVELS:
          raise InvalidFlagError(f"Optimization level {opt_level} not permitted.")
      for flag in extra_flags:
          if flag not in ALLOWED_COMPILER_FLAGS:
              raise InvalidFlagError(f"Compiler flag '{flag}' is not permitted.")
      return [opt_level] + extra_flags
  ```
- **Execution Mechanism:**
  1. Creates temporary working directory under `/tmp/compilerx_builds/{uuid}`.
  2. Writes `source.c` to disk.
  3. Dispatches compilation command to Clang within the execution sandbox via Docker SDK or local subprocess (if running in local native mode):
     ```bash
     clang -O2 -Wall -fdiagnostics-color=never -o /tmp/build/output /tmp/build/source.c
     ```
  4. Enforces 15.0s timeout deadline via `asyncio.wait_for()`.
  5. Measures compilation elapsed time via `time.perf_counter()`.
  6. Inspects generated binary size using `os.path.getsize()`.
  7. Returns populated `CompilationResult` dataclass.

#### 2. BenchmarkService (`app/services/benchmark_service.py`)
- **Isolation Harness:** Binaries are executed via the compiled C runner harness (`runner`).
- **Statistical Aggregation Algorithm:**
  Given an array of raw wall-clock execution times $T = [t_1, t_2, \dots, t_N]$:
  $$\mu = \frac{1}{N} \sum_{i=1}^N t_i$$
  $$\sigma = \sqrt{\frac{1}{N-1} \sum_{i=1}^N (t_i - \mu)^2}$$
  $$CV = \frac{\sigma}{\mu} \times 100\%$$
  $$\text{Speedup}_{Ox} = \frac{\mu_{O0}}{\mu_{Ox}}$$
- **High Variance Flagging:** If $CV > 15.0\%$, the result record sets `has_high_variance = True` to notify the frontend.

#### 3. MLService (`app/services/ml_service.py` & `app/ml/features.py`)
- **Feature Extraction Implementation:**
  The `features.py` module uses lexical regex tokenization and bracket-nesting state machines to extract 16 numeric features:
  - `max_loop_nesting_depth`: Maintains a stack of open loop scopes (`for`, `while`, `do`) and records the maximum depth reached.
  - `cyclomatic_complexity`: Counts decision keywords (`if`, `for`, `while`, `case`, `&&`, `||`, `?`) $+ 1$.
  - `arithmetic_to_branch_ratio`: Total arithmetic operators divided by branch keywords $+ 1$.
- **Model Inference:**
  ```python
  def predict_optimal_flag(features: dict, objective: str) -> PredictionResult:
      X = np.array([list(features.values())])
      probabilities = model.predict_proba(X)[0] # Shape: (4,)
      classes = model.classes_ # ['-O0', '-O1', '-O2', '-O3']
      best_idx = np.argmax(probabilities)
      return PredictionResult(
          recommended_level=classes[best_idx],
          confidence=float(probabilities[best_idx]),
          explanation=generate_explanation(features, classes[best_idx])
      )
  ```

---

## 4. Sandbox Container & Measurement Harness Design

### 4.1 Low-Overhead C Measurement Harness (`sandbox/runner.c`)

To guarantee zero Python interpreter overhead and capture pure process execution metrics, the benchmark sandbox uses a native C runner compiled directly into the container:

```c
// sandbox/runner.c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/resource.h>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <binary_path> [stdin_input]\n", argv[0]);
        return 1;
    }

    const char* binary_path = argv[1];
    const char* stdin_data = (argc > 2) ? argv[2] : "";

    int pipe_in[2];
    if (pipe(pipe_in) != 0) return 2;

    struct timespec start_time, end_time;
    struct rusage usage_start, usage_end;

    clock_gettime(CLOCK_MONOTONIC_RAW, &start_time);
    getrusage(RUSAGE_CHILDREN, &usage_start);

    pid_t pid = fork();
    if (pid == 0) {
        // Child Process
        close(pipe_in[1]);
        dup2(pipe_in[0], STDIN_FILENO);
        close(pipe_in[0]);
        
        // Execute target binary
        execl(binary_path, binary_path, NULL);
        perror("execl failed");
        exit(127);
    }

    // Parent Process
    close(pipe_in[0]);
    if (strlen(stdin_data) > 0) {
        write(pipe_in[1], stdin_data, strlen(stdin_data));
    }
    close(pipe_in[1]);

    int status;
    waitpid(pid, &status, 0);

    clock_gettime(CLOCK_MONOTONIC_RAW, &end_time);
    getrusage(RUSAGE_CHILDREN, &usage_end);

    double wall_time_ms = (end_time.tv_sec - start_time.tv_sec) * 1000.0 +
                          (end_time.tv_nsec - start_time.tv_nsec) / 1000000.0;
    
    double user_cpu_ms = (usage_end.ru_utime.tv_sec - usage_start.ru_utime.tv_sec) * 1000.0 +
                         (usage_end.ru_utime.tv_usec - usage_start.ru_utime.tv_usec) / 1000.0;
                         
    double sys_cpu_ms = (usage_end.ru_stime.tv_sec - usage_start.ru_stime.tv_sec) * 1000.0 +
                        (usage_end.ru_stime.tv_usec - usage_start.ru_stime.tv_usec) / 1000.0;

    long peak_rss_kb = usage_end.ru_maxrss;
    int exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;

    // Output formatted JSON for backend parser
    printf("{\"wall_time_ms\": %.3f, \"user_cpu_ms\": %.3f, \"sys_cpu_ms\": %.3f, \"peak_memory_kb\": %ld, \"exit_code\": %d}\n",
           wall_time_ms, user_cpu_ms, sys_cpu_ms, peak_rss_kb, exit_code);

    return 0;
}
```

### 4.2 Sandbox Container Definition (`sandbox/Dockerfile`)
```dockerfile
FROM alpine:3.19

# Install Clang 17, LLVM tools, musl libc development headers, and build tools
RUN apk add --no-cache \
    clang17 \
    llvm17 \
    musl-dev \
    gcc \
    make

# Create unprivileged runner user
RUN addgroup -S compilerx && adduser -S compilerx -G compilerx

WORKDIR /sandbox
COPY runner.c /sandbox/runner.c
RUN gcc -O2 -Wall /sandbox/runner.c -o /usr/local/bin/compilerx-runner \
    && rm /sandbox/runner.c

USER compilerx
ENTRYPOINT ["/usr/local/bin/compilerx-runner"]
```

---

## 5. Configuration Management (`app/core/config.py`)

All environment settings are validated at runtime via Pydantic Settings (`pydantic-settings`):

| Variable Name | Type | Default Value | Description |
|---|---|---|---|
| `ENVIRONMENT` | `str` | `"development"` | Mode: `"development"`, `"testing"`, `"production"`. |
| `DATABASE_URL` | `str` | `"sqlite+aiosqlite:///./data/compilerx.db"` | Async SQLAlchemy connection URI. |
| `DOCKER_SOCKET` | `str` | `"unix:///var/run/docker.sock"` | Docker daemon socket path. |
| `SANDBOX_IMAGE` | `str` | `"compilerx-sandbox:latest"` | Image tag used for ephemeral runner containers. |
| `MAX_FILE_SIZE_BYTES` | `int` | `1048576` (1 MB) | Hard limit on source code uploads. |
| `COMPILATION_TIMEOUT_SEC` | `float`| `15.0` | Maximum Clang compilation deadline. |
| `EXECUTION_TIMEOUT_SEC` | `float`| `10.0` | Maximum benchmark run wall-clock deadline. |
| `ML_MODEL_PATH` | `str` | `"app/ml/model.joblib"` | Path to serialized recommendation model artifact. |
| `CORS_ORIGINS` | `list[str]` | `["http://localhost:5173", "http://localhost:3000"]` | Whitelisted frontend web origins. |

---

## 6. Structured Logging & Observability

CompilerX uses `structlog` to output structured JSON logs, formatting each entry with:
- `timestamp`: ISO-8601 UTC.
- `level`: `INFO`, `WARNING`, `ERROR`, `DEBUG`.
- `request_id`: Traced via FastAPI middleware header `X-Request-ID`.
- `event`: Name of the architectural event (e.g., `compilation_started`, `benchmark_iteration_finished`, `ml_prediction_generated`).
- `context`: Key-value pairs (e.g., `file_id`, `optimization_level`, `elapsed_ms`).

Example output log:
```json
{
  "timestamp": "2026-11-06T12:02:00.142Z",
  "level": "info",
  "request_id": "req-9a1b-4c2d",
  "event": "compilation_finished",
  "source_file_id": "f5a3b2c1-0002-4000-8000-000000000002",
  "optimization_level": "-O2",
  "success": true,
  "compilation_time_ms": 142.8,
  "binary_size_bytes": 18432
}
```

---

*This document establishes the detailed technical design specification for the CompilerX implementation.*

