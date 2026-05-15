"""
Streamlit Web Application
==========================
How to run:
    Make sure the API server is running in a separate terminal:
        uvicorn src.api.app:app --reload --port 8000
    Then in another terminal (with venv active):
        streamlit run streamlit_app/app.py
    Browser opens automatically at http://localhost:8501
"""

import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Phishing Detector",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

API_URL = "http://localhost:8000"

st.title("🛡️ Phishing URL Detector")
st.markdown("""
**Hybrid ML Framework with Explainable AI**

Enter any website URL below to check if it might be a phishing site.
Our system was trained on over **235,000 real URLs** using
Random Forest and XGBoost machine learning models.
""")

st.divider()

url_input = st.text_input(
    label="Enter a URL to check:",
    placeholder="https://www.example.com",
    help="You can include or omit the http:// — we handle both"
)

check_button = st.button("🔍 Analyze This URL", type="primary", use_container_width=True)

if check_button and url_input:
    with st.spinner("Analyzing URL..."):
        try:
            response = requests.post(
                url=f"{API_URL}/predict",
                json={"url": url_input},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                prediction   = data['prediction']
                confidence   = data['confidence']
                top_features = data['top_features']

                st.divider()

                if prediction == 'phishing':
                    st.error("⚠️ **WARNING: This URL appears to be PHISHING**")
                    st.markdown(
                        f"The model is **{confidence * 100:.1f}%** confident this is a phishing site."
                    )
                else:
                    st.success("✅ **This URL appears to be LEGITIMATE**")
                    st.markdown(
                        f"The model estimates only a **{confidence * 100:.1f}%** chance this is phishing."
                    )

                st.markdown("**Phishing Probability:**")
                st.progress(value=confidence, text=f"{confidence * 100:.1f}% phishing probability")

                st.divider()
                st.subheader("🔎 Why did the model make this decision?")
                st.markdown(
                    "The SHAP analysis below shows which URL features most influenced this prediction. "
                    "🔴 = pushed toward phishing, 🟢 = pushed toward legitimate."
                )

                for i, feat in enumerate(top_features, start=1):
                    icon = "🔴" if feat['direction'] == 'phishing' else "🟢"
                    impact_str = f"{feat['impact']:+.4f}"
                    direction_text = (
                        "pushes toward phishing" if feat['direction'] == 'phishing'
                        else "pushes toward legitimate"
                    )
                    st.markdown(
                        f"{icon} **#{i} — {feat['feature']}**  \n"
                        f"Value: `{feat['value']}` | SHAP impact: `{impact_str}` ({direction_text})"
                    )

                with st.expander("📊 See all extracted URL features"):
                    feature_display = {
                        "Feature":     [f['feature'] for f in top_features],
                        "Value":       [f['value'] for f in top_features],
                        "SHAP Impact": [f"{f['impact']:+.4f}" for f in top_features],
                        "Direction":   [f['direction'] for f in top_features]
                    }
                    st.dataframe(pd.DataFrame(feature_display), use_container_width=True)

            elif response.status_code == 503:
                st.error("Model not loaded. Run: python src/models/train_model.py")
            elif response.status_code == 400:
                st.warning(f"Invalid input: {response.json().get('detail', 'Unknown error')}")
            else:
                st.error(
                    f"API error ({response.status_code}): "
                    f"{response.json().get('detail', 'Unknown')}"
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "❌ Could not connect to the analysis server.\n\n"
                "Start it with:\n```\nuvicorn src.api.app:app --reload --port 8000\n```"
            )
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

elif check_button and not url_input:
    st.warning("Please enter a URL before clicking Analyze.")

st.divider()
st.subheader("🧪 Sample URLs to Try")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Likely legitimate:**")
    st.code("https://www.google.com")
    st.code("https://www.github.com")
    st.code("https://www.wikipedia.org")
with col2:
    st.markdown("**Likely phishing (example patterns):**")
    st.code("http://paypa1-login.secure-account.net")
    st.code("http://192.168.1.1/bank-login")
    st.code("http://amazon.account-suspended.verify-now.com")

st.divider()
st.caption(
    "Hybrid Phishing Detection System | Powered by XGBoost + SHAP | "
    "Dataset: PhiUSIIL (UCI)"
)