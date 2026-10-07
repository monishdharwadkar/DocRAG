import React, { useState } from 'react';
import { ChevronDown, ChevronRight, CheckCircle2, XCircle, AlertTriangle, Cpu, Search, Sparkles, RefreshCw } from 'lucide-react';

export interface TraceItem {
  node_name: string;
  input_summary: string;
  output_summary: string;
  metadata?: any;
}

interface AgentTraceViewProps {
  traces: TraceItem[];
  lowConfidence?: boolean;
}

export const AgentTraceView: React.FC<AgentTraceViewProps> = ({ traces, lowConfidence }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!traces || traces.length === 0) return null;

  const getNodeIcon = (nodeName: string) => {
    switch (nodeName) {
      case 'retrieve': return <Search className="w-4 h-4 text-sky-400" />;
      case 'generate': return <Sparkles className="w-4 h-4 text-purple-400" />;
      case 'validate': return <Cpu className="w-4 h-4 text-emerald-400" />;
      case 'correct': return <RefreshCw className="w-4 h-4 text-amber-400" />;
      default: return <Cpu className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="mt-3 border border-slate-800 bg-slate-900/60 rounded-xl overflow-hidden backdrop-blur-md">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-xs font-medium text-slate-300 hover:bg-slate-800/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Agent Trace Workflow</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-950 text-sky-400 border border-sky-800/50">
            {traces.length} steps executed
          </span>
          {lowConfidence && (
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-950 text-amber-400 border border-amber-800/50">
              <AlertTriangle className="w-3 h-3" /> Low Confidence Escalation
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {isOpen ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/40 space-y-3">
          <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
            {traces.map((trace, idx) => {
              const valMeta = trace.node_name === 'validate' ? trace.metadata : null;
              const passed = valMeta?.passed;
              const score = valMeta?.groundedness_score;

              return (
                <div key={idx} className="relative flex items-start gap-3 text-xs">
                  <div className="absolute -left-6 top-0.5 p-1 rounded-full bg-slate-900 border border-slate-700">
                    {getNodeIcon(trace.node_name)}
                  </div>

                  <div className="flex-1 bg-slate-900/80 border border-slate-800 rounded-lg p-3">
                    <div className="flex items-center justify-between font-mono text-[11px] mb-1">
                      <span className="font-semibold uppercase tracking-wider text-slate-200">
                        {trace.node_name}
                      </span>
                      {trace.node_name === 'validate' && score !== undefined && (
                        <span className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                          passed ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60' : 'bg-rose-950 text-rose-400 border border-rose-800/60'
                        }`}>
                          {passed ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                          Groundedness: {(score * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>

                    <p className="text-slate-400 font-sans text-xs">{trace.output_summary}</p>

                    {valMeta?.issues && valMeta.issues.length > 0 && (
                      <div className="mt-2 p-2 bg-rose-950/40 border border-rose-900/40 rounded text-rose-300 text-[11px]">
                        <strong>Flagged Issues:</strong>
                        <ul className="list-disc list-inside mt-1 space-y-0.5">
                          {valMeta.issues.map((issue: string, i: number) => (
                            <li key={i}>{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
