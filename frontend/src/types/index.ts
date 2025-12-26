export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'error';
  content: string;
  timestamp: Date;
  tokens?: number;
}

export interface HistoryItem {
  timestamp: string;
  query: string;
  response: string;
  tokens: number;
}

export interface Stats {
  gamesCount: number;
  avgPoints: number;
  totalTokens: number;
}

export interface HealthResponse {
  status: string;
  database: string;
  records: number;
  version: string;
}

export interface StatsResponse {
  total_tokens: number;
  chat_sessions: number;
  games_in_db: number;
  players_tracked: number;
  avg_points?: number;
  rag_status: string;
}

export interface QueryResponse {
  response: string;
  tokens: number;
  total_tokens: number;
}
