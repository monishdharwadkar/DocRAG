import React from 'react';
import { ChatWindow } from './components/ChatWindow';
import { ShieldCheck, Database, Layers, Terminal } from 'lucide-react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Header Navbar */}
      <header className="h-16 bg-slate-900/80 border-b border-slate-800 px-8 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 font-black font-mono">
            DR
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
              DocRAG <span className="text-xs px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">v1.0-agentic</span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs text-slate-400 font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>vLLM / Mock: Ready</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-sky-400" />
            <span>Qdrant: Connected</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            <span>LangGraph: 4 Nodes</span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 p-6 max-w-7xl w-full mx-auto flex gap-6 overflow-hidden">
        {/* Sidebar Info Panel */}
        <aside className="w-72 hidden lg:flex flex-col gap-4 shrink-0">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3 backdrop-blur-md">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" /> Architecture Highlights
            </h3>
            <ul className="text-xs text-slate-300 space-y-2">
              <li className="flex items-start gap-2">
                <span className="text-sky-400 font-bold">•</span>
                <span><strong>Self-Healing Loop:</strong> Automated validation agent checks answer groundedness.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-400 font-bold">•</span>
                <span><strong>Correction Agent:</strong> Re-generates flagged unsupported claims up to 2 retries.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold">•</span>
                <span><strong>Low Confidence Escalation:</strong> Highlights answers if validation does not hit 80% score threshold.</span>
              </li>
            </ul>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3 backdrop-blur-md">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-sky-400" /> Sample Queries
            </h3>
            <div className="space-y-2 text-xs">
              <div className="p-2 bg-slate-950/60 border border-slate-800/80 rounded-lg text-slate-300">
                "What is the CPU scale down stabilization window for HPA?"
              </div>
              <div className="p-2 bg-slate-950/60 border border-slate-800/80 rounded-lg text-slate-300">
                "What are the SLA response times for SEV-0 and SEV-1 incidents?"
              </div>
              <div className="p-2 bg-slate-950/60 border border-slate-800/80 rounded-lg text-slate-300">
                "What is the zero-downtime database migration policy?"
              </div>
            </div>
          </div>
        </aside>

        {/* Chat Main Area */}
        <section className="flex-1 h-[calc(100vh-7rem)]">
          <ChatWindow />
        </section>
      </main>
    </div>
  );
};
