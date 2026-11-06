# CompilerX — REST API Specification (OpenAPI 3.1)
**AI-Powered Adaptive Code Optimization and Performance Analysis System**

---

| Field | Value |
|---|---|
| **Document Version** | 1.0.0 |
| **Status** | APPROVED — API Design Contract |
| **Author** | Principal Software Architect & Technical Lead |
| **Target Course** | Adaptive Software Engineering (24CI3201), KL University |
| **Base URL** | `http://localhost:8000/api/v1` |
| **Protocol** | HTTP/1.1 (JSON over REST) |
| **Last Updated** | 2026-11-06 |

---

## 1. Global API Standards & Conventions

### 1.1 Content Negotiation & Encoding
- All endpoints accept and return UTF-8 encoded JSON (`Content-Type: application/json; charset=utf-8`).
- File uploads accept either `multipart/form-data` or JSON payloads with encoded content.
- Date and time fields use strict **ISO-8601 UTC** representation (`YYYY-MM-DDTHH:MM:SS.sssZ`).
- Resource identifiers are formatted as lowercase **UUIDv4** strings.

### 1.2 Standard HTTP Status Codes

| Code | Meaning | Usage |
|---|---|---|
| `200 OK` | Request Succeeded | Read, update, or synchronous execution success. |
| `201 Created` | Resource Created | Entity creation (projects, files, compilations). |
| `202 Accepted` | Async Job Accepted | Long-running tasks (benchmark suite execution, ML retraining). |
| `204 No Content` | Deleted | Successful entity deletion with empty body. |
| `400 Bad Request` | Client Error | Malformed JSON, compilation failure, or invalid parameters. |
| `404 Not Found` | Entity Missing | Resource ID does not exist in persistence layer. |
| `413 Payload Too Large` | Size Exceeded | Source code exceeds 1 MB limit. |
| `422 Unprocessable Entity`| Validation Error | Pydantic schema validation failure or unwhitelisted compiler flag. |
| `429 Too Many Requests`| Rate Limited | Exceeded endpoint rate limit threshold. |
| `500 Internal Error` | Server Exception | Uncaught runtime error or container supervisor crash. |

### 1.3 Uniform Error Response Envelope
Every non-2xx HTTP response returns a standardized JSON error envelope:

```json
{
  "error": "STRING_ERROR_CODE",
  "message": "Human-readable explanation of failure.",
  "status_code": 400,
  "details": {},
  "timestamp": "2026-11-06T12:00:00.000Z"
}
```

---

## 2. API Endpoints Specification

### 2.1 Projects Management (`/projects`)

#### 1. Create Project
- **`POST /api/v1/projects`**
- **Description:** Initializes a new project workspace.
- **Request Body:**
```json
{
  "name": "QuickSort Performance Study",
  "description": "Comparative analysis of QuickSort with pivot variants.",
  "language": "c"
}
```
- **Response `201 Created`:**
```json
{
  "id": "e4b2d1c0-0001-4000-8000-000000000001",
  "name": "QuickSort Performance Study",
  "description": "Comparative analysis of QuickSort with pivot variants.",
  "language": "c",
  "file_count": 0,
  "created_at": "2026-11-06T12:00:00.000Z",
  "updated_at": "2026-11-06T12:00:00.000Z"
}
```

#### 2. List Projects
- **`GET /api/v1/projects`**
- **Query Parameters:**
  - `page` (integer, default: 1)
  - `page_size` (integer, default: 20, max: 100)
