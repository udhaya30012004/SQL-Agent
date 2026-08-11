import { apiClient } from './client';
import {
  TokenResponse,
  User,
  UserLoginPayload,
  UserSignupPayload,
} from '../types/auth';

export const authApi = {
  signup: async (payload: UserSignupPayload): Promise<User> => {
    const res = await apiClient.post<User>('/auth/signup', payload);
    return res.data;
  },

  login: async (payload: UserLoginPayload): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>('/auth/login', payload);
    return res.data;
  },

  logout: async (): Promise<{ message: string }> => {
    const res = await apiClient.post<{ message: string }>('/auth/logout');
    return res.data;
  },

  getMe: async (): Promise<User> => {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },
};
