import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, AlertTriangle, Loader2 } from 'lucide-react';
import { AgentTraceView, TraceItem } from './AgentTraceView';
import { SourceCitationView, SourceItem } from './SourceCitationView';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceItem[];
  traces?: TraceItem[];
  lowConfidence?: boolean;
}

export const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello! I am **DocRAG**, your self-healing multi-agent assistant for internal engineering documentation. Ask me anything about Kubernetes HPA runbooks, incident postmortems, onboarding, or database migration policies.',
      sources: [],
      traces: []
    }
  ]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsgText = input.trim();
    setInput('');
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMsgText
    };

    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsgText,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      if (data.session_id) setSessionId(data.session_id);

      const botMsg: Message = {
        id: data.message_id || Date.now().toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        traces: data.traces || [],
        lowConfidence: data.low_confidence || false
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: `⚠️ Error connecting to DocRAG backend: ${err.message || 'Unknown error'}. Make sure backend service is running on port 8000.`,
          lowConfidence: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-tr from-sky-600 to-indigo-600 rounded-xl shadow-lg shadow-sky-500/20">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              DocRAG Engineering Chatbot
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                Self-Healing Graph Active
              </span>
            </h2>
            <p className="text-xs text-slate-400">Multi-Agent RAG with Automated Groundedness Validation</p>
          </div>
        </div>
      </div>

      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-center shrink-0 text-sky-400">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div className={`max-w-3xl ${msg.role === 'user' ? 'bg-sky-600 text-white rounded-2xl rounded-tr-none px-5 py-3 shadow-md' : 'bg-slate-900/90 border border-slate-800 rounded-2xl rounded-tl-none p-5 shadow-xl text-slate-200'}`}>
              
              {/* Content */}
              <div className="text-sm leading-relaxed whitespace-pre-wrap">
                {msg.content}
              </div>

              {/* Low confidence escalation banner */}
              {msg.lowConfidence && (
                <div className="mt-3 p-3 bg-amber-950/60 border border-amber-800/60 rounded-xl flex items-center gap-2 text-amber-300 text-xs">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span><strong>Low Confidence Warning:</strong> This answer reached maximum correction retries without 100% groundedness validation. Please review sources carefully.</span>
                </div>
              )}

              {/* Agent Traces view */}
              {msg.traces && msg.traces.length > 0 && (
                <AgentTraceView traces={msg.traces} lowConfidence={msg.lowConfidence} />
              )}

              {/* Grounded Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <SourceCitationView sources={msg.sources} />
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-sky-700 flex items-center justify-center shrink-0 text-white font-bold">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 text-slate-400 text-xs font-mono bg-slate-900/50 p-4 border border-slate-800/60 rounded-xl w-max">
            <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
            <span>Executing Multi-Agent Graph (Retrieve → Generate → Validate)...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="p-4 bg-slate-900/90 border-t border-slate-800 backdrop-blur-md">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
          className="flex items-center gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask DocRAG about K8s HPA runbook, postmortems, API standards..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-3 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-sm rounded-xl transition-all flex items-center gap-2 shadow-lg shadow-sky-500/20"
          >
            <span>Send</span>
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
