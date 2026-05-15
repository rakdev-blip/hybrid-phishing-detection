"""
Prediction Module
=================
Loads a trained model and predicts whether a URL is phishing.
"""

import joblib
import json
import numpy as np
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.features.extractor import extract_features, get_feature_names


def load_model(model_type: str = 'xgboost'):
    model_files = {
        'xgboost': 'models/saved_models/xgboost_model.pkl',
        'random_forest': 'models/saved_models/random_forest_model.pkl'
    }
    if model_type not in model_files:
        raise ValueError(f"Unknown model type: {model_type}")

    path = model_files[model_type]
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model not found at: {path}\n"
            f"Run: python src/models/train_model.py"
        )
    return joblib.load(path)


def predict_url(url: str, model=None, model_type: str = 'xgboost') -> dict:
    if model is None:
        model = load_model(model_type)

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    features = extract_features(url)
    feature_names = get_feature_names()
    feature_values = [features.get(name, 0) for name in feature_names]
    X = np.array(feature_values).reshape(1, -1)

    prediction_int = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    confidence = float(probabilities[1])

    return {
        'prediction': 'phishing' if prediction_int == 1 else 'legitimate',
        'confidence': confidence,
        'features': features
    }