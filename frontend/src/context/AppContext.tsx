import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import type { Message, Stats, HistoryItem } from '@/types';
import { apiService } from '@/services/api';

interface AppContextType {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  stats: Stats;
  history: HistoryItem[];
  sendMessage: (query: string) => Promise<void>;
  clearChat: () => Promise<void>;
  loadHistory: () => Promise<void>;
  fetchStats: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const generateId = () => Math.random().toString(36).substring(2, 9);

export function AppProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<Stats>({
    gamesCount: 0,
    avgPoints: 0,
    totalTokens: 0,
  });
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const fetchStats = useCallback(async () => {
    try {
      const data = await apiService.getStats();
      setStats({
        gamesCount: data.games_in_db,
        avgPoints: data.avg_points || 0,
        totalTokens: data.total_tokens,
      });
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const data = await apiService.getHistory();
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  }, []);

  const sendMessage = useCallback(async (query: string) => {
    const userMessage: Message = {
      id: generateId(),
      type: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.sendQuery(query);
      
      const assistantMessage: Message = {
        id: generateId(),
        type: 'assistant',
        content: response.response,
        timestamp: new Date(),
        tokens: response.tokens,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setStats(prev => ({ ...prev, totalTokens: response.total_tokens }));
      await loadHistory();
    } catch (err) {
      const errorMessage: Message = {
        id: generateId(),
        type: 'error',
        content: 'Failed to get response. Please check if the backend server is running.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setError('Connection error');
    } finally {
      setIsLoading(false);
    }
  }, [loadHistory]);

  const clearChat = useCallback(async () => {
    try {
      await apiService.clearChat();
      setMessages([]);
      setHistory([]);
      setStats(prev => ({ ...prev, totalTokens: 0 }));
    } catch (err) {
      console.error('Failed to clear chat:', err);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    loadHistory();
    
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [fetchStats, loadHistory]);

  return (
    <AppContext.Provider
      value={{
        messages,
        isLoading,
        error,
        stats,
        history,
        sendMessage,
        clearChat,
        loadHistory,
        fetchStats,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
