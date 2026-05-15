"""
Model Training Script
=====================
Run this from the project root with:
    python src/models/train_model.py
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
import xgboost as xgb
import joblib
import json
import os


def main():
    print("=" * 50)
    print("Phishing Detection Model Trainer")
    print("=" * 50)

    data_path = 'data/processed/features_dataset.csv'
    if not os.path.exists(data_path):
        print(f"ERROR: Dataset not found at {data_path}")
        print("Run notebooks/01_data_preprocessing.ipynb and 01b_feature_engineering.ipynb first.")
        return

    print(f"\nLoading dataset...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows")

    X = df.drop('label', axis=1)
    y = df['label']
    feature_names = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training: {len(X_train)} | Testing: {len(X_test)}")

    print("\nTraining Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=20, random_state=42, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_f1 = f1_score(y_test, rf.predict(X_test))
    print(f"Random Forest F1: {rf_f1:.4f}")

    print("\nTraining XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        eval_metric='logloss', random_state=42, n_jobs=-1
    )
    xgb_model.fit(X_train, y_train, verbose=False)
    xgb_f1 = f1_score(y_test, xgb_model.predict(X_test))
    print(f"XGBoost F1: {xgb_f1:.4f}")

    os.makedirs('models/saved_models', exist_ok=True)
    joblib.dump(rf, 'models/saved_models/random_forest_model.pkl')
    joblib.dump(xgb_model, 'models/saved_models/xgboost_model.pkl')
    with open('models/saved_models/feature_names.json', 'w') as f:
        json.dump(feature_names, f)

    print("\nAll models saved.")
    best = 'XGBoost' if xgb_f1 > rf_f1 else 'Random Forest'
    print(f"Recommended model: {best}")


if __name__ == "__main__":
    main()