import React, { useState } from 'react';
import { Settings, Sliders, Moon, Key, Check } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';

export const SettingsPage: React.FC = () => {
  const [defaultConn, setDefaultConn] = useState<string>(
    localStorage.getItem('connection_string') ||
      'postgresql+psycopg2://postgres:1234@localhost:5432/pagila'
  );
  const [saved, setSaved] = useState<boolean>(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('connection_string', defaultConn);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-12 animate-fade-in-up">
      <Card glowColor="violet">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/25 flex items-center justify-center text-violet-400">
              <Settings className="w-5 h-5" />
            </div>
            <div>
              <CardTitle>Platform Configuration Settings</CardTitle>
              <CardDescription>
                Manage default database strings, API preferences, and UI themes
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <form onSubmit={handleSave} className="space-y-4">
            <Input
              label="Default PostgreSQL Connection String"
              value={defaultConn}
              onChange={(e) => setDefaultConn(e.target.value)}
              placeholder="postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
            />

            <div className="flex items-center justify-between pt-2">
              {saved ? (
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1 font-heading">
                  <Check className="w-4 h-4" /> Preferences saved!
                </span>
              ) : (
                <span className="text-xs text-slate-500">
                  Stored securely in client localStorage
                </span>
              )}

              <Button type="submit" size="sm">
                Save Settings
              </Button>
            </div>
          </form>

          <div className="pt-6 border-t border-white/[0.05] space-y-3">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2 font-heading">
              <Moon className="w-4 h-4 text-violet-400" /> UI Aesthetic Theme
            </h4>
            <div className="p-4 rounded-xl bg-space-surface/80 border border-violet-500/20 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-100 font-heading">Electric Space Deep Violet</p>
                <p className="text-[11px] text-slate-500">Deep cosmic background with neon violet & cyan accents</p>
              </div>
              <span className="text-xs font-bold text-violet-300 bg-violet-500/15 px-2.5 py-1 rounded-full border border-violet-500/30 animate-glow-pulse font-mono">
                ACTIVE
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
