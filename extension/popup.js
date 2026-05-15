const API_URL = 'http://localhost:8000';

function showStatus(statusId) {
  ['status-loading', 'status-safe', 'status-phishing', 'status-error'].forEach(function(id) {
    document.getElementById(id).classList.add('hidden');
  });
  if (statusId) {
    document.getElementById(statusId).classList.remove('hidden');
  }
}

function displayFeatures(topFeatures) {
  var list = document.getElementById('features-list');
  list.innerHTML = '';
  topFeatures.forEach(function(feat) {
    var li = document.createElement('li');
    var icon = feat.direction === 'phishing' ? '🔴' : '🟢';
    var value = parseFloat(feat.value).toFixed(2);
    li.textContent = icon + ' ' + feat.feature + ' = ' + value;
    list.appendChild(li);
  });
  document.getElementById('features-section').classList.remove('hidden');
}

async function checkCurrentPage() {
  var button = document.getElementById('check-btn');
  button.disabled = true;
  button.textContent = 'Analyzing...';

  document.getElementById('url-display').classList.add('hidden');
  document.getElementById('features-section').classList.add('hidden');
  showStatus('loading');

  try {
    var tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    var url = tabs[0].url;

    var displayUrl = url.length > 55 ? url.substring(0, 55) + '...' : url;
    document.getElementById('url-text').textContent = displayUrl;
    document.getElementById('url-display').classList.remove('hidden');

    if (url.startsWith('chrome://') ||
        url.startsWith('chrome-extension://') ||
        url.startsWith('about:')) {
      showStatus('error');
      document.getElementById('error-detail').textContent =
        'Cannot analyze browser internal pages.';
      return;
    }

    var response = await fetch(API_URL + '/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url })
    });

    if (!response.ok) {
      var errorData = await response.json();
      throw new Error(errorData.detail || 'API error: ' + response.status);
    }

    var data = await response.json();
    var confidencePct = (data.confidence * 100).toFixed(1);

    if (data.prediction === 'phishing') {
      showStatus('phishing');
      document.getElementById('phishing-detail').textContent =
        'Confidence: ' + confidencePct + '% likely phishing. Proceed with caution.';
    } else {
      showStatus('safe');
      document.getElementById('safe-detail').textContent =
        'Phishing probability: ' + confidencePct + '%. This page appears safe.';
    }

    if (data.top_features && data.top_features.length > 0) {
      displayFeatures(data.top_features);
    }

  } catch (error) {
    showStatus('error');
    if (error.message.includes('Failed to fetch') ||
        error.message.includes('NetworkError') ||
        error.message.includes('ERR_CONNECTION_REFUSED')) {
      document.getElementById('error-detail').textContent =
        'Cannot connect to the analysis server. ' +
        'Start it with: uvicorn src.api.app:app --reload --port 8000';
    } else {
      document.getElementById('error-detail').textContent =
        'Error: ' + error.message;
    }
  } finally {
    button.disabled = false;
    button.textContent = 'Check This Page';
  }
}

document.addEventListener('DOMContentLoaded', function() {
  checkCurrentPage();
  document.getElementById('check-btn').addEventListener('click', checkCurrentPage);
});