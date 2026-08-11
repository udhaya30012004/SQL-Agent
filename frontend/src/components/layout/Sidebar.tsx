import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquarePlus,
  Database,
  FileSpreadsheet,
  Settings,
  User as UserIcon,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Search,
  Trash2,
  Sparkles,
  Bot,
  Pin,
  ExternalLink,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { ChatSession } from '../../types/chat';
import { chatApi } from '../../api/chatApi';
import { SkeletonLoader } from '../common/SkeletonLoader';
import { Dialog } from '../ui/dialog';
import { Button } from '../ui/button';

interface SidebarProps {
  sessions: ChatSession[];
  isLoadingSessions: boolean;
  onRefreshSessions: () => void;
  activeConnection: string | null;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  isLoadingSessions,
  onRefreshSessions,
  activeConnection,
}) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [deleteModalSessionId, setDeleteModalSessionId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [pinnedSessionIds, setPinnedSessionIds] = useState<string[]>([]);

  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleCreateNewChat = async (agentType: 'sql' | 'pandas') => {
    try {
      const newSession = await chatApi.createSession({
        agent_type: agentType,
        title: `New ${agentType.toUpperCase()} Analysis`,
      });
      onRefreshSessions();
      navigate(`/chat/${newSession.id}`);
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleDeleteSession = async () => {
    if (!deleteModalSessionId) return;
    setIsDeleting(true);
    try {
      await chatApi.deleteSession(deleteModalSessionId);
      onRefreshSessions();
      if (location.pathname.includes(deleteModalSessionId)) {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    } finally {
      setIsDeleting(false);
      setDeleteModalSessionId(null);
    }
  };

  const togglePinSession = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    setPinnedSessionIds((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const filteredSessions = sessions.filter((s) =>
    (s.title || 'Untitled Chat').toLowerCase().includes(searchQuery.toLowerCase())
  );

  const pinnedSessions = filteredSessions.filter((s) => pinnedSessionIds.includes(s.id));
  const recentSessions = filteredSessions.filter((s) => !pinnedSessionIds.includes(s.id));

  return (
    <>
      <aside
        className={`relative flex flex-col h-screen bg-space-surface/95 border-r border-white/[0.06] transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] z-30 select-none backdrop-blur-xl ${
          isCollapsed ? 'w-20' : 'w-72'
        }`}
      >
        {/* Subtle gradient overlay at bottom */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-violet-950/20 pointer-events-none rounded-r-xl" />

        {/* Top Header / Logo */}
        <div className="relative flex items-center justify-between p-4 border-b border-white/[0.04]">
          <div
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-cyan-400 p-0.5 shadow-lg shadow-violet-500/25 group-hover:shadow-violet-500/40 group-hover:scale-105 transition-all duration-300">
              <div className="w-full h-full bg-space-deep rounded-[10px] flex items-center justify-center">
                <Bot className="w-5 h-5 text-violet-400" />
              </div>
            </div>
            {!isCollapsed && (
              <div>
                <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5 font-heading">
                  Agentic DA
                  <span className="text-[10px] font-semibold text-violet-300 bg-violet-500/15 px-1.5 py-0.5 rounded-full border border-violet-400/25 animate-glow-pulse">
                    PRO
                  </span>
                </h1>
                <p className="text-[11px] text-slate-500">Enterprise AI Analyst</p>
              </div>
            )}
          </div>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-white/5 transition-all duration-200"
          >
            {isCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>

        {/* Quick Agent Actions */}
        <div className="relative p-3 space-y-2 border-b border-white/[0.04]">
          <button
            onClick={() => handleCreateNewChat('sql')}
            className={`w-full flex items-center justify-center gap-2.5 py-2.5 px-3 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white font-bold text-xs shadow-lg shadow-violet-500/20 hover:shadow-violet-500/35 transition-all duration-300 transform active:scale-95 shimmer-effect ${
              isCollapsed ? 'px-0' : ''
            }`}
          >
            <MessageSquarePlus className="w-4 h-4" />
            {!isCollapsed && <span>New SQL Chat</span>}
          </button>

          {!isCollapsed && (
            <div className="grid grid-cols-2 gap-1.5 pt-1">
              <button
                onClick={() => navigate('/database')}
                className="flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg bg-space-elevated hover:bg-space-hover text-slate-400 hover:text-white text-[11px] font-medium border border-white/[0.05] transition-all duration-200"
              >
                <Database className="w-3.5 h-3.5 text-violet-400" />
                Connect DB
              </button>
              <button
                onClick={() => navigate('/pandas')}
                className="flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg bg-space-elevated hover:bg-space-hover text-slate-400 hover:text-white text-[11px] font-medium border border-white/[0.05] transition-all duration-200"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-cyan-400" />
                CSV Agent
              </button>
            </div>
          )}
        </div>

        {/* Active Database Badge Indicator */}
        {!isCollapsed && (
          <div className="relative mx-3 my-2 p-2.5 rounded-xl bg-space-elevated/60 border border-white/[0.04] flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-2 h-2 rounded-full bg-emerald-400 status-dot-pulse shrink-0" />
              <span className="text-[11px] text-slate-500 truncate">
                {activeConnection ? 'Pagila PostgreSQL' : 'Default Database'}
              </span>
            </div>
            <span className="text-[10px] text-emerald-400 font-mono bg-emerald-400/10 px-1.5 py-0.5 rounded border border-emerald-400/20">
              ONLINE
            </span>
          </div>
        )}

        {/* Main Navigation Links */}
        <div className="relative px-3 py-2 space-y-1">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all duration-300 relative ${
                isActive
                  ? 'bg-violet-500/10 text-violet-300 border border-violet-500/20'
                  : 'text-slate-500 hover:text-slate-200 hover:bg-white/[0.03]'
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-gradient-to-b from-violet-400 to-cyan-400" />
                )}
                <LayoutDashboard className="w-4 h-4" />
                {!isCollapsed && <span>Dashboard</span>}
              </>
            )}
          </NavLink>
        </div>

        {/* Search Session Filter */}
        {!isCollapsed && (
          <div className="relative px-3 py-1">
            <div className="relative flex items-center">
              <Search className="w-3.5 h-3.5 absolute left-3 text-slate-600" />
              <input
                type="text"
                placeholder="Search chats..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-space-deep text-xs text-slate-200 placeholder:text-slate-600 pl-8 pr-3 py-1.5 rounded-lg border border-white/[0.05] outline-none focus:border-violet-500/40 transition-colors duration-200"
              />
            </div>
          </div>
        )}

        {/* Conversation Sessions List */}
        {!isCollapsed && (
          <div className="relative flex-1 overflow-y-auto px-3 py-2 space-y-4">
            {isLoadingSessions ? (
              <SkeletonLoader variant="list" count={4} />
            ) : (
              <>
                {/* Pinned Sessions */}
                {pinnedSessions.length > 0 && (
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-violet-400/80 px-2 mb-1 flex items-center gap-1 font-heading">
                      <Pin className="w-3 h-3" /> Pinned Chats
                    </p>
                    <div className="space-y-0.5">
                      {pinnedSessions.map((session) => (
                        <SessionItem
                          key={session.id}
                          session={session}
                          isPinned={true}
                          onTogglePin={togglePinSession}
                          onDelete={(id) => setDeleteModalSessionId(id)}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Recent Sessions */}
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600 px-2 mb-1 font-heading">
                    Recent Sessions
                  </p>
                  {recentSessions.length === 0 ? (
                    <p className="text-[11px] text-slate-600 italic px-2 py-1">
                      No chat sessions found.
                    </p>
                  ) : (
                    <div className="space-y-0.5">
                      {recentSessions.map((session) => (
                        <SessionItem
                          key={session.id}
                          session={session}
                          isPinned={false}
                          onTogglePin={togglePinSession}
                          onDelete={(id) => setDeleteModalSessionId(id)}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}

        {/* Footer User Profile & Logout */}
        <div className="relative p-3 border-t border-white/[0.04] bg-space-deep/40 mt-auto">
          {!isCollapsed ? (
            <div className="flex items-center justify-between">
              <div
                onClick={() => navigate('/profile')}
                className="flex items-center gap-2.5 cursor-pointer hover:opacity-80 transition-opacity duration-200 min-w-0"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center font-bold text-white text-xs shadow-md shrink-0">
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-slate-200 truncate">
                    {user?.username}
                  </p>
                  <p className="text-[10px] text-slate-600 truncate">{user?.email}</p>
                </div>
              </div>
              <button
                onClick={logout}
                title="Logout"
                className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all duration-200"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <button
                onClick={() => navigate('/profile')}
                className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 text-white font-bold text-xs flex items-center justify-center"
              >
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </button>
              <button
                onClick={logout}
                className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Delete Confirmation Modal */}
      <Dialog
        isOpen={!!deleteModalSessionId}
        onClose={() => setDeleteModalSessionId(null)}
        title="Delete Session"
        description="Are you sure you want to delete this chat session? All question history will be permanently erased."
      >
        <div className="flex justify-end gap-3 mt-4">
          <Button variant="ghost" onClick={() => setDeleteModalSessionId(null)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            isLoading={isDeleting}
            onClick={handleDeleteSession}
          >
            Delete Session
          </Button>
        </div>
      </Dialog>
    </>
  );
};

interface SessionItemProps {
  session: ChatSession;
  isPinned: boolean;
  onTogglePin: (e: React.MouseEvent, id: string) => void;
  onDelete: (id: string) => void;
}

const SessionItem: React.FC<SessionItemProps> = ({
  session,
  isPinned,
  onTogglePin,
  onDelete,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = location.pathname.includes(session.id);

  return (
    <div
      onClick={() => navigate(`/chat/${session.id}`)}
      className={`group flex items-center justify-between px-2.5 py-2 rounded-xl text-xs cursor-pointer transition-all duration-300 relative ${
        isActive
          ? 'bg-violet-500/12 text-violet-300 font-semibold border border-violet-500/25'
          : 'text-slate-500 hover:text-slate-200 hover:bg-white/[0.03]'
      }`}
    >
      {/* Active indicator bar */}
      {isActive && (
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-4 rounded-r-full bg-gradient-to-b from-violet-400 to-cyan-400" />
      )}

      <div className="flex items-center gap-2 min-w-0">
        {session.agent_type === 'sql' ? (
          <Bot className="w-3.5 h-3.5 text-violet-400 shrink-0" />
        ) : (
          <FileSpreadsheet className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
        )}
        <span className="truncate">{session.title || 'Untitled Chat'}</span>
      </div>

      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <button
          onClick={(e) => onTogglePin(e, session.id)}
          className={`p-1 hover:text-violet-400 transition-colors ${
            isPinned ? 'text-violet-400 opacity-100' : 'text-slate-600'
          }`}
          title={isPinned ? 'Unpin Chat' : 'Pin Chat'}
        >
          <Pin className="w-3 h-3" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(session.id);
          }}
          className="p-1 text-slate-600 hover:text-rose-400 transition-colors"
          title="Delete Chat"
        >
          <Trash2 className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
};
