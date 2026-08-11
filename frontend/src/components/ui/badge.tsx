import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'gold' | 'violet' | 'cyan' | 'emerald' | 'rose' | 'gray';
  size?: 'sm' | 'md';
  className?: string;
  pulse?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'violet',
  size = 'md',
  className = '',
  pulse = false,
}) => {
  const variants = {
    gold: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    violet: 'bg-violet-500/10 text-violet-300 border-violet-500/30',
    cyan: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
    emerald: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
    rose: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
    gray: 'bg-slate-800/80 text-slate-300 border-slate-700/60',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 font-semibold tracking-wide rounded-full border shadow-sm ${
        variants[variant]
      } ${sizes[size]} ${pulse ? 'animate-glow-pulse' : ''} ${className}`}
    >
      {children}
    </span>
  );
};
