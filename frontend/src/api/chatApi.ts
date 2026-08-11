import { apiClient } from './client';
import {
  ChatMessage,
  ChatRequest,
  ChatSession,
  SessionCreateRequest,
} from '../types/chat';

export const chatApi = {
  createSession: async (
    payload: SessionCreateRequest
  ): Promise<ChatSession> => {
    const res = await apiClient.post<ChatSession>('/chat/sessions', payload);
    return res.data;
  },

  getSessions: async (): Promise<ChatSession[]> => {
    const res = await apiClient.get<ChatSession[]>('/chat/sessions');
    return res.data;
  },

  getSessionById: async (sessionId: string): Promise<ChatSession> => {
    const res = await apiClient.get<ChatSession>(`/chat/sessions/${sessionId}`);
    return res.data;
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await apiClient.delete(`/chat/sessions/${sessionId}`);
  },

  askAgent: async (payload: ChatRequest): Promise<ChatMessage> => {
    // Note: Must use trailing slash '/chat/' to prevent FastAPI 307 Temporary Redirect header stripping
    const res = await apiClient.post<ChatMessage>('/chat/', payload);
    return res.data;
  },
};
