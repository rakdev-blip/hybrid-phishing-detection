"""
URL Feature Extractor
=====================
Takes a URL string and extracts numerical features from it.
These features are what the machine learning model uses to decide
whether the URL is phishing or legitimate.
"""

import re
import math
import os
from urllib.parse import urlparse
import tldextract

# ---------------------------------------------------------------
# Tranco domain reputation list loader
# Uses multiple path strategies to find the file whether called
# from a notebook, terminal script, or the API server
# ---------------------------------------------------------------

_TRANCO_DOMAINS = set()

def _find_tranco_file():
    """
    Tries multiple strategies to locate tranco_top_1million.txt
    regardless of where the code is being called from.
    """
    filename = 'tranco_top_1million.txt'

    # Strategy 1: relative to this file (src/features/extractor.py)
    # Go up 3 levels: features -> src -> project_root -> data/raw
    try:
        this_file = os.path.abspath(__file__)
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(this_file))
        )
        candidate = os.path.join(project_root, 'data', 'raw', filename)
        if os.path.exists(candidate):
            return candidate
    except Exception:
        pass

    # Strategy 2: relative to current working directory
    # Works when running from the project root in terminal
    candidate = os.path.join(os.getcwd(), 'data', 'raw', filename)
    if os.path.exists(candidate):
        return candidate

    # Strategy 3: walk up from cwd looking for the file
    current = os.getcwd()
    for _ in range(5):
        candidate = os.path.join(current, 'data', 'raw', filename)
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    # Strategy 4: check common Windows project paths
    for drive in ['D:\\', 'C:\\']:
        candidate = os.path.join(drive, 'HPD', 'hybrid-phishing-detection',
                                 'data', 'raw', filename)
        if os.path.exists(candidate):
            return candidate

    return None


def _load_tranco():
    global _TRANCO_DOMAINS
    if len(_TRANCO_DOMAINS) == 0:
        path = _find_tranco_file()
        if path:
            with open(path, encoding='utf-8') as f:
                lines = f.read().splitlines()
            # Use top 500,000 to avoid obscure domains
            _TRANCO_DOMAINS = set(lines[:500000])
            print(f"Loaded {len(_TRANCO_DOMAINS)} Tranco domains from: {path}")
        else:
            print("Warning: tranco_top_1million.txt not found anywhere.")
            print("Domain reputation feature will be 0 for all URLs.")
            print("Run Phase 1 Step 2 to download the Tranco list.")

_load_tranco()


def extract_features(url: str) -> dict:
    """
    Input:  a URL string, e.g. "https://www.google.com"
    Output: a dictionary of feature names mapped to numbers
    """
    features = {}

    parsed = urlparse(url)
    extracted = tldextract.extract(url)

    # ---------------------------------------------------------------
    # FEATURE GROUP 1: Length features
    # ---------------------------------------------------------------
    features['url_length'] = len(url)
    features['domain_length'] = len(extracted.domain) if extracted.domain else 0
    features['path_length'] = len(parsed.path)

    # ---------------------------------------------------------------
    # FEATURE GROUP 2: Character count features
    # ---------------------------------------------------------------
    features['num_dots'] = url.count('.')
    features['num_hyphens'] = url.count('-')
    features['num_underscores'] = url.count('_')
    features['num_slashes'] = max(0, url.count('/') - 2)
    features['num_at_signs'] = url.count('@')
    features['num_question_marks'] = url.count('?')
    features['num_equals_signs'] = url.count('=')
    features['num_digits'] = sum(c.isdigit() for c in url)

    # ---------------------------------------------------------------
    # FEATURE GROUP 3: Security features
    # ---------------------------------------------------------------
    features['uses_https'] = 1 if parsed.scheme == 'https' else 0

    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    netloc_without_port = parsed.netloc.split(':')[0]
    features['uses_ip_address'] = 1 if ip_pattern.match(netloc_without_port) else 0

    # ---------------------------------------------------------------
    # FEATURE GROUP 4: Domain features
    # ---------------------------------------------------------------
    subdomain_str = extracted.subdomain
    features['num_subdomains'] = len(subdomain_str.split('.')) if subdomain_str else 0
    features['has_www'] = 1 if 'www' in url.lower() else 0

    # ---------------------------------------------------------------
    # FEATURE GROUP 5: Suspicious keyword features
    # ---------------------------------------------------------------
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

    # ---------------------------------------------------------------
    # FEATURE GROUP 6: Entropy feature
    # ---------------------------------------------------------------
    def shannon_entropy(text):
        if not text:
            return 0.0
        probabilities = [text.count(c) / len(text) for c in set(text)]
        return -sum(p * math.log2(p) for p in probabilities)

    features['domain_entropy'] = shannon_entropy(extracted.domain)

    # ---------------------------------------------------------------
    # FEATURE GROUP 7: Domain reputation feature
    # ---------------------------------------------------------------
    # A URL is trusted only if:
    # 1. Its registered domain is in the Tranco top 500k AND
    # 2. The subdomain is simple (empty, 'www', or 'mail')
    # This prevents paypa1-login.evil.com scoring as trusted
    # even if evil.com is in Tranco

    registered_domain = (
        extracted.domain + '.' + extracted.suffix
    ).lower() if extracted.suffix else extracted.domain.lower()

    subdomain_lower = extracted.subdomain.lower() if extracted.subdomain else ''
    subdomain_is_simple = subdomain_lower in ('', 'www', 'mail', 'www2', 'secure')

    in_tranco = registered_domain in _TRANCO_DOMAINS

    features['is_in_top_1million'] = 1 if (in_tranco and subdomain_is_simple) else 0

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
        'domain_entropy', 'is_in_top_1million'
    ]


def features_to_array(features: dict) -> list:
    """Converts features dict to ordered list for the ML model."""
    return [features.get(name, 0) for name in get_feature_names()]