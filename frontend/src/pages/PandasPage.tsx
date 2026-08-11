import React from 'react';
import { CsvUploader } from '../components/pandas/CsvUploader';
import { FileSpreadsheet, Sparkles } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';

export const PandasPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-4xl mx-auto pb-12 animate-fade-in-up">
      <Card glowColor="cyan">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center text-cyan-400">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <CardTitle>Pandas Agent CSV Upload Workspace</CardTitle>
              <CardDescription>
                Upload any messy CSV dataset to run natural language Python analytics
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="p-4 rounded-xl bg-space-surface/80 border border-white/[0.05] space-y-2 text-xs text-slate-400">
            <p className="font-semibold text-slate-200 flex items-center gap-1.5 font-heading">
              <Sparkles className="w-4 h-4 text-cyan-400" /> How the Pandas Agent Works:
            </p>
            <ul className="list-disc list-inside space-y-1 pl-1">
              <li>Upload your raw CSV file to backend storage.</li>
              <li>Agent automatically inspects column data types and handles missing values.</li>
              <li>Generates safe, sandboxed Pandas code to answer your queries and plot charts.</li>
            </ul>
          </div>

          <CsvUploader />
        </CardContent>
      </Card>
    </div>
  );
};
