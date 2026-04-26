import axios from 'axios';


const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://195.250.20.9:5000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use((config) => {
  console.log('API Request:', config.url);
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export const dashboardAPI = {
  // Get overall statistics
  getStats: () => api.get('/stats'),

  // Get list of attackers
  getAttackers: (limit = 20) => api.get(`/attackers?limit=${limit}`),

  // Get attack timeline data
  getTimeline: (hours = 24) => api.get(`/timeline?hours=${hours}`),

  // Get captured credentials
  getCredentials: (limit = 50) => api.get(`/credentials?limit=${limit}`),

  // Get attack details
  getAttackDetails: (attackerId) => api.get(`/attackers/${attackerId}`),

  // Get protocol breakdown
  getProtocols: () => api.get('/protocols'),

  // Get HTTP requests
  getHttpRequests: (limit = 20) => api.get(`/http-requests?limit=${limit}`),

  // Get commands executed
  getCommands: (limit = 20) => api.get(`/commands?limit=${limit}`),

  // Get geographic distribution
  getGeoData: () => api.get('/geo-distribution'),

  // Get geo map data with lat/lon for Leaflet pins
  getGeoMap: () => api.get('/geo-map'),

  // Get recent events for live threat feed
  getRecentEvents: (limit = 20) => api.get(`/events/recent?limit=${limit}`),

  // Get session commands for replay
  getSessionCommands: (sessionId) => api.get(`/sessions/${sessionId}/commands`),

  // Health check
  healthCheck: () => axios.get(`${API_BASE_URL}/health`),
};

export default api;
