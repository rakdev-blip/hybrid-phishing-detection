# Hybrid ML Framework for Multi-Modal Phishing Detection
### With Browser Extension and Explainable AI

## Project Overview

This project is a phishing detection system that uses machine learning to classify
websites as safe or phishing in real time. It analyzes the URL and extracts numerical
features that indicate whether the site is trustworthy.

**Why this matters:** Phishing remains one of the most dangerous cybersecurity threats.
Traditional blacklists fail against newly created phishing sites created daily.

**What was built:**
- A machine learning model trained on 235,795 real URLs from the PhiUSIIL dataset
- A web interface where anyone can check a URL
- A browser extension that checks the current page automatically
- Explainable AI output using SHAP showing why the model made its decision

---

## Dataset

**PhiUSIIL Phishing URL Dataset** — UCI Machine Learning Repository
- 134,850 legitimate URLs (label = 0 in our system)
- 100,945 phishing URLs (label = 1 in our system)
- **Download:** https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset
- Place the downloaded file at: `data/raw/PhiUSIIL_Phishing_URL_Dataset.csv`

**Important note about labels:** The original PhiUSIIL dataset uses 1 = legitimate
and 0 = phishing. Our code expects 1 = phishing and 0 = legitimate. The feature
engineering notebook handles this flip automatically in Cell 4.

---

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Git
- VS Code
- Google Chrome (for the browser extension)

### Step 1 — Clone the repository
```bash
cd ~/Documents
git clone https://github.com/YOUR_USERNAME/hybrid-phishing-detection.git
cd hybrid-phishing-detection
```

### Step 2 — Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
source venv/Scripts/activate  # Windows
```

You must see `(venv)` in your terminal prompt before continuing.

### Step 3 — Install all required packages
```bash
pip install -r requirements.txt
```

### Step 4 — Download the dataset
Download from the UCI link above and place the file at:
`data/raw/PhiUSIIL_Phishing_URL_Dataset.csv`

### Step 5 — Run the preprocessing notebook
Open VS Code, open the project folder, then open and run all cells in:
`notebooks/01_data_preprocessing.ipynb`

Wait for all cells to finish before continuing.

### Step 6 — Run the feature engineering notebook
Open and run all cells in:
`notebooks/01b_feature_engineering.ipynb`

**This step takes 20 to 30 minutes** for the full 235,795 URLs.
Do not close VS Code while it is running.
Cell 4 automatically flips the labels to match the code's expectations.

### Step 7 — Train the models
```bash
python src/models/train_model.py
```

Wait for it to finish. You will see F1 scores for both models printed at the end.

### Step 8 — Start the API server (leave this running)
```bash
uvicorn src.api.app:app --reload --port 8000
```

Test it is working: open `http://localhost:8000/health` in your browser.
You should see: `{"status":"ok","model_loaded":true}`

### Step 9 — Start the Streamlit app (open a new terminal for this)
```bash
source venv/bin/activate
streamlit run streamlit_app/app.py
```

Your browser opens automatically at `http://localhost:8501`

### Step 10 — Load the browser extension (optional)
1. Open Chrome and go to `chrome://extensions/`
2. Turn on **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Select the `extension/` folder from this project
5. The shield icon appears in your Chrome toolbar
6. Make sure the API server is running, then click the icon on any webpage

---

## How to Use

**Web app:**
Go to `http://localhost:8501`, type any URL in the input field, click Analyze.
You will see whether the URL is phishing or legitimate, a confidence percentage,
and the top SHAP features that influenced the decision.

**Browser extension:**
Navigate to any website in Chrome, click the shield icon in the toolbar.
The extension automatically checks the current page.

**API directly:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

---

## Running Tests
```bash
pytest tests/ -v
```

Expected: all tests pass or are skipped with a clear reason.
The model-dependent tests are skipped if the model has not been trained yet.

---

## Model Performance

| Model | Accuracy | Precision | Recall | F1 Score |
|-------|----------|-----------|--------|----------|
| Random Forest | 0.9980 | 0.9996 | 0.9958 | 0.9977 |
| XGBoost | 0.9981 | 0.9996 | 0.9959 | 0.9977 |

*(Fill these in from the output of notebooks/02_model_training.ipynb)*

---

## Project Structure

```
hybrid-phishing-detection/
├── README.md                        ← this file
├── requirements.txt                 ← all Python packages needed
├── .gitignore                       ← files Git does not track
├── data/
│   ├── raw/                         ← original downloaded dataset (not committed)
│   ├── processed/                   ← cleaned and feature-extracted CSVs (not committed)
│   └── sample_urls/
│       └── test_urls.csv            ← small list of test URLs for demos
├── notebooks/
│   ├── 01_data_preprocessing.ipynb  ← cleans the raw dataset
│   ├── 01b_feature_engineering.ipynb← extracts features and flips labels
│   ├── 02_model_training.ipynb      ← trains and compares models
│   └── 03_explainability.ipynb      ← SHAP analysis and plots
├── src/
│   ├── features/
│   │   └── extractor.py             ← extracts 18 numerical features from a URL
│   ├── models/
│   │   ├── train_model.py           ← standalone training script
│   │   ├── predict.py               ← prediction function used by the app and API
│   │   └── explain.py               ← SHAP top feature explanation
│   └── api/
│       └── app.py                   ← FastAPI backend server
├── streamlit_app/
│   └── app.py                       ← Streamlit web interface
├── extension/
│   ├── manifest.json                ← Chrome extension configuration
│   ├── popup.html                   ← extension popup layout
│   ├── popup.js                     ← extension logic
│   ├── background.js                ← extension background worker
│   └── style.css                    ← extension styling
├── tests/
│   ├── test_features.py             ← tests for feature extractor
│   ├── test_model.py                ← tests for prediction module
│   └── test_api.py                  ← tests for FastAPI endpoints
├── docs/
│   ├── screenshots/                 ← screenshots for report
│   └── demo_script.md               ← step by step demo instructions
└── models/
    └── saved_models/                ← trained model files (not committed)
```

---

## Known Issues and Notes

- The PhiUSIIL dataset labels are inverted compared to standard convention.
  Label flipping is handled automatically in `notebooks/01b_feature_engineering.ipynb` Cell 4.
- The `on_event` startup warning from FastAPI is a deprecation notice only and does
  not affect functionality.
- Model `.pkl` files are not committed to GitHub. Run `python src/models/train_model.py`
  after cloning to generate them locally.
- The browser extension requires the API server to be running locally on port 8000.

---

## Technologies Used

| Tool | Purpose |
|------|---------|
| Python 3.11 | Main programming language |
| pandas, numpy | Data processing and manipulation |
| scikit-learn | Random Forest model |
| XGBoost | XGBoost model |
| SHAP | Explainable AI feature importance |
| Streamlit | Web interface |
| FastAPI | REST API backend |
| Chrome Extension Manifest V3 | Browser component |
| pytest | Automated testing |
| Git + GitHub | Version control |

---

## References

- PhiUSIIL Phishing URL Dataset (UCI Machine Learning Repository, 2023)
- SHAP: Lundberg, S. & Lee, S.I. (2017). A unified approach to interpreting model predictions.
- XGBoost: Chen, T. & Guestrin, C. (2016). XGBoost: A scalable tree boosting system.
- Research in 2025-2026 supports browser-extension-style and SHAP-based phishing
  detection as practical real-world directions.