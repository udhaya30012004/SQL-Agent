import React, { useState, useRef } from 'react';
import { Send, Database, MessageSquareText, BarChart3, PanelsTopLeft } from 'lucide-react';
import { Button } from '../ui/button';
import { ChatResponseMode } from '../../types/chat';

interface ChatInputProps {
  onSendMessage: (
    question: string,
    connectionString?: string,
    responseMode?: ChatResponseMode
  ) => void;
  isLoading: boolean;
  disabled?: boolean;
}

const responseModeOptions: Array<{
  value: ChatResponseMode;
  label: string;
  icon: React.ReactNode;
}> = [
  {
    value: 'answer',
    label: 'Answer',
    icon: <MessageSquareText className="w-3.5 h-3.5" />,
  },
  {
    value: 'chart',
    label: 'Chart',
    icon: <BarChart3 className="w-3.5 h-3.5" />,
  },
  {
    value: 'both',
    label: 'Both',
    icon: <PanelsTopLeft className="w-3.5 h-3.5" />,
  },
];

const getInitialResponseMode = (): ChatResponseMode => {
  const savedMode = localStorage.getItem('chat_response_mode');

  if (savedMode === 'answer' || savedMode === 'chart' || savedMode === 'both') {
    return savedMode;
  }

  return 'both';
};

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  disabled = false,
}) => {
  const [question, setQuestion] = useState<string>('');
  const [showDbInput, setShowDbInput] = useState<boolean>(false);
  const [customConnStr, setCustomConnStr] = useState<string>(
    localStorage.getItem('connection_string') || ''
  );
  const [responseMode, setResponseMode] = useState<ChatResponseMode>(
    getInitialResponseMode
  );

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!question.trim() || isLoading || disabled) return;

    onSendMessage(
      question.trim(),
      customConnStr.trim() ? customConnStr.trim() : undefined,
      responseMode
    );
    setQuestion('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuestion(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        160
      )}px`;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-3">
      {/* Optional Custom Database Connection String Expandable Bar */}
      {showDbInput && (
        <div className="p-3 rounded-xl bg-space-surface border border-violet-500/30 flex items-center gap-2 animate-fade-in-up">
          <Database className="w-4 h-4 text-violet-400 shrink-0" />
          <input
            type="text"
            placeholder="postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
            value={customConnStr}
            onChange={(e) => {
              setCustomConnStr(e.target.value);
              localStorage.setItem('connection_string', e.target.value);
            }}
            className="w-full bg-transparent text-xs font-mono text-slate-200 placeholder:text-slate-600 outline-none"
          />
        </div>
      )}

      {/* Main Input Box */}
      <div className="relative rounded-[1.5rem] bg-[#10111f]/95 border border-white/[0.08] focus-within:border-violet-400/60 focus-within:ring-4 focus-within:ring-violet-500/10 shadow-2xl transition-all duration-300 p-2 backdrop-blur-xl">
        <textarea
          ref={textareaRef}
          value={question}
          onChange={handleTextareaChange}
          onKeyDown={handleKeyDown}
          disabled={isLoading || disabled}
          placeholder="Ask any natural-language question about your database or CSV dataset..."
          rows={1}
          className="w-full bg-transparent text-sm text-slate-100 placeholder:text-slate-500 px-3 py-3 outline-none resize-none max-h-40 min-h-[52px]"
        />

        <div className="flex flex-col gap-3 pt-2 border-t border-white/[0.04] px-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex items-center rounded-xl bg-black/20 p-1 border border-white/[0.06]">
              {responseModeOptions.map((option) => {
                const isActive = responseMode === option.value;

                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => {
                      setResponseMode(option.value);
                      localStorage.setItem('chat_response_mode', option.value);
                    }}
                    disabled={isLoading || disabled}
                    className={`h-8 px-3 rounded-lg inline-flex items-center gap-1.5 text-[11px] font-semibold transition-colors ${
                      isActive
                        ? 'bg-white text-slate-950 shadow-sm'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-white/[0.06]'
                    }`}
                    title={`Return ${option.label.toLowerCase()}`}
                  >
                    {option.icon}
                    <span>{option.label}</span>
                  </button>
                );
              })}
            </div>

            <button
              type="button"
              onClick={() => setShowDbInput(!showDbInput)}
              className={`h-8 flex items-center gap-1 px-2.5 text-[11px] font-medium rounded-lg transition-all duration-200 ${
                showDbInput || customConnStr
                  ? 'bg-violet-500/15 text-violet-300 border border-violet-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              }`}
            >
              <Database className="w-3.5 h-3.5" />
              <span>{customConnStr ? 'Custom DB String' : 'Specify Database'}</span>
            </button>
          </div>

          <Button
            type="submit"
            size="sm"
            isLoading={isLoading}
            disabled={!question.trim() || disabled}
            rightIcon={<Send className="w-3.5 h-3.5" />}
            className="self-end sm:self-auto"
          >
            Ask
          </Button>
        </div>
      </div>
    </form>
  );
};
