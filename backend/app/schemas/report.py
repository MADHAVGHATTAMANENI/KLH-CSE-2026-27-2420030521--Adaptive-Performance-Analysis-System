from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SystemEnvironmentInfo(BaseModel):
    hostname: str
    platform: str
    architecture: str
    cpu_cores: int
    compiler_path: str
    compiler_version: str


class BenchmarkReportData(BaseModel):
    report_id: str
    generated_at: str
    project_id: str
    source_file_id: str
    filename: str
    environment: SystemEnvironmentInfo
    suite_id: str
    status: str
    runs_per_level: int
    results: List[Dict[str, Any]]
    recommendation: Optional[Dict[str, Any]] = None
    analytics_summary: Dict[str, Any]

