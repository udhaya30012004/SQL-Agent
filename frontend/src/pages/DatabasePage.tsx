import React, { useState } from 'react';
import { ConnectionForm } from '../components/db/ConnectionForm';
import { SchemaViewer } from '../components/db/SchemaViewer';

export const DatabasePage: React.FC = () => {
  const [activeConnString, setActiveConnString] = useState<string>(
    localStorage.getItem('connection_string') ||
      'postgresql+psycopg2://postgres:1234@localhost:5432/pagila'
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12 animate-fade-in-up">
      <ConnectionForm
        onConnectionVerified={(conn) => setActiveConnString(conn)}
      />

      <SchemaViewer connectionString={activeConnString} />
    </div>
  );
};
