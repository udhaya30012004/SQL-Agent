import React, { useState } from 'react';
import { Copy, Check, Terminal, ChevronDown, ChevronRight } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface SqlQueryCardProps {
  sqlQuery: string;
}

export const SqlQueryCard: React.FC<SqlQueryCardProps> = ({ sqlQuery }) => {
  const [copied, setCopied] = useState<boolean>(false);
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(sqlQuery);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-xl bg-space-deep border border-cyan-500/25 overflow-hidden shadow-md my-2.5 transition-all duration-300 glow-cyan">
      {/* Clickable Header Bar Toggle */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between px-4 py-2 bg-space-surface/90 hover:bg-space-elevated/90 cursor-pointer border-b border-white/[0.05] select-none transition-colors group"
      >
        <div className="flex items-center gap-2.5">
          <Terminal className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform duration-200" />
          <span className="text-xs font-mono font-semibold text-cyan-300 group-hover:text-cyan-200 font-heading">
            {isOpen ? 'Hide Generated PostgreSQL Query' : 'View Generated PostgreSQL Query'}
          </span>
          <span className="text-[10px] text-slate-400 font-mono bg-space-deep px-2 py-0.5 rounded border border-white/[0.05]">
            SQL
          </span>
        </div>

        <div className="flex items-center gap-3">
          {isOpen && (
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-medium text-slate-300 hover:text-white bg-space-elevated hover:bg-space-hover rounded-md border border-white/10 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-emerald-400" />
                  <span className="text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3 text-slate-400" />
                  <span>Copy SQL</span>
                </>
              )}
            </button>
          )}

          {isOpen ? (
            <ChevronDown className="w-4 h-4 text-cyan-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-cyan-400 transition-colors" />
          )}
        </div>
      </div>

      {/* Collapsible Syntax-Highlighted Code Block */}
      {isOpen && (
        <div className="p-1 text-xs font-mono overflow-x-auto max-h-80 border-t border-white/[0.05] bg-space-deep/80 animate-fade-in-up">
          <SyntaxHighlighter
            language="sql"
            style={vscDarkPlus}
            customStyle={{
              margin: 0,
              padding: '12px',
              background: 'transparent',
              fontSize: '12px',
              lineHeight: '1.5',
            }}
          >
            {sqlQuery}
          </SyntaxHighlighter>
        </div>
      )}
    </div>
  );
};
