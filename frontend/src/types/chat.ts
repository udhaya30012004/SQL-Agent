export interface ChatMessage {
  id: number;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  sql_query?: string | null;
  chart_path?: string | null;
  chart_spec?: Record<string, any> | null;
  error?: string | null;
}

export type ChatResponseMode = 'answer' | 'chart' | 'both';

export interface ChatSession {
  id: string;
  user_id: string;
  agent_type: 'sql' | 'pandas';
  title?: string | null;
  created_at: string;
  messages: ChatMessage[];
}

export interface SessionCreateRequest {
  agent_type: 'sql' | 'pandas';
  title?: string;
}

export interface ChatRequest {
  session_id: string;
  question: string;
  response_mode?: ChatResponseMode;
  connection_string?: string;
}
