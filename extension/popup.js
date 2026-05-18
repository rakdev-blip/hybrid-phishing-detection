const API_URL = 'http://localhost:8000';

function showStatus(statusId) {
  ['status-loading', 'status-safe', 'status-phishing', 'status-error'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });
  if (statusId) {
    var target = document.getElementById(statusId);
    if (target) target.classList.remove('hidden');
  }
}

function displayFeatures(topFeatures) {
  if (!topFeatures || topFeatures.length === 0) return;
  var list = document.getElementById('features-list');
  if (!list) return;
  list.innerHTML = '';
  topFeatures.forEach(function(feat) {
    var li = document.createElement('li');
    var icon = feat.direction === 'phishing' ? '🔴' : '🟢';
    var value = parseFloat(feat.value).toFixed(2);
    li.textContent = icon + ' ' + feat.feature + ' = ' + value;
    list.appendChild(li);
  });
  var section = document.getElementById('features-section');
  if (section) section.classList.remove('hidden');
}

async function checkCurrentPage() {
  var button = document.getElementById('check-btn');
  if (button) {
    button.disabled = true;
    button.textContent = 'Analyzing...';
  }

  var urlDisplay = document.getElementById('url-display');
  var featuresSection = document.getElementById('features-section');
  if (urlDisplay) urlDisplay.classList.add('hidden');
  if (featuresSection) featuresSection.classList.add('hidden');

  showStatus('status-loading');

  try {
    var tabs = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tabs || tabs.length === 0) {
      showStatus('status-error');
      var errEl = document.getElementById('error-detail');
      if (errEl) errEl.textContent = 'Could not get current tab.';
      return;
    }

    var url = tabs[0].url;

    var urlText = document.getElementById('url-text');
    if (urlText) {
      urlText.textContent = url.length > 55 ? url.substring(0, 55) + '...' : url;
    }
    if (urlDisplay) urlDisplay.classList.remove('hidden');

    if (url.startsWith('chrome://') ||
        url.startsWith('chrome-extension://') ||
        url.startsWith('about:') ||
        url.startsWith('edge://')) {
      showStatus('status-error');
      var errEl = document.getElementById('error-detail');
      if (errEl) errEl.textContent = 'Cannot analyze browser internal pages.';
      return;
    }

    var response = await fetch(API_URL + '/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url, fast: true })
    });

    if (!response.ok) {
      var errorData = await response.json();
      throw new Error(errorData.detail || 'API error: ' + response.status);
    }

    var data = await response.json();
    var confidencePct = (data.confidence * 100).toFixed(1);

    if (data.prediction === 'phishing') {
      showStatus('status-phishing');
      var phishEl = document.getElementById('phishing-detail');
      if (phishEl) {
        phishEl.textContent = 'Confidence: ' + confidencePct + '% likely phishing. Proceed with caution.';
      }
    } else {
      showStatus('status-safe');
      var safeEl = document.getElementById('safe-detail');
      if (safeEl) {
        safeEl.textContent = 'Phishing probability: ' + confidencePct + '%. This page appears safe.';
      }
    }

    if (data.top_features && data.top_features.length > 0) {
      displayFeatures(data.top_features);
    }

  } catch (error) {
    showStatus('status-error');
    var errEl = document.getElementById('error-detail');
    if (errEl) {
      if (error.message.includes('Failed to fetch') ||
          error.message.includes('NetworkError') ||
          error.message.includes('ERR_CONNECTION_REFUSED') ||
          error.message.includes('Load failed')) {
        errEl.textContent = 'Cannot connect to the analysis server. Start it with: uvicorn src.api.app:app --reload --port 8000';
      } else {
        errEl.textContent = 'Error: ' + error.message;
      }
    }
  } finally {
    if (button) {
      button.disabled = false;
      button.textContent = 'Check This Page';
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  checkCurrentPage();
  var btn = document.getElementById('check-btn');
  if (btn) {
    btn.addEventListener('click', checkCurrentPage);
  }
});