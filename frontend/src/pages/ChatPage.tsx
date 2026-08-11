import React, { useState, useEffect, useRef } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { Bot, RefreshCw, AlertCircle, ArrowLeft, Loader2, Sparkles } from 'lucide-react';
import { chatApi } from '../api/chatApi';
import { ChatMessage, ChatSession } from '../types/chat';
import { ChatResponseMode } from '../types/chat';
import { ChatMessageItem } from '../components/chat/ChatMessageItem';
import { ChatInput } from '../components/chat/ChatInput';
import { StateWrapper } from '../components/common/StateWrapper';
import { Button } from '../components/ui/button';

export const ChatPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoadingSession, setIsLoadingSession] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<any>(null);
  const [isAsking, setIsAsking] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSession = async () => {
    if (!sessionId) return;
    setIsLoadingSession(true);
    setIsError(false);
    setError(null);
    try {
      const data = await chatApi.getSessionById(sessionId);
      setSession(data);
      setMessages(data.messages || []);
    } catch (err) {
      setIsError(true);
      setError(err);
    } finally {
      setIsLoadingSession(false);
    }
  };

  useEffect(() => {
    fetchSession();
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isAsking]);

  // Handle URL query parameter e.g., ?q=Show+top+revenue+customers
  useEffect(() => {
    const initialQuery = searchParams.get('q');
    if (initialQuery && session && messages.length === 0 && !isAsking) {
      handleSendMessage(initialQuery);
    }
  }, [searchParams, session]);

  const handleSendMessage = async (
    question: string,
    connectionString?: string,
    responseMode: ChatResponseMode = 'both'
  ) => {
    if (!sessionId) return;

    // Optimistically add user message to UI immediately
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      session_id: sessionId,
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setIsAsking(true);

    try {
      const assistantMsg = await chatApi.askAgent({
        session_id: sessionId,
        question,
        connection_string: connectionString,
        response_mode: responseMode,
      });

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errMsg =
        err?.response?.data?.detail || err?.message || 'Agent execution failed.';
      const tempErrorMsg: ChatMessage = {
        id: Date.now() + 1,
        session_id: sessionId,
        role: 'assistant',
        content: `Error: ${errMsg}`,
        error: errMsg,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempErrorMsg]);
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto animate-fade-in-up">
      {/* Top Session Title Header */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-base font-bold text-slate-100 flex items-center gap-2 font-heading">
              {session?.title || 'Conversational Session'}
              <span className="text-[10px] font-bold uppercase tracking-wider text-violet-300 bg-violet-500/10 px-2 py-0.5 rounded border border-violet-500/20 font-mono">
                {session?.agent_type || 'SQL'} AGENT
              </span>
            </h1>
            <p className="text-xs text-slate-500">
              Session ID: <span className="font-mono">{sessionId}</span>
            </p>
          </div>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={fetchSession}
          leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
        >
          Refresh Log
        </Button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-4 scroll-smooth">
        <StateWrapper
          isLoading={isLoadingSession}
          isError={isError}
          error={error}
          isEmpty={messages.length === 0 && !isAsking}
          onRetry={fetchSession}
          isRetrying={isLoadingSession}
          skeletonVariant="chat"
          skeletonCount={3}
          emptyTitle="Start a new conversation"
          emptyDescription="Type your natural language data query below to trigger the AI agent workflow."
          emptyIcon={Sparkles}
        >
          {messages.map((msg) => (
            <ChatMessageItem key={msg.id} message={msg} />
          ))}

          {/* Thinking Indicator */}
          {isAsking && (
            <div className="flex items-center gap-3 p-4 rounded-2xl bg-space-surface/80 border border-violet-500/30 text-violet-300 text-xs animate-pulse shadow-lg glow-violet">
              <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
              <div className="space-y-0.5">
                <p className="font-bold font-heading">Working on your query...</p>
                <p className="text-[11px] text-slate-400">
                  Generating SQL, executing it, and preparing the selected output.
                </p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </StateWrapper>
      </div>

      {/* Input Box */}
      <div className="pt-4 mt-auto">
        <ChatInput onSendMessage={handleSendMessage} isLoading={isAsking} />
      </div>
    </div>
  );
};
