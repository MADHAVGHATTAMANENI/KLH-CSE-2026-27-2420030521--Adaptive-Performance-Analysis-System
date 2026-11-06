from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class OptimizationLevel(str, Enum):
    O0 = "-O0"
    O1 = "-O1"
    O2 = "-O2"
    O3 = "-O3"
    OS = "-Os"
    OZ = "-Oz"


class CompileRequest(BaseModel):
    optimization_level: OptimizationLevel = Field(
        default=OptimizationLevel.O0,
        description="Target Clang optimization level (-O0, -O1, -O2, -O3, -Os, -Oz)",
    )
    compiler_flags: List[str] = Field(
        default_factory=list,
        description="Auxiliary compiler flags (must be in whitelist, e.g. ['-Wall', '-ffast-math'])",
    )


class CompileResponse(BaseModel):
    id: str
    source_file_id: str
    optimization_level: str
    compiler_flags: List[str]
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    compilation_time_ms: float
    binary_size_bytes: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompilationHistoryItem(BaseModel):
    id: str
    optimization_level: str
    compiler_flags: List[str]
    success: bool
    exit_code: int
    compilation_time_ms: float
    binary_size_bytes: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
