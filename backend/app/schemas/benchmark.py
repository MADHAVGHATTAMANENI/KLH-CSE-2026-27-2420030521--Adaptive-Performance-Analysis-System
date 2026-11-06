from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SuiteStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BenchmarkRunRequest(BaseModel):
    num_runs: int = Field(default=5, ge=1, le=20, description="Repetitions count")
    stdin_payload: Optional[str] = Field(None, max_length=65536, description="Input string piped to stdin")


class BenchmarkRunItem(BaseModel):
    run_index: int
    wall_time_ms: float
    user_cpu_time_ms: float
    sys_cpu_time_ms: float
    peak_memory_kb: int
    exit_code: int

    model_config = ConfigDict(from_attributes=True)


class BenchmarkStatistics(BaseModel):
    mean_wall_time_ms: float
    median_wall_time_ms: float
    stddev_ms: float
    min_ms: float
    max_ms: float
    variance_cv_percent: float
    has_high_variance: bool


class BenchmarkRunResponse(BaseModel):
    compilation_id: str
    runs: List[BenchmarkRunItem]
    statistics: BenchmarkStatistics


class BenchmarkSuiteRequest(BaseModel):
    runs_per_level: int = Field(default=5, ge=3, le=10, description="Repetitions per optimization level")
    stdin_payload: Optional[str] = Field(None, max_length=65536, description="Input string piped to stdin")


class SuiteResultItem(BaseModel):
    optimization_level: str
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

    model_config = ConfigDict(from_attributes=True)


class BenchmarkSuiteResponse(BaseModel):
    suite_id: str
    source_file_id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    results: List[SuiteResultItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
