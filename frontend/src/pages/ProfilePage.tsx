import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, Calendar, Shield, LogOut } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

export const ProfilePage: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-12 animate-fade-in-up">
      <Card glowColor="violet">
        <CardHeader>
          <div className="flex items-center gap-4">
            {/* Spinning gradient ring around avatar */}
            <div className="relative p-1 rounded-full bg-gradient-to-tr from-violet-600 via-cyan-400 to-emerald-400 shadow-xl shadow-violet-500/20">
              <div className="w-16 h-16 rounded-full bg-space-deep flex items-center justify-center font-extrabold text-white text-2xl font-heading">
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </div>
            </div>
            <div>
              <CardTitle className="text-xl">{user?.username}</CardTitle>
              <CardDescription>{user?.email}</CardDescription>
              <div className="flex items-center gap-2 mt-2">
                <Badge variant="emerald">Active Account</Badge>
                <Badge variant="violet" pulse>Enterprise Tier</Badge>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-space-surface/80 border border-white/[0.05] space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1.5 font-heading">
                <User className="w-3.5 h-3.5 text-violet-400" /> Account ID
              </span>
              <p className="text-xs font-mono text-slate-200 truncate">{user?.id}</p>
            </div>

            <div className="p-4 rounded-xl bg-space-surface/80 border border-white/[0.05] space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1.5 font-heading">
                <Mail className="w-3.5 h-3.5 text-violet-400" /> Email Address
              </span>
              <p className="text-xs font-mono text-slate-200 truncate">{user?.email}</p>
            </div>

            <div className="p-4 rounded-xl bg-space-surface/80 border border-white/[0.05] space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1.5 font-heading">
                <Calendar className="w-3.5 h-3.5 text-violet-400" /> Registration Date
              </span>
              <p className="text-xs font-mono text-slate-200">
                {user?.created_at
                  ? new Date(user.created_at).toLocaleDateString()
                  : 'N/A'}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-space-surface/80 border border-white/[0.05] space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1.5 font-heading">
                <Shield className="w-3.5 h-3.5 text-violet-400" /> Security Status
              </span>
              <p className="text-xs font-mono text-emerald-400">JWT Token Authenticated</p>
            </div>
          </div>

          <div className="pt-4 border-t border-white/[0.05] flex justify-end">
            <Button
              variant="danger"
              onClick={logout}
              leftIcon={<LogOut className="w-4 h-4" />}
            >
              Sign Out of Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
