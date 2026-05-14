import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
});

export const predictCards = async (data) => {
  const response = await api.post('/predict', data);
  return response.data;
};

export const submitFeedback = async (predictionId, isCorrect, actualCards = null) => {
  const payload = { prediction_id: predictionId };
  if (isCorrect !== null) payload.is_correct = isCorrect;
  if (actualCards !== null) payload.actual_cards = actualCards;
  const response = await api.post('/feedback', payload);
  return response.data;
};

export const getHistory = async () => {
  const response = await api.get('/history');
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export const trainModel = async () => {
  const response = await api.post('/train');
  return response.data;
};
