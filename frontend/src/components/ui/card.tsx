import React from 'react';

export const Card: React.FC<{
  children: React.ReactNode;
  className?: string;
  goldGlow?: boolean;
  glowColor?: 'violet' | 'cyan' | 'emerald' | 'none';
}> = ({ children, className = '', goldGlow = false, glowColor = 'none' }) => {
  const glowStyles = {
    violet: 'border-violet-500/25 shadow-[0_0_30px_-5px_rgba(139,92,246,0.15)] hover:shadow-[0_0_40px_-5px_rgba(139,92,246,0.25)]',
    cyan: 'border-cyan-500/25 shadow-[0_0_30px_-5px_rgba(34,211,238,0.15)] hover:shadow-[0_0_40px_-5px_rgba(34,211,238,0.25)]',
    emerald: 'border-emerald-500/25 shadow-[0_0_30px_-5px_rgba(52,211,153,0.15)] hover:shadow-[0_0_40px_-5px_rgba(52,211,153,0.25)]',
    none: 'border-white/[0.07] shadow-xl hover:shadow-2xl',
  };

  const resolvedGlow = goldGlow ? 'violet' : glowColor;

  return (
    <div
      className={`rounded-2xl bg-space-surface/80 border backdrop-blur-xl transition-all duration-300 hover-lift ${glowStyles[resolvedGlow]} ${className}`}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`p-6 border-b border-white/5 ${className}`}>{children}</div>
);

export const CardTitle: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <h3 className={`text-lg font-bold text-slate-100 tracking-tight font-heading ${className}`}>
    {children}
  </h3>
);

export const CardDescription: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <p className={`text-sm text-slate-400 mt-1 leading-relaxed ${className}`}>
    {children}
  </p>
);

export const CardContent: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>{children}</div>
);

export const CardFooter: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`p-6 border-t border-white/5 flex items-center justify-between ${className}`}>
    {children}
  </div>
);
