import React from 'react';

interface SkeletonLoaderProps {
  variant?: 'card' | 'table' | 'list' | 'chat' | 'schema';
  count?: number;
  className?: string;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  variant = 'card',
  count = 3,
  className = '',
}) => {
  const items = Array.from({ length: count });

  if (variant === 'table') {
    return (
      <div className={`w-full space-y-3 ${className}`}>
        <div className="h-10 bg-space-elevated/80 rounded-lg shimmer-effect" />
        {items.map((_, i) => (
          <div key={i} className="h-12 bg-space-elevated/40 rounded-lg shimmer-effect" />
        ))}
      </div>
    );
  }

  if (variant === 'list') {
    return (
      <div className={`space-y-2 ${className}`}>
        {items.map((_, i) => (
          <div
            key={i}
            className="flex items-center gap-3 p-3 rounded-xl bg-space-elevated/40 shimmer-effect"
          >
            <div className="w-8 h-8 rounded-lg bg-space-elevated" />
            <div className="flex-1 space-y-1.5">
              <div className="h-4 w-3/4 bg-space-elevated rounded" />
              <div className="h-3 w-1/2 bg-space-elevated/50 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (variant === 'chat') {
    return (
      <div className={`space-y-4 p-4 ${className}`}>
        {items.map((_, i) => (
          <div
            key={i}
            className={`flex gap-3 max-w-[80%] ${
              i % 2 === 0 ? 'ml-auto flex-row-reverse' : ''
            }`}
          >
            <div className="w-9 h-9 rounded-full bg-space-elevated shrink-0 shimmer-effect" />
            <div className="space-y-2 p-4 rounded-2xl bg-space-surface/60 border border-white/[0.05] w-full shimmer-effect">
              <div className="h-4 w-5/6 bg-space-elevated rounded" />
              <div className="h-4 w-2/3 bg-space-elevated/70 rounded" />
              <div className="h-4 w-1/2 bg-space-elevated/50 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (variant === 'schema') {
    return (
      <div className={`space-y-3 ${className}`}>
        {items.map((_, i) => (
          <div
            key={i}
            className="p-4 rounded-xl bg-space-surface/40 border border-white/[0.05] space-y-3 shimmer-effect"
          >
            <div className="flex justify-between items-center">
              <div className="h-5 w-40 bg-violet-500/20 rounded" />
              <div className="h-4 w-16 bg-space-elevated rounded-full" />
            </div>
            <div className="space-y-2 pt-2 border-t border-white/[0.05]">
              <div className="h-3 w-full bg-space-elevated/60 rounded" />
              <div className="h-3 w-4/5 bg-space-elevated/60 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 md:grid-cols-3 gap-4 ${className}`}>
      {items.map((_, i) => (
        <div
          key={i}
          className="p-6 rounded-2xl bg-space-surface/50 border border-white/[0.05] space-y-3 shimmer-effect"
        >
          <div className="h-5 w-1/3 bg-violet-500/20 rounded" />
          <div className="h-8 w-2/3 bg-space-elevated rounded" />
          <div className="h-4 w-full bg-space-elevated/50 rounded" />
        </div>
      ))}
    </div>
  );
};
