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

# Permanent whitelist of globally trusted domains
# These domains bypass the ML model entirely and always return legitimate
# Add any domain here that you know is legitimate but gets false positives
TRUSTED_DOMAIN_WHITELIST = {
    'google.com', 'www.google.com',
    'github.com', 'www.github.com',
    'youtube.com', 'www.youtube.com',
    'wikipedia.org', 'www.wikipedia.org', 'en.wikipedia.org',
    'facebook.com', 'www.facebook.com',
    'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
    'instagram.com', 'www.instagram.com',
    'linkedin.com', 'www.linkedin.com',
    'netflix.com', 'www.netflix.com',
    'amazon.com', 'www.amazon.com',
    'reddit.com', 'www.reddit.com',
    'microsoft.com', 'www.microsoft.com',
    'apple.com', 'www.apple.com',
    'bbc.com', 'www.bbc.com',
    'discord.com', 'www.discord.com',
    'spotify.com', 'www.spotify.com',
    'stackoverflow.com', 'www.stackoverflow.com',
    'medium.com', 'www.medium.com',
    'notion.so', 'www.notion.so',
    'canva.com', 'www.canva.com',
    'figma.com', 'www.figma.com',
    'dropbox.com', 'www.dropbox.com',
    'zoom.us', 'www.zoom.us',
    'slack.com', 'www.slack.com',
    'trello.com', 'www.trello.com',
    'atlassian.com', 'www.atlassian.com',
    'coursera.org', 'www.coursera.org',
    'udemy.com', 'www.udemy.com',
    'khanacademy.org', 'www.khanacademy.org',
}

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
    
    # Check whitelist before running the model
    # Whitelisted domains always return legitimate regardless of model output
    from urllib.parse import urlparse as _urlparse
    import tldextract as _tldextract
    _parsed = _urlparse(url)
    _hostname = _parsed.netloc.lower()
    _extracted = _tldextract.extract(url)
    _registered = (_extracted.domain + '.' + _extracted.suffix).lower()

    if _hostname in TRUSTED_DOMAIN_WHITELIST or _registered in TRUSTED_DOMAIN_WHITELIST:
        return {
            "url": url,
            "prediction": "legitimate",
            "confidence": 0.01,
            "top_features": [],
            "source": "whitelist"
        }

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