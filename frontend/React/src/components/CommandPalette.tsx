import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Briefcase, X, Home, MessageSquare, Settings } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function CommandPalette({ isOpen, setIsOpen }: { isOpen: boolean, setIsOpen: (o: boolean) => void }) {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setIsOpen]);

  if (!isOpen) return null;

  const actions = [
    { id: 'home', name: 'Dashboard Home', icon: Home, route: '/app' },
    { id: 'search', name: 'Search Candidates', icon: Search, route: '/search' },
    { id: 'copilot', name: 'Ask AI Copilot', icon: MessageSquare, route: '/copilot' },
    { id: 'jobs', name: 'Manage Jobs', icon: Briefcase, route: '/jobs' },
    { id: 'settings', name: 'Settings', icon: Settings, route: '/settings' }
  ];

  const filteredActions = actions.filter(a => a.name.toLowerCase().includes(query.toLowerCase()));

  const handleSelect = (route: string) => {
    navigate(route);
    setIsOpen(false);
    setQuery('');
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-32">
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          exit={{ opacity: 0 }} 
          className="absolute inset-0 bg-background/80 backdrop-blur-sm"
          onClick={() => setIsOpen(false)}
        />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.95, y: -20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -20 }}
          transition={{ duration: 0.2 }}
          className="relative w-full max-w-2xl bg-surface/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
        >
          <div className="flex items-center px-4 py-4 border-b border-white/5">
            <Search className="w-5 h-5 text-text-muted mr-3" />
            <input 
              autoFocus
              type="text" 
              placeholder="Type a command or search..."
              className="flex-1 bg-transparent border-none outline-none text-text text-lg placeholder:text-text-muted"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
            <button onClick={() => setIsOpen(false)} className="p-1 rounded-lg hover:bg-white/5 transition-colors">
              <X className="w-5 h-5 text-text-muted" />
            </button>
          </div>

          <div className="max-h-96 overflow-y-auto p-2">
            {filteredActions.length > 0 ? (
              <div className="space-y-1">
                <div className="px-3 py-2 text-xs font-semibold text-text-muted uppercase tracking-wider">
                  Suggestions
                </div>
                {filteredActions.map((action, idx) => (
                  <button
                    key={action.id}
                    onClick={() => handleSelect(action.route)}
                    className="w-full flex items-center px-3 py-3 rounded-xl hover:bg-primary/20 hover:text-primary transition-colors text-left group"
                  >
                    <action.icon className="w-5 h-5 text-text-muted group-hover:text-primary mr-3 transition-colors" />
                    <span className="flex-1 font-medium">{action.name}</span>
                    {idx === 0 && (
                      <span className="text-xs text-text-muted bg-white/5 px-2 py-1 rounded">Enter ↵</span>
                    )}
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-text-muted">
                No results found for "{query}"
              </div>
            )}
          </div>
          
          <div className="px-4 py-3 bg-surface border-t border-white/5 text-xs text-text-muted flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="bg-white/5 px-2 py-1 rounded">↑</span>
              <span className="bg-white/5 px-2 py-1 rounded">↓</span>
              <span>to navigate</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="bg-white/5 px-2 py-1 rounded">esc</span>
              <span>to close</span>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
