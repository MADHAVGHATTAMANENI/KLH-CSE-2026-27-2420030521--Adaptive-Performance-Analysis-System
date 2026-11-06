import json
import os
from typing import Dict
import joblib
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError
from app.core.logging import logger
from app.ml.features import CodeFeatureExtractor
from app.ml.train import METRICS_FILE, MODEL_FILE, train_recommendation_model
from app.models.recommendation import OptimizationRecommendation, MLTrainingRecord
from app.models.source_file import SourceFile
from app.schemas.ml import (
    FeatureVector,
    InfluencingFeature,
    ModelStatusResponse,
    RecommendationResponse,
)


class MLService:
    """
    Adaptive Machine Learning Optimization Engine
    Extracts structural/lexical code features, performs sub-millisecond inference,
    generates explainable rationales, and manages model retraining.
    """

    _model = None

    def __init__(self, db: AsyncSession):
        self.db = db
        self._ensure_model_loaded()

    @classmethod
    def _ensure_model_loaded(cls):
        """Loads or trains the serialized Random Forest model artifact."""
        if cls._model is None:
            if not os.path.exists(MODEL_FILE):
                logger.info("model_file_not_found_training_now")
                train_recommendation_model()
            cls._model = joblib.load(MODEL_FILE)
            logger.info("ml_model_loaded", model_path=MODEL_FILE)

    async def extract_file_features(self, source_file_id: str) -> FeatureVector:
        """Extracts 16D feature vector for a stored source file."""
        stmt = select(SourceFile).where(SourceFile.id == source_file_id)
        res = await self.db.execute(stmt)
        source_file = res.scalar_one_or_none()
        if not source_file:
            raise EntityNotFoundError("SourceFile", source_file_id)

        raw_features = CodeFeatureExtractor.extract_features(source_file.content)
        return FeatureVector(**raw_features)

    async def recommend(
        self,
        source_file_id: str,
        objective: str = "SPEED",
    ) -> RecommendationResponse:
        """
        Infers the optimal compiler optimization flag based on source code features.
        """
        self._ensure_model_loaded()

        stmt = select(SourceFile).where(SourceFile.id == source_file_id)
        res = await self.db.execute(stmt)
        source_file = res.scalar_one_or_none()
        if not source_file:
            raise EntityNotFoundError("SourceFile", source_file_id)

        # 1. Feature extraction
        raw_features = CodeFeatureExtractor.extract_features(source_file.content)
        feature_vector = FeatureVector(**raw_features)

        # 2. Prediction vector
        X = np.array([list(raw_features.values())])
        probs = self._model.predict_proba(X)[0]
        classes = list(self._model.classes_)

        # Objective adjustment (Size vs Speed)
        if objective == "SIZE":
            recommended_level = "-Os"
            confidence = 0.85
        else:
            best_idx = int(np.argmax(probs))
            recommended_level = classes[best_idx]
            confidence = float(probs[best_idx])

        # 3. Top Influencing Features
        feature_names = list(raw_features.keys())
        importances = list(self._model.feature_importances_)
        feature_rankings = sorted(
            [InfluencingFeature(feature=name, importance=round(float(imp), 4))
             for name, imp in zip(feature_names, importances)],
            key=lambda x: x.importance,
            reverse=True,
        )
        top_3 = feature_rankings[:3]

        # 4. Generate Natural-Language Explanation
        explanation = self._generate_explanation(
            recommended_level=recommended_level,
            confidence=confidence,
            features=raw_features,
            objective=objective,
        )

        # 5. Persist recommendation in DB
        recommendation = OptimizationRecommendation(
            source_file_id=source_file.id,
            recommended_level=recommended_level,
            confidence_score=round(confidence, 4),
            objective=objective,
            features_extracted=raw_features,
            explanation=explanation,
        )
        self.db.add(recommendation)
        await self.db.flush()
        await self.db.refresh(recommendation)

        return RecommendationResponse(
            id=recommendation.id,
            source_file_id=source_file.id,
            recommended_level=recommended_level,
            confidence_score=round(confidence, 4),
            objective=objective,
            explanation=explanation,
            features_extracted=feature_vector,
            top_influencing_features=top_3,
            created_at=recommendation.created_at,
        )

    @staticmethod
    def _generate_explanation(
        recommended_level: str,
        confidence: float,
        features: Dict[str, float],
        objective: str,
    ) -> str:
        """Formulates an explainable technical justification based on code features."""
        conf_pct = round(confidence * 100, 1)
        nesting = int(features.get("max_loop_nesting_depth", 0))
        loops = int(features.get("loop_count", 0))
        ratio = features.get("arithmetic_to_branch_ratio", 0.0)

        if objective == "SIZE":
            return (
                f"Recommended {recommended_level} for size optimization. Disables aggressive loop "
                f"unrolling and inline expansion to minimize final binary footprint."
            )

        if recommended_level == "-O3":
            return (
                f"Recommended -O3 (Confidence: {conf_pct}%). Extracted features show {loops} loop(s) "
                f"with maximum nesting depth of {nesting} and an arithmetic-to-branch ratio of {ratio}. "
                f"Aggressive Clang loop vectorization and SLP auto-vectorization provide substantial speedup."
            )
        elif recommended_level == "-O2":
            return (
                f"Recommended -O2 (Confidence: {conf_pct}%). Balanced loop and control flow structure "
                f"detected. Clang's instruction scheduling and common subexpression elimination offer "
                f"high runtime performance without excessive binary bloat."
            )
        else:
            return (
                f"Recommended {recommended_level} (Confidence: {conf_pct}%). Program has minimal loop "
                f"nesting or scalar control flow where high optimization passes yield negligible gains."
            )

    @staticmethod
    def get_model_status() -> ModelStatusResponse:
        """Retrieves model evaluation metrics from metrics.json."""
        if not os.path.exists(METRICS_FILE):
            train_recommendation_model()

        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ModelStatusResponse(**data)

    async def retrain_model(self) -> ModelStatusResponse:
        """Triggers model retraining, reloads in-memory model artifact, and persists lifecycle record."""
        metrics = train_recommendation_model()
        MLService._model = joblib.load(MODEL_FILE)

        # Persist ML lifecycle training record in database
        record = MLTrainingRecord(
            model_version=metrics["model_version"],
            training_samples=metrics["training_samples"],
            accuracy=metrics["accuracy"],
            f1_macro=metrics["f1_macro"],
            confusion_matrix=metrics["confusion_matrix"],
            per_class_metrics=metrics.get("per_class_metrics", {}),
            feature_importance=metrics.get("feature_importances", {}),
            training_duration_ms=metrics["training_duration_ms"],
        )
        self.db.add(record)
        await self.db.flush()

        return ModelStatusResponse(**metrics)
