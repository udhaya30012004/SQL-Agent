import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bot,
  Database,
  FileSpreadsheet,
  BarChart3,
  ShieldCheck,
  Zap,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { Button } from '../components/ui/button';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-space-deep text-slate-100 flex flex-col selection:bg-violet-500/20 selection:text-violet-300 dot-grid-bg relative overflow-hidden">
      {/* Floating background orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="bg-orb bg-orb-violet w-[600px] h-[600px] -top-40 -left-40" />
        <div className="bg-orb bg-orb-cyan w-[500px] h-[500px] top-1/3 -right-32" />
        <div className="bg-orb bg-orb-emerald w-[400px] h-[400px] bottom-0 left-1/4" />
      </div>

      {/* Top Navbar */}
      <nav className="relative h-20 px-8 border-b border-white/[0.06] flex items-center justify-between backdrop-blur-2xl bg-space-deep/60 sticky top-0 z-50">
        {/* Bottom gradient glow line */}
        <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-violet-500/40 to-transparent" />

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-cyan-400 p-0.5 shadow-lg shadow-violet-500/25">
            <div className="w-full h-full bg-space-deep rounded-[10px] flex items-center justify-center">
              <Bot className="w-5 h-5 text-violet-400" />
            </div>
          </div>
          <span className="text-base font-bold text-white tracking-tight font-heading">
            Agentic Data Analyst
          </span>
        </div>

        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/login')}>
            Sign In
          </Button>
          <Button onClick={() => navigate('/signup')}>
            Get Started Free
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-6 py-24 md:py-32 text-center max-w-5xl mx-auto flex flex-col items-center z-10 glitter-container">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/25 text-violet-300 text-xs font-semibold mb-8 shadow-inner animate-fade-in-up animate-breathe">
          <Sparkles className="w-4 h-4 text-violet-400" />
          <span>Next-Generation AI Agentic Data Science</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight leading-tight max-w-4xl mb-6 font-heading animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          Conversational Intelligence for Your <br />
          <span className="text-gradient-violet-cyan">
            PostgreSQL & CSV Data
          </span>
        </h1>

        <p className="text-base md:text-lg text-slate-400 max-w-2xl mb-10 leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          Ask natural-language questions, automatically generate & validate PostgreSQL queries, execute analytics in safe sandboxes, and view interactive Plotly charts in seconds.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4 w-full justify-center animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          <Button
            size="lg"
            onClick={() => navigate('/signup')}
            rightIcon={<ArrowRight className="w-5 h-5" />}
          >
            Launch Analyst Platform
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate('/login')}
          >
            Sign In to Existing Account
          </Button>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="relative px-6 py-16 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 z-10 stagger-children">
        <div className="p-8 rounded-2xl bg-space-surface/60 border border-white/[0.06] space-y-4 hover:border-violet-500/35 transition-all duration-300 backdrop-blur-lg hover-lift animate-fade-in-up">
          <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/25 flex items-center justify-center text-violet-400">
            <Database className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100 font-heading">PostgreSQL SQL RAG</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Hybrid keyword + Pinecone semantic schema retriever automatically selects relevant tables and builds safe read-only SQL queries.
          </p>
        </div>

        <div className="p-8 rounded-2xl bg-space-surface/60 border border-white/[0.06] space-y-4 hover:border-cyan-500/35 transition-all duration-300 backdrop-blur-lg hover-lift animate-fade-in-up">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center text-cyan-400">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100 font-heading">Pandas CSV Workspace</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Drag & drop raw CSV datasets to query messy spreadsheets and generate business intelligence insights instantly.
          </p>
        </div>

        <div className="p-8 rounded-2xl bg-space-surface/60 border border-white/[0.06] space-y-4 hover:border-emerald-500/35 transition-all duration-300 backdrop-blur-lg hover-lift animate-fade-in-up">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400">
            <BarChart3 className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100 font-heading">Plotly Interactive Charts</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            LLM auto-detects optimal chart specifications and renders interactive HTML bar, line, pie, and scatter charts.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative mt-auto py-8 border-t border-white/[0.06] text-center text-xs text-slate-600 z-10">
        <p>© 2026 Agentic Data Analyst Platform. Production AI Architecture.</p>
      </footer>
    </div>
  );
};
