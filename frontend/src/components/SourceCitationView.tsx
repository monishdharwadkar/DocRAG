import React, { useState } from 'react';
import { FileText, ExternalLink, X } from 'lucide-react';

export interface SourceItem {
  source_path: string;
  heading: string;
  chunk_id: string;
  score?: number;
  text?: string;
}

interface SourceCitationViewProps {
  sources: SourceItem[];
}

export const SourceCitationView: React.FC<SourceCitationViewProps> = ({ sources }) => {
  const [activeChunk, setActiveChunk] = useState<SourceItem | null>(null);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-800/80">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
        <FileText className="w-3.5 h-3.5 text-sky-400" /> Grounded Context Sources
      </div>

      <div className="flex flex-wrap gap-2">
        {sources.map((src, i) => (
          <button
            key={i}
            onClick={() => setActiveChunk(src)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-700/80 hover:border-sky-500 text-slate-300 text-xs font-mono transition-all group"
          >
            <span className="text-sky-400 font-bold">[{i + 1}]</span>
            <span className="truncate max-w-[200px]">{src.source_path.replace('docs_sample/', '')}</span>
            <span className="text-slate-500">#{src.heading}</span>
            <ExternalLink className="w-3 h-3 text-slate-500 group-hover:text-sky-400" />
          </button>
        ))}
      </div>

      {/* Chunk Modal */}
      {activeChunk && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-semibold text-sky-400 font-mono">
                  {activeChunk.source_path}
                </h3>
                <p className="text-xs text-slate-400">Heading: {activeChunk.heading}</p>
              </div>
              <button
                onClick={() => setActiveChunk(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-slate-300 text-xs font-mono leading-relaxed max-h-96 overflow-y-auto whitespace-pre-wrap">
              {activeChunk.text || "No chunk text available."}
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-400">
              <span>Similarity Score: {(activeChunk.score || 0).toFixed(4)}</span>
              <button
                onClick={() => setActiveChunk(null)}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-md font-sans text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
