from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.ml import (
    FeatureVector,
    ModelStatusResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.ml_service import MLService

router = APIRouter(tags=["Adaptive AI Optimization"])


@router.get(
    "/optimization/features/{file_id}",
    response_model=FeatureVector,
    summary="Extract 16D static code feature vector",
)
async def extract_features(
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    ml_service = MLService(db)
    return await ml_service.extract_file_features(file_id)


@router.post(
    "/files/{file_id}/recommend",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get ML-driven compiler optimization recommendation",
)
async def get_recommendation(
    file_id: str,
    payload: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
):
    ml_service = MLService(db)
    return await ml_service.recommend(
        source_file_id=file_id,
        objective=payload.objective.value,
    )


@router.get(
    "/ml/model/status",
    response_model=ModelStatusResponse,
    summary="Get ML model evaluation metrics, accuracy, and confusion matrix (CO4)",
)
async def get_model_status():
    return MLService.get_model_status()


@router.post(
    "/ml/model/retrain",
    response_model=ModelStatusResponse,
    summary="Trigger model retraining on benchmark dataset (CO4)",
)
async def retrain_model(db: AsyncSession = Depends(get_db)):
    ml_service = MLService(db)
    return await ml_service.retrain_model()

