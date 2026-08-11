import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Bot, Mail, Lock, User, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';

export const SignupPage: React.FC = () => {
  const [username, setUsername] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !email || !password) {
      setError('Please fill in all fields.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      await signup({ username, email, password });
      navigate('/dashboard');
    } catch (err: any) {
      const errMsg =
        err?.response?.data?.detail ||
        err?.message ||
        'Registration failed. Email may already be in use.';
      setError(errMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-space-deep flex flex-col justify-center items-center p-6 relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="bg-orb bg-orb-cyan w-[500px] h-[500px] -top-32 -left-32" />
        <div className="bg-orb bg-orb-violet w-[400px] h-[400px] bottom-0 -right-24" />
        <div className="bg-orb bg-orb-emerald w-[300px] h-[300px] top-1/2 left-1/4" />
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
            Create Platform Account
          </h2>
          <p className="text-xs text-slate-500">
            Register to launch your conversational SQL & Pandas AI analyst
          </p>
        </div>

        {/* Signup Form Card */}
        <div className="p-8 rounded-2xl bg-space-surface/80 border border-violet-500/15 shadow-2xl shadow-violet-500/5 backdrop-blur-xl space-y-5 animate-fade-in-up relative" style={{ animationDelay: '0.1s' }}>
          {/* Gradient top accent line */}
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent rounded-t-2xl" />

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Username"
              type="text"
              placeholder="JohnDoe"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              leftIcon={<User className="w-4 h-4" />}
              required
            />

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
              label="Password (min 6 characters)"
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
              Create Account
            </Button>
          </form>

          <div className="text-center pt-2 border-t border-white/[0.04]">
            <p className="text-xs text-slate-500">
              Already have an account?{' '}
              <Link to="/login" className="text-violet-400 font-semibold hover:text-violet-300 hover:underline transition-colors">
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
