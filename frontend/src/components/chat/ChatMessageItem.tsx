import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User as UserIcon, Copy, Check, AlertCircle } from 'lucide-react';
import { ChatMessage } from '../../types/chat';
import { ChartViewer } from './ChartViewer';

interface ChatMessageItemProps {
  message: ChatMessage;
}

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({ message }) => {
  const [copiedAnswer, setCopiedAnswer] = useState<boolean>(false);
  const isUser = message.role === 'user';

  const handleCopyAnswer = () => {
    navigator.clipboard.writeText(message.content);
    setCopiedAnswer(true);
    setTimeout(() => setCopiedAnswer(false), 2000);
  };

  const formattedTime = new Date(message.created_at).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div
      className={`flex gap-3 md:gap-4 py-5 transition-all duration-300 animate-fade-in-up ${
        isUser
          ? 'justify-end'
          : 'max-w-full'
      }`}
    >
      {/* Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold shrink-0 bg-white text-slate-950 shadow-sm">
          <Bot className="w-4 h-4" />
        </div>
      )}

      {/* Message Content Container */}
      <div className={`min-w-0 space-y-3 ${isUser ? 'max-w-[78%]' : 'flex-1'}`}>
        <div className={`flex items-center gap-2 ${isUser ? 'justify-end' : 'justify-between'}`}>
          <div className="flex items-center gap-2">
            {!isUser && (
              <span className="text-xs font-bold text-slate-200 font-heading">
                AI Data Analyst
              </span>
            )}
            <span className="text-[10px] text-slate-500">{formattedTime}</span>
          </div>

          {!isUser && (
            <button
              onClick={handleCopyAnswer}
              className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white px-2 py-0.5 rounded hover:bg-white/5 transition-colors"
            >
              {copiedAnswer ? (
                <Check className="w-3 h-3 text-emerald-400" />
              ) : (
                <Copy className="w-3 h-3" />
              )}
              <span>{copiedAnswer ? 'Copied' : 'Copy'}</span>
            </button>
          )}
        </div>

        {/* Error Banner if message has error */}
        {message.error && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{message.error}</span>
          </div>
        )}

        {/* Main Text Content / Markdown */}
        <div
          className={`prose prose-invert prose-sm max-w-none leading-relaxed font-normal ${
            isUser
              ? 'rounded-3xl rounded-br-md bg-white text-slate-950 prose-p:text-slate-950 px-4 py-3 shadow-sm'
              : 'text-slate-200 prose-headings:text-slate-100 prose-strong:text-white'
          }`}
        >
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Plotly Chart Component */}
        {!isUser && message.chart_path && (
          <ChartViewer
            chartPath={message.chart_path}
            chartSpec={message.chart_spec}
          />
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold shrink-0 bg-slate-800 text-slate-300 border border-white/10">
          <UserIcon className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};
