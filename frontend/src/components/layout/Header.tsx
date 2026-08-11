import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, User, Sparkles } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { Badge } from '../ui/badge';

interface HeaderProps {
  title?: string;
  subtitle?: string;
  activeConnection?: string | null;
}

export const Header: React.FC<HeaderProps> = ({
  title = 'Dashboard',
  subtitle = 'Welcome back to your AI Data Analyst workspace',
  activeConnection,
}) => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="relative h-16 px-6 bg-space-surface/60 border-b border-white/[0.06] backdrop-blur-xl flex items-center justify-between z-20 shrink-0">
      {/* Subtle gradient glow line at bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-violet-500/30 to-transparent" />

      <div>
        <h2 className="text-base font-bold text-slate-100 tracking-tight flex items-center gap-2 font-heading">
          {title}
        </h2>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Database Connection Quick Status */}
        <div
          onClick={() => navigate('/database')}
          className="cursor-pointer group flex items-center gap-2 px-3 py-1.5 rounded-xl bg-space-elevated/80 border border-white/[0.06] hover:border-violet-500/30 transition-all duration-300"
        >
          <Database className="w-3.5 h-3.5 text-violet-400 group-hover:scale-110 transition-transform duration-300" />
          <div className="text-left hidden sm:block">
            <p className="text-[10px] uppercase font-bold tracking-wider text-slate-500 font-heading">
              Target Database
            </p>
            <p className="text-xs font-semibold text-slate-200">
              {activeConnection ? 'Pagila PostgreSQL' : 'Default Postgres'}
            </p>
          </div>
          <Badge variant="emerald" size="sm" className="ml-1">
            Connected
          </Badge>
        </div>

        {/* Profile Action Pill */}
        <div
          onClick={() => navigate('/profile')}
          className="flex items-center gap-2.5 p-1.5 pr-3 rounded-full bg-space-elevated border border-white/[0.06] hover:border-violet-500/25 cursor-pointer transition-all duration-300 group"
        >
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 text-white font-bold text-xs flex items-center justify-center shadow-md group-hover:shadow-violet-500/30 transition-shadow duration-300">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <span className="text-xs font-medium text-slate-200 hidden sm:inline">
            {user?.username}
          </span>
        </div>
      </div>
    </header>
  );
};
