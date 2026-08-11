import React, { useState } from 'react';
import { BarChart3, Maximize2, ExternalLink, Loader2 } from 'lucide-react';
import { Dialog } from '../ui/dialog';
import { buildBackendUrl } from '../../api/config';

interface ChartViewerProps {
  chartPath: string;
  chartSpec?: Record<string, any> | null;
}

export const ChartViewer: React.FC<ChartViewerProps> = ({
  chartPath,
  chartSpec,
}) => {
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Normalize backslashes (Windows) and forward slashes to reliably extract filename
  // e.g. "F:\DA_Project\SQL_Agent\artifacts\charts\bar_graph_11.html" -> "bar_graph_11.html"
  const normalizedPath = chartPath.replace(/\\/g, '/');
  const filename = normalizedPath.split('/').pop() || '';
  const chartUrl = buildBackendUrl(`/charts/${filename}`);

  return (
    <>
      <div className="rounded-2xl bg-space-deep border border-violet-500/25 overflow-hidden shadow-2xl my-4 glow-violet">
        <div className="flex items-center justify-between px-4 py-2.5 bg-space-surface/90 border-b border-white/[0.05]">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-violet-400" />
            <span className="text-xs font-semibold text-slate-200 font-heading">
              {chartSpec?.title || 'Interactive Plotly Analytics Visualization'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={chartUrl}
              target="_blank"
              rel="noreferrer"
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
              title="Open in new tab"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
            <button
              onClick={() => setIsFullscreen(true)}
              className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-violet-300 bg-violet-500/15 hover:bg-violet-500/25 rounded-lg border border-violet-500/30 transition-colors"
            >
              <Maximize2 className="w-3 h-3" />
              <span>Fullscreen</span>
            </button>
          </div>
        </div>

        <div className="relative w-full h-[400px] bg-space-deep">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-space-deep z-10">
              <div className="flex flex-col items-center gap-2">
                <Loader2 className="w-6 h-6 text-violet-400 animate-spin" />
                <span className="text-xs text-slate-400 font-heading">Rendering Plotly Chart...</span>
              </div>
            </div>
          )}
          <iframe
            src={chartUrl}
            title="Plotly Interactive Visualization"
            onLoad={() => setIsLoading(false)}
            className="w-full h-full border-0"
          />
        </div>
      </div>

      {/* Fullscreen Dialog Modal */}
      <Dialog
        isOpen={isFullscreen}
        onClose={() => setIsFullscreen(false)}
        title={chartSpec?.title || 'Plotly Chart View'}
        maxWidth="2xl"
      >
        <div className="w-full h-[70vh]">
          <iframe
            src={chartUrl}
            title="Plotly Fullscreen Visualization"
            className="w-full h-full border-0 rounded-xl bg-space-deep"
          />
        </div>
      </Dialog>
    </>
  );
};
