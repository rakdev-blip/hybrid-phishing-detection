"""
Unit Tests for Feature Extractor
==================================
Run all tests with: pytest tests/ -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.features.extractor import extract_features, get_feature_names


class TestExtractFeaturesBasic:

    def test_returns_a_dictionary(self):
        result = extract_features("https://www.google.com")
        assert isinstance(result, dict)

    def test_all_feature_names_are_present(self):
        expected = get_feature_names()
        result = extract_features("https://www.google.com")
        for name in expected:
            assert name in result, f"Feature '{name}' is missing"

    def test_all_values_are_numbers(self):
        result = extract_features("https://www.google.com")
        for name, value in result.items():
            assert isinstance(value, (int, float)), f"Feature '{name}' is not a number"


class TestHTTPSDetection:

    def test_https_url_gets_one(self):
        result = extract_features("https://www.google.com")
        assert result['uses_https'] == 1

    def test_http_url_gets_zero(self):
        result = extract_features("http://www.example.com")
        assert result['uses_https'] == 0


class TestIPAddressDetection:

    def test_ip_address_url_is_flagged(self):
        result = extract_features("http://192.168.1.1/login")
        assert result['uses_ip_address'] == 1

    def test_normal_domain_is_not_flagged(self):
        result = extract_features("https://www.google.com")
        assert result['uses_ip_address'] == 0


class TestURLLength:

    def test_url_length_is_exact(self):
        url = "https://www.google.com"
        result = extract_features(url)
        assert result['url_length'] == len(url)

    def test_longer_url_has_greater_length(self):
        short = extract_features("https://google.com")
        long  = extract_features(
            "http://paypa1-secure-login.suspicious-domain.com/account/verify?token=abc123"
        )
        assert long['url_length'] > short['url_length']


class TestSuspiciousKeywords:

    def test_url_with_login_keyword(self):
        result = extract_features("http://paypa1-login.suspicious.com")
        assert result['has_suspicious_keyword'] == 1

    def test_clean_url_has_no_keywords(self):
        result = extract_features("https://www.bbc.co.uk/news")
        assert result['has_suspicious_keyword'] == 0

    def test_keyword_count_is_correct(self):
        result = extract_features("http://secure-account-login.evil.com")
        assert result['num_suspicious_keywords'] >= 2


class TestDotCount:

    def test_counts_dots_correctly(self):
        result = extract_features("https://a.b.c.com")
        assert result['num_dots'] == 3


class TestFeatureNames:

    def test_returns_list(self):
        assert isinstance(get_feature_names(), list)

    def test_not_empty(self):
        assert len(get_feature_names()) > 0

    def test_all_strings(self):
        for name in get_feature_names():
            assert isinstance(name, str)

    def test_no_duplicates(self):
        names = get_feature_names()
        assert len(names) == len(set(names))