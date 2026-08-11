import React from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-semibold transition-all duration-300 ease-out focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:ring-offset-1 focus:ring-offset-space-deep disabled:opacity-50 disabled:cursor-not-allowed select-none rounded-xl font-sans relative overflow-hidden';

    const variants = {
      primary:
        'bg-gradient-to-r from-violet-600 via-violet-500 to-cyan-500 hover:from-violet-500 hover:via-violet-400 hover:to-cyan-400 text-white shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 hover:scale-[1.03] active:scale-[0.97] shimmer-effect btn-glow-pulse',
      secondary:
        'bg-space-elevated hover:bg-space-hover text-slate-100 border border-white/10 hover:border-violet-500/30 shadow-sm hover:shadow-violet-500/10',
      outline:
        'bg-space-surface/60 hover:bg-space-elevated text-slate-200 border border-violet-500/30 hover:border-violet-400/60 shadow-sm hover:shadow-violet-500/15',
      ghost:
        'bg-transparent hover:bg-white/5 text-slate-300 hover:text-white',
      danger:
        'bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 text-white shadow-lg shadow-rose-500/20 hover:shadow-rose-500/35 border border-rose-500/30 hover:scale-[1.03] active:scale-[0.97]',
    };

    const sizes = {
      sm: 'px-3.5 py-1.5 text-xs gap-1.5',
      md: 'px-5 py-2.5 text-sm gap-2',
      lg: 'px-7 py-3.5 text-base gap-2.5',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin text-current shrink-0" />
        ) : (
          leftIcon
        )}
        <span>{children}</span>
        {!isLoading && rightIcon}
      </button>
    );
  }
);

Button.displayName = 'Button';
