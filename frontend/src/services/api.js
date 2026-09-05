/**
 * Centralized API Service Layer.
 * Communicates with FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP Error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

export const api = {
  // Phase 1 Endpoints
  getHealth: () => fetchJson('/api/health'),
  getSummary: () => fetchJson('/api/data/summary'),
  getServiceBreakdown: () => fetchJson('/api/cost/service-breakdown'),
  getProviderBreakdown: () => fetchJson('/api/cost/provider-breakdown'),
  getDailyTrend: () => fetchJson('/api/cost/daily-trend'),
  validateDataset: () => fetchJson('/api/data/validate', { method: 'POST' }),

  // Phase 2 Endpoints
  getAnomalies: (contamination = 0.03) => fetchJson(`/api/anomalies?contamination=${contamination}`),
  getAnomaliesSummary: (contamination = 0.03) => fetchJson(`/api/anomalies/summary?contamination=${contamination}`),
  getTopAnomalies: (limit = 10, contamination = 0.03) => fetchJson(`/api/anomalies/top?limit=${limit}&contamination=${contamination}`),

  // Phase 3 Endpoints
  getForecast: (days = 30) => fetchJson(`/api/forecast?days=${days}`),
  getForecastSummary: () => fetchJson('/api/forecast/summary'),
  getServiceForecasts: () => fetchJson('/api/forecast/services'),
  getForecastEvaluation: () => fetchJson('/api/forecast/evaluation'),

  // Phase 4 Endpoints
  getAnomalyAnalysis: (anomalyId) => fetchJson(`/api/anomalies/${anomalyId}/analysis`),
  getRecommendations: () => fetchJson('/api/recommendations'),
  getCostDrivers: () => fetchJson('/api/cost/drivers'),
  getBusinessInsights: () => fetchJson('/api/insights'),

  // Phase 6.5 Real Data Import Endpoints
  getActiveDataset: () => fetchJson('/api/data/active'),
  uploadDataset: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetchJson('/api/data/upload', {
      method: 'POST',
      headers: {}, // fetch will set multipart/form-data boundary automatically
      body: formData,
    });
  },
  activateDataset: (filename) => fetchJson('/api/data/activate', {
    method: 'POST',
    body: JSON.stringify({ filename }),
  }),
  restoreDemoDataset: () => fetchJson('/api/data/restore-demo', {
    method: 'POST',
  }),
};
