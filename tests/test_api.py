"""
Unit Tests for the FastAPI Backend
Run with: pytest tests/ -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_api_module_imports_successfully():
    from src.api.app import app
    assert app is not None


class TestHealthEndpoint:

    def setup_method(self):
        from fastapi.testclient import TestClient
        from src.api.app import app
        self.client = TestClient(app)

    def test_health_returns_200(self):
        response = self.client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self):
        response = self.client.get("/health")
        assert isinstance(response.json(), dict)

    def test_health_has_status_field(self):
        response = self.client.get("/health")
        assert 'status' in response.json()

    def test_health_has_model_loaded_field(self):
        response = self.client.get("/health")
        data = response.json()
        assert 'model_loaded' in data
        assert isinstance(data['model_loaded'], bool)


def test_predict_with_no_body_returns_422():
    from fastapi.testclient import TestClient
    from src.api.app import app
    client = TestClient(app)
    response = client.post("/predict")
    assert response.status_code == 422