import React, { useState, useEffect } from 'react';
import { Table, Key, Link2, Search, Layers, ChevronDown, ChevronUp } from 'lucide-react';
import { DatabaseSchemaResponse, TableSchema } from '../../types/sql';
import { connectorApi } from '../../api/connectorApi';
import { StateWrapper } from '../common/StateWrapper';
import { Badge } from '../ui/badge';

interface SchemaViewerProps {
  connectionString: string;
}

export const SchemaViewer: React.FC<SchemaViewerProps> = ({ connectionString }) => {
  const [data, setData] = useState<DatabaseSchemaResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedTables, setExpandedTables] = useState<Record<string, boolean>>({});

  const fetchSchema = async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const res = await connectorApi.getSchema(connectionString);
      setData(res);
      // Auto-expand first 2 tables
      if (res.schema) {
        const firstTwo = Object.keys(res.schema).slice(0, 2);
        const initExpanded: Record<string, boolean> = {};
        firstTwo.forEach((t) => (initExpanded[t] = true));
        setExpandedTables(initExpanded);
      }
    } catch (err: any) {
      setIsError(true);
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (connectionString) {
      fetchSchema();
    }
  }, [connectionString]);

  const toggleTable = (tableName: string) => {
    setExpandedTables((prev) => ({
      ...prev,
      [tableName]: !prev[tableName],
    }));
  };

  const schemaEntries = data?.schema ? Object.entries(data.schema) : [];
  const filteredEntries = schemaEntries.filter(([tableName]) =>
    tableName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-space-surface/60 border border-white/[0.06]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-violet-500/10 border border-violet-500/25 flex items-center justify-center text-violet-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 font-heading">
              Extracted Database Schema Metadata
            </h3>
            <p className="text-xs text-slate-400">
              Total Tables Detected: <span className="text-violet-400 font-bold font-mono">{data?.tables_count || 0}</span>
            </p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search tables..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-space-deep text-xs text-slate-200 placeholder:text-slate-500 pl-8 pr-3 py-2 rounded-xl border border-white/[0.08] outline-none focus:border-violet-500/50 transition-colors"
          />
        </div>
      </div>

      <StateWrapper
        isLoading={isLoading}
        isError={isError}
        error={error}
        isEmpty={filteredEntries.length === 0}
        onRetry={fetchSchema}
        isRetrying={isLoading}
        skeletonVariant="schema"
        skeletonCount={3}
        emptyTitle="No tables found"
        emptyDescription="No database tables matched your search query or schema is empty."
      >
        <div className="grid grid-cols-1 gap-4">
          {filteredEntries.map(([tableName, tableDetails]) => {
            const isExpanded = !!expandedTables[tableName];
            const primaryKeys = tableDetails.primary_keys || tableDetails.primary_key || [];
            const foreignKeys = tableDetails.foreign_keys || [];
            const columns = tableDetails.columns || [];

            return (
              <div
                key={tableName}
                className="rounded-2xl bg-space-surface/80 border border-white/[0.07] overflow-hidden shadow-lg transition-all duration-300 hover-lift"
              >
                {/* Table Header */}
                <div
                  onClick={() => toggleTable(tableName)}
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/[0.03] transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Table className="w-4 h-4 text-violet-400" />
                    <span className="text-sm font-bold font-mono text-slate-100">
                      {tableName}
                    </span>
                    <Badge variant="gray" size="sm">
                      {columns.length} Columns
                    </Badge>
                  </div>

                  <div className="flex items-center gap-2">
                    {primaryKeys.length > 0 && (
                      <Badge variant="violet" size="sm">
                        <Key className="w-3 h-3" /> PK ({primaryKeys.join(', ')})
                      </Badge>
                    )}
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </div>

                {/* Expanded Table Column & Relationship Details */}
                {isExpanded && (
                  <div className="p-4 border-t border-white/[0.05] bg-space-deep/60 space-y-4 animate-fade-in-up">
                    {/* Columns List */}
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 font-heading">
                        Columns
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                        {columns.map((col) => {
                          const isPk = primaryKeys.includes(col.name);
                          return (
                            <div
                              key={col.name}
                              className="p-2.5 rounded-xl bg-space-surface/90 border border-white/[0.05] flex items-center justify-between text-xs"
                            >
                              <div className="flex items-center gap-2 min-w-0">
                                {isPk ? (
                                  <Key className="w-3.5 h-3.5 text-violet-400 shrink-0" />
                                ) : (
                                  <div className="w-1.5 h-1.5 rounded-full bg-slate-600 shrink-0" />
                                )}
                                <span className="font-mono text-slate-200 truncate">
                                  {col.name}
                                </span>
                              </div>
                              <span className="text-[10px] font-mono text-violet-300 bg-violet-500/10 px-2 py-0.5 rounded border border-violet-500/20">
                                {col.type}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Foreign Keys List */}
                    {foreignKeys.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 font-heading">
                          <Link2 className="w-3.5 h-3.5 text-cyan-400" /> Foreign Relationships
                        </h4>
                        <div className="space-y-1.5">
                          {foreignKeys.map((fk, idx) => {
                            const fkCols = Array.isArray(fk.constrained_columns)
                              ? fk.constrained_columns.join(', ')
                              : Array.isArray(fk.column)
                              ? fk.column.join(', ')
                              : fk.column || '';

                            const refCols = Array.isArray(fk.referred_columns)
                              ? fk.referred_columns.join(', ')
                              : fk.referred_columns || '';

                            return (
                              <div
                                key={idx}
                                className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-300 flex items-center gap-2"
                              >
                                <span>
                                  {fkCols} → {fk.referred_table}({refCols})
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </StateWrapper>
    </div>
  );
};
