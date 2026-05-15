# Demo Script

## Before the demo — setup checklist

Run through this list a few minutes before presenting:

- [ ] API is running in Terminal 1:
      `uvicorn src.api.app:app --reload --port 8000`
- [ ] Streamlit is running in Terminal 2:
      `streamlit run streamlit_app/app.py`
- [ ] Browser is open at http://localhost:8501
- [ ] Chrome extension is loaded at chrome://extensions/
- [ ] notebooks/02_model_training.ipynb is open in VS Code
- [ ] notebooks/03_explainability.ipynb is open in VS Code

---

## Demo flow (total approximately 6-7 minutes)

### Section 1 — Introduce the problem (1 minute)

Say this:
"Phishing websites trick users into revealing passwords and banking credentials.
Traditional blacklists fail against the thousands of new phishing domains created
every day. I built a system that uses machine learning trained on 235,795 real URLs
to detect phishing in real time — and it explains exactly why it made each decision."

### Section 2 — Show the dataset (30 seconds)

Open notebooks/01_data_preprocessing.ipynb in VS Code.
Show the cells that display the dataset shape and label distribution.
Say: "This is the PhiUSIIL dataset from UCI — a real publicly available research
dataset containing 134,850 legitimate URLs and 100,945 phishing URLs."

### Section 3 — Show the Streamlit app (2-3 minutes)

Switch to the browser tab with http://localhost:8501

Test 1 — Legitimate URL:
- Type `https://www.google.com` in the input field
- Click Analyze This URL
- Show the green SAFE result and the confidence score
- Scroll down to the SHAP explanation section

Test 2 — Phishing-pattern URL:
- Type `http://paypa1-login.secure-account-verify.com`
- Click Analyze This URL
- Show the red WARNING result
- Point to the SHAP explanation and say:
  "The model does not just say it is phishing — it tells us exactly why.
  The high URL length, missing HTTPS, and suspicious keywords like login
  all pushed the prediction toward phishing."

### Section 4 — Show the browser extension (1 minute)

Switch to Chrome with the extension loaded.
Navigate to https://www.google.com
Click the shield icon in the Chrome toolbar.
Show the SAFE result in the popup with the confidence percentage.
Say: "This is how it works in a real browser — checking every page as you browse."

### Section 5 — Show model comparison (30 seconds)

Open notebooks/02_model_training.ipynb in VS Code.
Show the model comparison table cell and its output.
Say: "I compared two models — Random Forest and XGBoost.
XGBoost performed slightly better with an F1 score of [your number]."

### Section 6 — Show SHAP explainability (1 minute)

Open notebooks/03_explainability.ipynb in VS Code.
Show the global feature importance bar chart.
Say: "This is the global view — across all tested URLs, these are the features
that matter most for detecting phishing overall."
Show the waterfall plot for one URL.
Say: "This is the local view — for this specific URL, here is exactly what
pushed the prediction in each direction."

---

## Key points to emphasize throughout

1. Real data: 235,795 URLs from a real research dataset
2. Hybrid approach: two models trained and compared, not just one
3. Explainability: the system does not just say yes or no, it shows why
4. Practical components: works as a web app and as a browser extension concept