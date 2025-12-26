import axios from 'axios';
import type { QueryResponse, HealthResponse, StatsResponse, HistoryItem } from '@/types';

// Connect to Flask backend API - use relative URL when served from Flask
const API_BASE_URL = import.meta.env.PROD ? '/api' : 'http://localhost:5001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  async sendQuery(query: string): Promise<QueryResponse> {
    const response = await api.post<QueryResponse>('/query', { query });
    return response.data;
  },

  async getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  },

  async getStats(): Promise<StatsResponse> {
    const response = await api.get<StatsResponse>('/stats');
    return response.data;
  },

  async getHistory(): Promise<HistoryItem[]> {
    const response = await api.get<HistoryItem[]>('/history');
    return response.data;
  },

  async clearChat(): Promise<{ success: boolean }> {
    const response = await api.post<{ success: boolean }>('/clear-chat');
    return response.data;
  },
};
