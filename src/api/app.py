"""
FastAPI Backend Server
======================
How to start this server:
    Open a terminal in the project root
    Make sure (venv) is active
    Run: uvicorn src.api.app:app --reload --port 8000

Then visit http://localhost:8000/docs to test endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from src.models.predict import predict_url, load_model
from src.models.explain import get_top_features

app = FastAPI(
    title="Phishing Detection API",
    description="Hybrid ML-based phishing URL detection with SHAP explainability",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None


@app.on_event("startup")
async def load_model_on_startup():
    global model
    try:
        model = load_model('xgboost')
        print("Model loaded successfully. Server is ready.")
    except FileNotFoundError as e:
        print(f"WARNING: Could not load model: {e}")
        print("Run python src/models/train_model.py first.")


class URLRequest(BaseModel):
    url: str


@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
async def predict(request: URLRequest):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run: python src/models/train_model.py"
        )

    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    try:
        result = predict_url(url, model=model)
        top_features = get_top_features(url, model, n_top=5)
        return {
            "url": url,
            "prediction": result['prediction'],
            "confidence": round(result['confidence'], 4),
            "top_features": top_features
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")