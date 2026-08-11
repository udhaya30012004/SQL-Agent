import { apiClient } from './client';
import {
  ConnectorConnectionTestResponse,
  ConnectorSchemaResponse,
  ConnectorStatusResponse,
  PairingCodeResponse,
} from '../types/connector';

export const connectorApi = {
  createPairingCode: async (): Promise<PairingCodeResponse> => {
    const res = await apiClient.post<PairingCodeResponse>('/connectors/pairing-code');
    return res.data;
  },

  getStatus: async (): Promise<ConnectorStatusResponse> => {
    const res = await apiClient.get<ConnectorStatusResponse>('/connectors/status');
    return res.data;
  },

  testConnection: async (
    connectionString: string
  ): Promise<ConnectorConnectionTestResponse> => {
    const res = await apiClient.post<ConnectorConnectionTestResponse>(
      '/connectors/connections/test',
      { connection_string: connectionString }
    );
    return res.data;
  },

  getSchema: async (connectionString: string): Promise<ConnectorSchemaResponse> => {
    const res = await apiClient.post<ConnectorSchemaResponse>('/connectors/schema', {
      connection_string: connectionString,
    });
    return res.data;
  },
};
