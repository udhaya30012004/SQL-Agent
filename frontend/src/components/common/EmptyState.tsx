import React from 'react';
import { LucideIcon, Inbox } from 'lucide-react';
import { Button } from '../ui/button';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Inbox,
  title,
  description,
  actionLabel,
  onAction,
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center text-center p-8 rounded-2xl bg-space-surface/60 border border-white/[0.06] shadow-xl backdrop-blur-lg ${className}`}
    >
      <div className="w-14 h-14 rounded-2xl bg-violet-500/10 border border-violet-500/25 flex items-center justify-center mb-4 text-violet-400 shadow-inner">
        <Icon className="w-7 h-7" />
      </div>
      <h3 className="text-lg font-bold text-slate-100 mb-1 font-heading">{title}</h3>
      <p className="text-sm text-slate-400 max-w-sm mb-6 leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
