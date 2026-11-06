from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ParetoPoint(BaseModel):
    optimization_level: str
    speedup: float
    binary_size_bytes: int
    runtime_ms: float
    is_pareto_optimal: bool

    model_config = ConfigDict(from_attributes=True)


class RegressionAlert(BaseModel):
    level: str
    comparison_level: str
    slowdown_factor: float
    reason: str


class SuiteAnalyticsResponse(BaseModel):
    suite_id: str
    source_file_id: str
    optimal_for_speed: str
    optimal_for_size: str
    max_speedup: float
    max_size_reduction_pct: float
    has_regression: bool
    regressions: List[RegressionAlert]
    pareto_frontier: List[ParetoPoint]
    overall_efficiency_score: float


class FileAnalyticsOverview(BaseModel):
    source_file_id: str
    filename: str
    total_suites_run: int
    latest_suite_id: Optional[str]
    best_speedup_observed: float
    best_level: Optional[str]
    recent_regression_detected: bool
