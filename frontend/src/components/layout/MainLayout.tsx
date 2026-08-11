import React, { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { chatApi } from '../../api/chatApi';
import { ChatSession } from '../../types/chat';
import { motion, AnimatePresence } from 'framer-motion';

export const MainLayout: React.FC = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState<boolean>(true);
  const [activeConnection, setActiveConnection] = useState<string | null>(
    localStorage.getItem('connection_string') || null
  );

  const location = useLocation();

  const fetchSessions = async () => {
    try {
      const data = await chatApi.getSessions();
      setSessions(data);
    } catch (err) {
      console.error('Failed to load chat sessions:', err);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  // Compute header titles based on active route
  const getHeaderInfo = () => {
    const path = location.pathname;
    if (path.includes('/dashboard')) {
      return { title: 'Dashboard Overview', subtitle: 'AI Analytics platform summary & quick templates' };
    }
    if (path.includes('/database')) {
      return { title: 'Database Connections & Schema Explorer', subtitle: 'Test live connections and inspect metadata tables' };
    }
    if (path.includes('/pandas')) {
      return { title: 'Pandas CSV Dataset Workspace', subtitle: 'Upload CSV spreadsheets and run AI data transformations' };
    }
    if (path.includes('/chat')) {
      return { title: 'Conversational AI Agent Workspace', subtitle: 'Natural Language SQL Generation & Interactive Plotly Charts' };
    }
    if (path.includes('/profile')) {
      return { title: 'User Account Profile', subtitle: 'Manage credentials and session access' };
    }
    if (path.includes('/settings')) {
      return { title: 'Platform Settings', subtitle: 'API keys, theme preferences, and configuration' };
    }
    return { title: 'Agentic Data Analyst', subtitle: 'Enterprise AI Data Science Engine' };
  };

  const headerInfo = getHeaderInfo();

  return (
    <div className="flex h-screen w-screen bg-space-deep text-slate-100 overflow-hidden dot-grid-bg">
      {/* Floating background orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="bg-orb bg-orb-violet w-[500px] h-[500px] -top-32 -left-32" />
        <div className="bg-orb bg-orb-cyan w-[400px] h-[400px] top-1/2 -right-24" />
        <div className="bg-orb bg-orb-emerald w-[350px] h-[350px] -bottom-20 left-1/3" />
      </div>

      <Sidebar
        sessions={sessions}
        isLoadingSessions={isLoadingSessions}
        onRefreshSessions={fetchSessions}
        activeConnection={activeConnection}
      />

      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden relative z-10">
        <Header
          title={headerInfo.title}
          subtitle={headerInfo.subtitle}
          activeConnection={activeConnection}
        />

        <main className="flex-1 overflow-y-auto p-6 relative scroll-smooth">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.3, ease: [0.32, 0.72, 0, 1] }}
              className="h-full"
            >
              <Outlet context={{ onRefreshSessions: fetchSessions }} />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
};
