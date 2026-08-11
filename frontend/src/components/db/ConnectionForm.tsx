import React, { useEffect, useState } from 'react';
import { Database, CheckCircle2, AlertCircle, RefreshCw, PlugZap, Copy } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';
import { connectorApi } from '../../api/connectorApi';
import { BACKEND_ORIGIN } from '../../api/config';
import { ConnectorStatusResponse, PairingCodeResponse } from '../../types/connector';

interface ConnectionFormProps {
  onConnectionVerified: (connectionString: string) => void;
}

export const ConnectionForm: React.FC<ConnectionFormProps> = ({
  onConnectionVerified,
}) => {
  const [connString, setConnString] = useState<string>(
    localStorage.getItem('connection_string') ||
      'postgresql+psycopg2://postgres:1234@localhost:5432/pagila'
  );
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [status, setStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });
  const [connectorStatus, setConnectorStatus] = useState<ConnectorStatusResponse>({
    status: 'offline',
  });
  const [pairing, setPairing] = useState<PairingCodeResponse | null>(null);

  const connectorCommand = pairing
    ? `python local_connector/connector.py start --backend ${BACKEND_ORIGIN} --pairing-code ${pairing.pairing_code}`
    : '';

  const refreshConnectorStatus = async () => {
    try {
      const res = await connectorApi.getStatus();
      setConnectorStatus(res);
    } catch {
      setConnectorStatus({ status: 'offline' });
    }
  };

  const createPairingCode = async () => {
    const res = await connectorApi.createPairingCode();
    setPairing(res);
    await refreshConnectorStatus();
  };

  useEffect(() => {
    refreshConnectorStatus();
    const intervalId = window.setInterval(refreshConnectorStatus, 5000);
    return () => window.clearInterval(intervalId);
  }, []);

  const handleTestConnection = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setStatus({ type: null, message: '' });

    try {
      if (connectorStatus.status !== 'online') {
        throw new Error('Local connector is offline. Start the connector before testing this database.');
      }

      const res = await connectorApi.testConnection(connString);
      setStatus({
        type: 'success',
        message: res.message || 'Database connection verified successfully!',
      });
      localStorage.setItem('connection_string', connString);
      onConnectionVerified(connString);
    } catch (err: any) {
      const errMsg =
        err?.response?.data?.detail ||
        err?.message ||
        'Failed to connect to the database. Please check your credentials.';
      setStatus({ type: 'error', message: errMsg });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card glowColor="violet">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/25 flex items-center justify-center text-violet-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <CardTitle>PostgreSQL Database Connection</CardTitle>
            <CardDescription>
              Enter a valid PostgreSQL SQLAlchemy connection string to query live databases
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="rounded-xl border border-white/[0.08] bg-space-deep/70 p-4 space-y-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <PlugZap className="w-4 h-4 text-violet-400" />
              <div>
                <p className="text-xs font-semibold text-slate-200">Local Connector</p>
                <p className="text-[11px] text-slate-500">
                  Status: <span className={connectorStatus.status === 'online' ? 'text-emerald-300' : 'text-amber-300'}>{connectorStatus.status}</span>
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button type="button" variant="ghost" size="sm" onClick={refreshConnectorStatus}>
                Check
              </Button>
              <Button type="button" size="sm" onClick={createPairingCode}>
                Pair Connector
              </Button>
            </div>
          </div>

          {pairing && connectorStatus.status !== 'online' && (
            <div className="space-y-2">
              <p className="text-[11px] text-slate-400">
                Run this command from the project root on the machine that can reach your database.
              </p>
              <div className="flex items-center gap-2 rounded-lg bg-black/30 border border-white/[0.06] p-2">
                <code className="text-[11px] text-violet-200 font-mono break-all flex-1">
                  {connectorCommand}
                </code>
                <button
                  type="button"
                  onClick={() => navigator.clipboard.writeText(connectorCommand)}
                  className="p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-white/5"
                  title="Copy command"
                >
                  <Copy className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleTestConnection} className="space-y-4">
          <Input
            label="Connection String (SQLAlchemy Format)"
            placeholder="postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
            value={connString}
            onChange={(e) => setConnString(e.target.value)}
            required
          />

          <div className="flex items-center justify-between pt-2">
            <p className="text-[11px] text-slate-500">
              Format: <code className="text-violet-400">postgresql+psycopg2://user:pass@host:port/dbname</code>
            </p>

            <Button
              type="submit"
              isLoading={isLoading}
              leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}
            >
              Test Connection
            </Button>
          </div>
        </form>

        {/* Status Message */}
        {status.type === 'success' && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-300 text-xs flex items-center gap-3 animate-fade-in-up">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <span>{status.message}</span>
          </div>
        )}

        {status.type === 'error' && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs flex items-center gap-3 animate-fade-in-up">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{status.message}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
