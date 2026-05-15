"""
Unit Tests for the Prediction Module
Run with: pytest tests/ -v
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_predict_module_can_be_imported():
    from src.models.predict import predict_url, load_model
    assert callable(predict_url)
    assert callable(load_model)


def test_load_model_raises_error_for_invalid_type():
    from src.models.predict import load_model
    with pytest.raises((ValueError, FileNotFoundError)):
        load_model('nonexistent_model_type_xyz')


@pytest.mark.skipif(
    not os.path.exists('models/saved_models/xgboost_model.pkl'),
    reason="Trained model not found — run src/models/train_model.py first"
)
class TestPredictionWithModel:

    def setup_method(self):
        from src.models.predict import load_model
        self.model = load_model('xgboost')

    def test_prediction_returns_dict(self):
        from src.models.predict import predict_url
        result = predict_url("https://www.google.com", model=self.model)
        assert isinstance(result, dict)

    def test_prediction_has_required_keys(self):
        from src.models.predict import predict_url
        result = predict_url("https://www.google.com", model=self.model)
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'features' in result

    def test_prediction_value_is_valid(self):
        from src.models.predict import predict_url
        result = predict_url("https://www.google.com", model=self.model)
        assert result['prediction'] in ['phishing', 'legitimate']

    def test_confidence_is_between_zero_and_one(self):
        from src.models.predict import predict_url
        result = predict_url("https://www.google.com", model=self.model)
        assert 0.0 <= result['confidence'] <= 1.0

    def test_google_is_likely_legitimate(self):
        from src.models.predict import predict_url
        result = predict_url("https://www.google.com", model=self.model)
        assert result['prediction'] == 'legitimate'

    def test_obvious_phishing_url(self):
        from src.models.predict import predict_url
        result = predict_url(
            "http://192.168.1.1/paypal-login-verify", model=self.model
        )
        assert result['confidence'] > 0.3