import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Bot, Mail, Lock, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all required fields.');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      navigate('/dashboard');
    } catch (err: any) {
      const errMsg =
        err?.response?.data?.detail ||
        err?.message ||
        'Authentication failed. Please check your credentials.';
      setError(errMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-space-deep flex flex-col justify-center items-center p-6 relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="bg-orb bg-orb-violet w-[500px] h-[500px] -top-32 -right-32" />
        <div className="bg-orb bg-orb-cyan w-[400px] h-[400px] bottom-0 -left-24" />
      </div>

      {/* Glitter container */}
      <div className="w-full max-w-md space-y-6 relative z-10 glitter-container">
        {/* Header Logo */}
        <div className="text-center space-y-2 animate-fade-in-up">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-violet-600 to-cyan-400 p-0.5 shadow-xl shadow-violet-500/25 mb-2 animate-breathe">
            <div className="w-full h-full bg-space-deep rounded-xl flex items-center justify-center">
              <Bot className="w-7 h-7 text-violet-400" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight font-heading">
            Sign in to Agentic DA
          </h2>
          <p className="text-xs text-slate-500">
            Enter your email & password to access your AI Data Analyst account
          </p>
        </div>

        {/* Login Form Card */}
        <div className="p-8 rounded-2xl bg-space-surface/80 border border-violet-500/15 shadow-2xl shadow-violet-500/5 backdrop-blur-xl space-y-5 animate-fade-in-up relative" style={{ animationDelay: '0.1s' }}>
          {/* Gradient top accent line */}
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-violet-500/50 to-transparent rounded-t-2xl" />

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              placeholder="user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-4 h-4" />}
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              leftIcon={<Lock className="w-4 h-4" />}
              required
            />

            <Button
              type="submit"
              className="w-full mt-2"
              isLoading={isLoading}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Sign In
            </Button>
          </form>

          <div className="text-center pt-2 border-t border-white/[0.04]">
            <p className="text-xs text-slate-500">
              Don't have an account?{' '}
              <Link to="/signup" className="text-violet-400 font-semibold hover:text-violet-300 hover:underline transition-colors">
                Sign Up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
