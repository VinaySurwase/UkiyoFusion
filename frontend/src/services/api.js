import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'development' ? 'http://localhost:5001' : (process.env.REACT_APP_API_URL || 'http://localhost:5001');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 3600000, // 1 hour timeout for image processing
});

export const transformImage = async (data) => {
  try {
    console.log('Sending transform request:', data);
    const response = await api.post('/api/transform', data);
    console.log('Transform response received:', response.data);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      url: error.config?.url
    });
    throw new Error(error.response?.data?.error || 'Failed to transform image');
  }
};

export const getModels = async () => {
  try {
    console.log('Fetching models from:', `${API_BASE_URL}/api/models`);
    const response = await api.get('/api/models');
    console.log('Models response:', response.data);
    return response.data;
  } catch (error) {
    console.error('API Error fetching models:', error);
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      url: error.config?.url
    });
    throw new Error('Failed to fetch models');
  }
};

export const getStyles = async () => {
  try {
    console.log('Fetching styles from:', `${API_BASE_URL}/api/styles`);
    const response = await api.get('/api/styles');
    console.log('Styles response:', response.data);
    return response.data;
  } catch (error) {
    console.error('API Error fetching styles:', error);
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      url: error.config?.url
    });
    throw new Error('Failed to fetch styles');
  }
};

export const getControlNetOptions = async () => {
  try {
    console.log('Fetching ControlNet options from:', `${API_BASE_URL}/api/controlnet`);
    const response = await api.get('/api/controlnet');
    console.log('ControlNet response:', response.data);
    return response.data;
  } catch (error) {
    console.error('API Error fetching ControlNet options:', error);
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      url: error.config?.url
    });
    // Return empty options if ControlNet is not available
    return { controlnet_options: {} };
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error('Health check failed');
  }
};

export default api;
