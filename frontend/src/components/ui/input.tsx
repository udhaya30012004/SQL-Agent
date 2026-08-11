import React from 'react';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, leftIcon, rightIcon, className = '', ...props }, ref) => {
    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider font-heading">
            {label}
          </label>
        )}
        <div className="relative flex items-center group">
          {leftIcon && (
            <div className="absolute left-3.5 text-slate-500 group-focus-within:text-violet-400 transition-colors pointer-events-none">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            className={`w-full bg-space-surface/80 text-slate-100 placeholder:text-slate-600 text-sm rounded-xl border ${
              error
                ? 'border-rose-500/80 focus:ring-rose-500/30 focus:border-rose-400'
                : 'border-white/[0.07] focus:border-violet-500/60 focus:ring-violet-500/20'
            } ${leftIcon ? 'pl-10' : 'pl-3.5'} ${
              rightIcon ? 'pr-10' : 'pr-3.5'
            } py-2.5 outline-none transition-all duration-300 focus:ring-4 focus:shadow-[0_0_15px_rgba(139,92,246,0.15)] ${className}`}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3.5 text-slate-500">
              {rightIcon}
            </div>
          )}
        </div>
        {error && <p className="text-xs text-rose-400 mt-1">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
