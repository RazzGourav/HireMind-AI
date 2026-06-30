import React, { useState } from 'react';
import { Send, Bot } from 'lucide-react';
import axios from 'axios';

export default function Copilot() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', content: string}[]>([
    { role: 'assistant', content: 'Hi! I am the HireMind Recruiter Copilot. Ask me questions about the candidate pool, like "Who has production ML experience?" or "Compare the top two candidates."' }
  ]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg = query;
    setQuery('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/copilot/query', {
        query: userMsg
      });
      
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.answer }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error analyzing your request.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Bot className="text-primary w-8 h-8" />
          Recruiter Copilot
        </h1>
        <p className="text-text-muted mt-2">Natural language analytics for your candidate pool.</p>
      </div>

      <div className="flex-1 card mt-6 flex flex-col p-0 overflow-hidden">
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] rounded-2xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-primary text-white rounded-br-none' 
                  : 'bg-surface-light text-text rounded-bl-none border border-surface-light'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-surface-light text-text-muted rounded-2xl p-4 rounded-bl-none animate-pulse">
                Thinking...
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-surface-light bg-surface">
          <form onSubmit={handleSubmit} className="relative">
            <input 
              type="text" 
              placeholder="Ask anything..."
              className="w-full bg-background border border-surface-light rounded-full py-4 pl-6 pr-16 focus:outline-none focus:border-primary text-text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <button 
              type="submit"
              disabled={loading || !query}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-primary hover:bg-blue-700 text-white rounded-full transition-colors disabled:opacity-50"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
