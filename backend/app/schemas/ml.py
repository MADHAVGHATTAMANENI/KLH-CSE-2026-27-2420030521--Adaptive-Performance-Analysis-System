from datetime import datetime
from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field


class OptimizationObjective(str, Enum):
    SPEED = "SPEED"
    SIZE = "SIZE"
    BALANCED = "BALANCED"


class FeatureVector(BaseModel):
    lines_of_code: float
    function_count: float
    cyclomatic_complexity: float
    loop_count: float
    max_loop_nesting_depth: float
    integer_arithmetic_ops: float
    float_arithmetic_ops: float
    pointer_dereferences: float
    array_subscript_ops: float
    branch_count: float
    recursive_call_count: float
    bitwise_ops: float
    memory_allocation_ops: float
    math_library_calls: float
    global_variable_count: float
    arithmetic_to_branch_ratio: float


class RecommendationRequest(BaseModel):
    objective: OptimizationObjective = Field(
        default=OptimizationObjective.SPEED,
        description="Optimization objective: SPEED, SIZE, or BALANCED",
    )


class InfluencingFeature(BaseModel):
    feature: str
    importance: float


class RecommendationResponse(BaseModel):
    id: str
    source_file_id: str
    recommended_level: str
    confidence_score: float
    objective: str
    explanation: str
    features_extracted: FeatureVector
    top_influencing_features: List[InfluencingFeature] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelStatusResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_version: str
    training_samples: int
    test_samples: int
    accuracy: float
    f1_macro: float
    confusion_matrix: List[List[int]]
    labels: List[str]
    feature_importances: Dict[str, float]
    training_duration_ms: float
