"""
SHAP Explainability Module
==========================
Explains why the model made a specific phishing/legitimate prediction.
"""

import shap
import numpy as np
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.features.extractor import extract_features, get_feature_names


def get_top_features(url: str, model, n_top: int = 5) -> list:
    """
    Returns the top N features that most influenced the prediction for this URL.
    """
    feature_names = get_feature_names()
    features = extract_features(url)
    feature_values = [features.get(name, 0) for name in feature_names]

    X = pd.DataFrame([feature_values], columns=feature_names)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    single_shap = shap_values[0]

    contributions = []
    for name, val, shap_val in zip(feature_names, feature_values, single_shap):
        contributions.append({
            'feature': name,
            'value': float(val),
            'impact': float(shap_val),
            'direction': 'phishing' if shap_val > 0 else 'legitimate'
        })

    contributions.sort(key=lambda x: abs(x['impact']), reverse=True)
    return contributions[:n_top]