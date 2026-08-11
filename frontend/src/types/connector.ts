import { ConnectionTestResponse, DatabaseSchemaResponse } from './sql';

export interface PairingCodeResponse {
  connector_id: string;
  pairing_code: string;
  status: string;
}

export interface ConnectorStatusResponse {
  connector_id?: string | null;
  status: 'pending' | 'online' | 'offline';
  last_seen_at?: string | null;
}

export type ConnectorConnectionTestResponse = ConnectionTestResponse;
export type ConnectorSchemaResponse = DatabaseSchemaResponse;
