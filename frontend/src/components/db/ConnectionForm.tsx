import React, { useState } from 'react';
import { Database, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';
import { sqlApi } from '../../api/sqlApi';

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

  const handleTestConnection = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setStatus({ type: null, message: '' });

    try {
      const res = await sqlApi.testConnection({
        connection_string: connString,
      });
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
