import json
import os
import time
from typing import Dict
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from app.ml.dataset import generate_extended_dataset
from app.ml.features import CodeFeatureExtractor


MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, "model.joblib")
METRICS_FILE = os.path.join(MODEL_DIR, "metrics.json")


def train_recommendation_model() -> Dict:
    """
    Trains and evaluates the Random Forest recommendation model on the benchmark corpus.
    Saves the serialized model artifact and evaluation metrics snapshot.
    """
    corpus = generate_extended_dataset()
    start_time = time.perf_counter()

    feature_matrix = []
    labels = []

    for name, code, speed_label, size_label in corpus:
        feats = CodeFeatureExtractor.extract_features(code)
        feature_matrix.append(list(feats.values()))
        labels.append(speed_label)

    X = np.array(feature_matrix)
    y = np.array(labels)

    feature_names = list(CodeFeatureExtractor.extract_features("int main(){}").keys())

    # Stratified or standard train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y if len(set(y)) > 1 else None
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=2,
        random_state=42,
    )
    clf.fit(X_train, y_train)

    train_duration_ms = (time.perf_counter() - start_time) * 1000.0

    # Predictions & Evaluations
    y_pred = clf.predict(X_test)
    accuracy = float(np.mean(y_pred == y_test))
    
    unique_labels = sorted(list(set(y)))
    cm = confusion_matrix(y_test, y_pred, labels=unique_labels).tolist()
    report = classification_report(y_test, y_pred, labels=unique_labels, output_dict=True, zero_division=0)

    # Feature Importance Mapping
    importances = {
        name: round(float(imp), 4)
        for name, imp in zip(feature_names, clf.feature_importances_)
    }
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))

    metrics = {
        "model_version": "v1.0.0-rf100",
        "training_samples": len(X),
        "test_samples": len(X_test),
        "accuracy": round(accuracy, 4),
        "f1_macro": round(report.get("macro avg", {}).get("f1-score", 0.0), 4),
        "confusion_matrix": cm,
        "labels": unique_labels,
        "feature_importances": sorted_importances,
        "training_duration_ms": round(train_duration_ms, 2),
    }

    # Persist model and metrics
    joblib.dump(clf, MODEL_FILE)
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    results = train_recommendation_model()
    print("Model Training Completed Successfully!")
    print(f"Accuracy: {results['accuracy'] * 100:.1f}%")
    print(f"Top Features: {list(results['feature_importances'].keys())[:3]}")