- **Response `200 OK`:**
```json
{
  "items": [
    {
      "id": "e4b2d1c0-0001-4000-8000-000000000001",
      "name": "QuickSort Performance Study",
      "language": "c",
      "file_count": 2,
      "updated_at": "2026-11-06T12:05:00.000Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

#### 3. Get Project Details
- **`GET /api/v1/projects/{project_id}`**
- **Response `200 OK`:** Returns project metadata along with nested array of associated `source_files`.

#### 4. Delete Project
- **`DELETE /api/v1/projects/{project_id}`**
- **Response `204 No Content`** (cascades deletion to all files, compilations, and benchmarks).

---

### 2.2 Source File Operations (`/files`)

#### 1. Create Source File
- **`POST /api/v1/projects/{project_id}/files`**
- **Request Body:**
```json
{
  "filename": "quicksort.c",
  "content": "#include <stdio.h>\nvoid swap(int* a, int* b) { ... }\nint main() { ... }"
}
```
- **Validation Rules:**
  - `filename` must match regex: `^[a-zA-Z0-9_\-.]+\.(c|cpp)$`.
  - `content` byte length $\le 1{,}048{,}576$ (1 MB).
- **Response `201 Created`:**
```json
{
  "id": "f5a3b2c1-0002-4000-8000-000000000002",
  "project_id": "e4b2d1c0-0001-4000-8000-000000000001",
  "filename": "quicksort.c",
  "content_hash": "a4f5c6b7e8d9...",
  "size_bytes": 1420,
  "created_at": "2026-11-06T12:01:00.000Z",
  "updated_at": "2026-11-06T12:01:00.000Z"
}
```

#### 2. Get Source File Content
- **`GET /api/v1/files/{file_id}`**
- **Response `200 OK`:** Returns full source file including `content` text.

#### 3. Update Source File
- **`PUT /api/v1/files/{file_id}`**
- **Request Body:**
```json
{
  "content": "#include <stdio.h>\n// Updated algorithm\n..."
}
```
- **Response `200 OK`:** Returns updated file metadata and newly computed `content_hash`.

---

### 2.3 Compilation Engine (`/compilation`)

#### 1. Compile Source File
- **`POST /api/v1/files/{file_id}/compile`**
- **Rate Limit:** 10 requests / minute per client IP.
- **Request Body:**
```json
{
  "optimization_level": "-O2",
  "compiler_flags": ["-Wall", "-pedantic"]
}
```
- **Validation Rules:**
  - `optimization_level` must be one of: `["-O0", "-O1", "-O2", "-O3", "-Os", "-Oz"]`.
  - `compiler_flags` elements must belong to the approved security whitelist.
- **Response `201 Created` (Compilation Succeeded):**
```json
{
  "id": "c1000000-0003-4000-8000-000000000001",
  "source_file_id": "f5a3b2c1-0002-4000-8000-000000000002",
  "optimization_level": "-O2",
  "compiler_flags": ["-Wall", "-pedantic"],
  "success": true,
  "stdout": "",
  "stderr": "",
  "exit_code": 0,
  "compilation_time_ms": 142.8,
  "binary_size_bytes": 18432,
  "created_at": "2026-11-06T12:02:00.000Z"
}
```
- **Response `400 Bad Request` (Compilation Failed with Diagnostics):**
```json
{
  "error": "COMPILATION_ERROR",
  "message": "Clang exited with status 1.",
  "status_code": 400,
  "details": {
    "exit_code": 1,
    "compilation_time_ms": 68.4,
    "stderr": "quicksort.c:14:5: error: use of undeclared identifier 'temp'\n    temp = *a;\n    ^\n1 error generated.\n"
  },
  "timestamp": "2026-11-06T12:02:05.000Z"
}
```

---

### 2.4 Benchmarking Pipeline (`/benchmarks`)

#### 1. Execute Single Benchmark Run
- **`POST /api/v1/compilations/{compilation_id}/benchmark`**
- **Rate Limit:** 5 requests / minute per client IP.
- **Request Body:**
```json
{
  "num_runs": 5,
  "stdin_payload": "10000\n"
}
```
- **Response `200 OK`:**
```json
{
  "compilation_id": "c1000000-0003-4000-8000-000000000001",
  "runs": [
    {
      "run_index": 1,
      "wall_time_ms": 14.82,
      "user_cpu_time_ms": 13.90,
      "sys_cpu_time_ms": 0.82,
      "peak_memory_kb": 2412,
      "exit_code": 0
    },
    {
      "run_index": 2,
      "wall_time_ms": 14.79,
      "user_cpu_time_ms": 13.88,
      "sys_cpu_time_ms": 0.81,
      "peak_memory_kb": 2412,
      "exit_code": 0
    }
  ],
  "statistics": {
    "mean_wall_time_ms": 14.80,
    "median_wall_time_ms": 14.79,
    "stddev_ms": 0.021,
    "min_ms": 14.79,
    "max_ms": 14.82,
    "variance_cv_percent": 0.14,
    "has_high_variance": false
  }
}
```

#### 2. Execute Automated Multi-Optimization Benchmark Suite
- **`POST /api/v1/files/{file_id}/benchmark-suite`**
- **Description:** Triggers asynchronous compilation and benchmarking across `-O0`, `-O1`, `-O2`, and `-O3`.
- **Request Body:**
```json
{
  "runs_per_level": 5,
  "stdin_payload": "5000\n"
}
```
- **Response `202 Accepted`:**
```json
{
  "suite_id": "s1000000-0004-4000-8000-000000000001",
  "status": "RUNNING",
  "message": "Benchmark suite initiated across -O0, -O1, -O2, -O3.",
  "estimated_duration_s": 6
}
```

#### 3. Poll Benchmark Suite Status & Results
- **`GET /api/v1/benchmarks/suite/{suite_id}`**
- **Response `200 OK` (when Completed):**
```json
{
  "suite_id": "s1000000-0004-4000-8000-000000000001",
  "status": "COMPLETED",
  "source_file_id": "f5a3b2c1-0002-4000-8000-000000000002",
  "started_at": "2026-11-06T12:03:00.000Z",
  "completed_at": "2026-11-06T12:03:06.400Z",
  "results": [
    {
      "optimization_level": "-O0",
      "mean_time_ms": 82.4,
      "median_time_ms": 82.1,
      "stddev_time_ms": 0.8,
      "speedup_vs_o0": 1.0,
      "peak_memory_kb": 2400,
      "binary_size_bytes": 16400,
      "has_high_variance": false
    },
    {
      "optimization_level": "-O1",
      "mean_time_ms": 34.2,
      "median_time_ms": 34.1,
      "stddev_time_ms": 0.4,
      "speedup_vs_o0": 2.41,
      "peak_memory_kb": 2410,
      "binary_size_bytes": 18200,
      "has_high_variance": false
    },
    {
      "optimization_level": "-O2",
      "mean_time_ms": 22.8,
      "median_time_ms": 22.7,
      "stddev_time_ms": 0.3,
      "speedup_vs_o0": 3.61,
      "peak_memory_kb": 2420,
      "binary_size_bytes": 19400,
      "has_high_variance": false
    },
    {
      "optimization_level": "-O3",
      "mean_time_ms": 18.5,
      "median_time_ms": 18.4,
      "stddev_time_ms": 0.2,
      "speedup_vs_o0": 4.45,
      "peak_memory_kb": 2428,
      "binary_size_bytes": 22100,
      "has_high_variance": false
    }
  ]
}
```

---

### 2.5 Adaptive AI Optimization Engine (`/optimization`)

#### 1. Extract Code Feature Vector
- **`GET /api/v1/optimization/features/{file_id}`**
- **Response `200 OK`:**
```json
{
  "source_file_id": "f5a3b2c1-0002-4000-8000-000000000002",
  "feature_vector": {
    "lines_of_code": 88,
    "function_count": 4,
    "cyclomatic_complexity": 9,
    "loop_count": 2,
    "max_loop_nesting_depth": 2,
    "integer_arithmetic_ops": 44,
    "float_arithmetic_ops": 0,
    "pointer_dereferences": 16,
    "array_subscript_ops": 32,
    "branch_count": 8,
    "recursive_call_count": 2,
    "bitwise_ops": 0,
    "memory_allocation_ops": 0,
    "math_library_calls": 0,
    "global_variable_count": 0,
    "arithmetic_to_branch_ratio": 4.88
  }
}
```

#### 2. Get Optimization Recommendation
- **`POST /api/v1/files/{file_id}/recommend`**
- **Request Body:**
```json
{
  "objective": "SPEED"
}
```
- **Response `200 OK`:**
```json
{
  "id": "rec-0001-4000-8000-000000000001",
  "source_file_id": "f5a3b2c1-0002-4000-8000-000000000002",
  "recommended_level": "-O3",
  "confidence_score": 0.865,
  "objective": "SPEED",
  "explanation": "Recommended -O3 (Confidence: 86.5%). Code analysis shows a high arithmetic-to-branch ratio (4.88) combined with nested array traversals. Aggressive Clang inlining and loop transformations are predicted to yield maximum throughput.",
  "top_influencing_features": [
    {"feature": "arithmetic_to_branch_ratio", "importance": 0.28},
    {"feature": "max_loop_nesting_depth", "importance": 0.22},
    {"feature": "array_subscript_ops", "importance": 0.16}
  ],
  "created_at": "2026-11-06T12:04:00.000Z"
}
```

#### 3. Inspect ML Model Performance Metrics (**CO4**)
- **`GET /api/v1/ml/model/status`**
- **Response `200 OK`:**
```json
{
  "model_version": "v1.0.0-rf100",
  "training_samples": 200,
  "accuracy": 0.825,
  "f1_macro": 0.812,
  "confusion_matrix": [
    [18, 2, 0, 0],
    [1, 16, 3, 0],
    [0, 2, 19, 4],
    [0, 0, 3, 22]
  ],
  "labels": ["-O0", "-O1", "-O2", "-O3"],
  "last_trained_at": "2026-11-06T10:00:00.000Z"
}
```

#### 4. Trigger Model Retraining (**CO4**)
- **`POST /api/v1/ml/model/retrain`**
- **Response `202 Accepted`:** Returns tracking ID for offline background retraining.

---

### 2.6 Report Generation (`/reports`)

#### 1. Generate Audit Report
- **`POST /api/v1/projects/{project_id}/reports`**
- **Request Body:**
```json
{
  "title": "Academic Performance Evaluation — Matrix Multiplier",
  "format": "MARKDOWN",
  "suite_id": "s1000000-0004-4000-8000-000000000001"
}
```
- **Response `200 OK`:** Returns structured report record with embedded markdown payload ready for export or PDF rendering.

---

### 2.7 System & Health Endpoints (`/health`)

#### 1. System Health Check
- **`GET /api/v1/health`**
- **Response `200 OK`:**
```json
{
  "status": "HEALTHY",
  "version": "1.0.0",
  "compiler": {
    "clang_version": "Apple clang version 21.0.0 / Docker Clang 17.0.6",
    "status": "AVAILABLE"
  },
  "docker": {
    "status": "CONNECTED",
    "socket": "/var/run/docker.sock"
  },
  "ml_subsystem": {
    "status": "LOADED",
    "model_version": "v1.0.0-rf100"
  },
  "database": {
    "status": "CONNECTED",
    "engine": "sqlite"
  }
}
```

---

## 3. Pydantic v2 Schema Definitions (Python Code Contract)

The following Python schemas define the exact request and response contracts implemented in `backend/app/schemas/`:

```python
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, UUID4

