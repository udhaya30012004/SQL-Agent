import { apiClient } from './client';
import {
  ConnectionTestRequest,
  ConnectionTestResponse,
  DatabaseSchemaResponse,
} from '../types/sql';

export const sqlApi = {
  testConnection: async (
    payload: ConnectionTestRequest
  ): Promise<ConnectionTestResponse> => {
    const res = await apiClient.post<ConnectionTestResponse>(
      '/sql/connect',
      payload
    );
    return res.data;
  },

  getSchema: async (
    payload: ConnectionTestRequest
  ): Promise<DatabaseSchemaResponse> => {
    const res = await apiClient.post<DatabaseSchemaResponse>(
      '/sql/schema',
      payload
    );
    return res.data;
  },
};
