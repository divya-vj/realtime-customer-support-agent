import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const sendMessage = async (sessionId, message, customerName = null) => {
  try {
    const response = await api.post('/chat', {
      session_id: sessionId,
      message: message,
      customer_name: customerName,
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

export const getDashboardAnalytics = async () => {
  try {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  } catch (error) {
    console.error('Error fetching analytics:', error);
    throw error;
  }
};

export const getAllConversations = async (status = null, limit = 50) => {
  try {
    const params = { limit };
    if (status) params.status = status;
    
    const response = await api.get('/analytics/conversations', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching conversations:', error);
    throw error;
  }
};

export const getSentimentTrends = async () => {
  try {
    const response = await api.get('/analytics/sentiment-trends');
    return response.data;
  } catch (error) {
    console.error('Error fetching sentiment trends:', error);
    throw error;
  }
};

export default api;