# --- Enums ---
class LanguageEnum(str, Enum):
    C = "c"
    CPP = "cpp"

class OptimizationLevelEnum(str, Enum):
    O0 = "-O0"
    O1 = "-O1"
    O2 = "-O2"
    O3 = "-O3"
    OS = "-Os"
    OZ = "-Oz"

class ObjectiveEnum(str, Enum):
    SPEED = "SPEED"
    SIZE = "SIZE"
    BALANCED = "BALANCED"

class SuiteStatusEnum(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# --- Project Schemas ---
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    language: LanguageEnum = LanguageEnum.C

class ProjectResponse(BaseModel):
    id: UUID4
    name: str
    description: Optional[str]
    language: LanguageEnum
    file_count: int = 0
    created_at: datetime
    updated_at: datetime

# --- Source File Schemas ---
class SourceFileCreate(BaseModel):
    filename: str = Field(..., pattern=r"^[a-zA-Z0-9_\-.]+\.(c|cpp)$")
    content: str = Field(..., max_length=1_048_576)

class SourceFileResponse(BaseModel):
    id: UUID4
    project_id: UUID4
    filename: str
    content_hash: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime

# --- Compilation Schemas ---
class CompileRequest(BaseModel):
    optimization_level: OptimizationLevelEnum = OptimizationLevelEnum.O0
    compiler_flags: List[str] = Field(default_factory=list)

class CompileResponse(BaseModel):
    id: UUID4
    source_file_id: UUID4
    optimization_level: OptimizationLevelEnum
    compiler_flags: List[str]
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    compilation_time_ms: float
    binary_size_bytes: Optional[int]
    created_at: datetime

# --- Benchmarking Schemas ---
class BenchmarkSuiteRequest(BaseModel):
    runs_per_level: int = Field(default=5, ge=3, le=10)
    stdin_payload: Optional[str] = None

class SuiteResultItem(BaseModel):
    optimization_level: OptimizationLevelEnum
    mean_time_ms: float
    median_time_ms: float
    stddev_time_ms: float
    min_time_ms: float
    max_time_ms: float
    variance_cv_percent: float
    speedup_vs_o0: float
    peak_memory_kb: int
    binary_size_bytes: int
    has_high_variance: bool

class BenchmarkSuiteResponse(BaseModel):
    suite_id: UUID4
    status: SuiteStatusEnum
    source_file_id: UUID4
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    results: List[SuiteResultItem] = Field(default_factory=list)

# --- ML Recommendation Schemas ---
class FeatureVector(BaseModel):
    lines_of_code: int
    function_count: int
    cyclomatic_complexity: int
    loop_count: int
    max_loop_nesting_depth: int
    integer_arithmetic_ops: int
    float_arithmetic_ops: int
    pointer_dereferences: int
    array_subscript_ops: int
    branch_count: int
    recursive_call_count: int
    bitwise_ops: int
    memory_allocation_ops: int
    math_library_calls: int
    global_variable_count: int
    arithmetic_to_branch_ratio: float

class RecommendationRequest(BaseModel):
    objective: ObjectiveEnum = ObjectiveEnum.SPEED

class RecommendationResponse(BaseModel):
    id: UUID4
    source_file_id: UUID4
    recommended_level: OptimizationLevelEnum
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    objective: ObjectiveEnum
    explanation: str
    features_extracted: FeatureVector
    created_at: datetime
```

---

## 4. Rate Limiting & CORS Configuration

### 4.1 Rate Limiting Architecture
Enforced via `slowapi` utilizing the client's IP address (`get_remote_address`):
- **Default Global Limiter:** 60 requests/minute
- **Compilation Limit:** 10 requests/minute
- **Benchmark Execution Limit:** 5 requests/minute
- **Violation Response:** HTTP `429 Too Many Requests` with `Retry-After` header.

### 4.2 Cross-Origin Resource Sharing (CORS) Configuration
FastAPI `CORSMiddleware` is configured with strict developer and production origin controls:
```python
origins = [
    "http://localhost:5173",  # Vite Dev Server
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Production Docker Nginx
    "http://127.0.0.1:3000"
]
```
- Allowed methods: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`.
- Allowed headers: `Content-Type`, `Authorization`, `X-Request-ID`.

---

*This document defines the complete API specification and contract for CompilerX.*

