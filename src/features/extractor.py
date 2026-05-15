"""
URL Feature Extractor
=====================
Takes a URL string and extracts numerical features from it.
These features are what the machine learning model uses to decide
whether the URL is phishing or legitimate.
"""

import re
import math
from urllib.parse import urlparse
import tldextract


def extract_features(url: str) -> dict:
    """
    Input:  a URL string, e.g. "https://www.google.com"
    Output: a dictionary of feature names mapped to numbers
    """
    features = {}

    parsed = urlparse(url)
    extracted = tldextract.extract(url)

    # Length features
    features['url_length'] = len(url)
    features['domain_length'] = len(extracted.domain) if extracted.domain else 0
    features['path_length'] = len(parsed.path)

    # Character count features
    features['num_dots'] = url.count('.')
    features['num_hyphens'] = url.count('-')
    features['num_underscores'] = url.count('_')
    features['num_slashes'] = max(0, url.count('/') - 2)
    features['num_at_signs'] = url.count('@')
    features['num_question_marks'] = url.count('?')
    features['num_equals_signs'] = url.count('=')
    features['num_digits'] = sum(c.isdigit() for c in url)

    # Security features
    features['uses_https'] = 1 if parsed.scheme == 'https' else 0

    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    netloc_without_port = parsed.netloc.split(':')[0]
    features['uses_ip_address'] = 1 if ip_pattern.match(netloc_without_port) else 0

    # Domain features
    subdomain = extracted.subdomain
    features['num_subdomains'] = len(subdomain.split('.')) if subdomain else 0
    features['has_www'] = 1 if 'www' in url.lower() else 0

    # Suspicious keyword features
    suspicious_keywords = [
        'login', 'signin', 'secure', 'account', 'update',
        'verify', 'banking', 'confirm', 'password', 'paypal',
        'ebay', 'amazon', 'apple', 'microsoft', 'support',
        'webscr', 'cmd', 'dispatch', 'suspend'
    ]
    url_lower = url.lower()
    features['has_suspicious_keyword'] = 1 if any(
        k in url_lower for k in suspicious_keywords
    ) else 0
    features['num_suspicious_keywords'] = sum(
        k in url_lower for k in suspicious_keywords
    )

    # Entropy feature
    def shannon_entropy(text):
        if not text:
            return 0.0
        probabilities = [text.count(c) / len(text) for c in set(text)]
        return -sum(p * math.log2(p) for p in probabilities)

    features['domain_entropy'] = shannon_entropy(extracted.domain)

    return features


def get_feature_names() -> list:
    """
    Returns the ordered list of feature names.
    The order must always be the same — the model depends on it.
    """
    return [
        'url_length', 'domain_length', 'path_length',
        'num_dots', 'num_hyphens', 'num_underscores',
        'num_slashes', 'num_at_signs', 'num_question_marks',
        'num_equals_signs', 'num_digits', 'uses_https',
        'uses_ip_address', 'num_subdomains', 'has_www',
        'has_suspicious_keyword', 'num_suspicious_keywords',
        'domain_entropy'
    ]


def features_to_array(features: dict) -> list:
    """Converts features dict to ordered list for the ML model."""
    return [features.get(name, 0) for name in get_feature_names()]