import { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { BrainCircuit, Search, LayoutDashboard, MessageSquare, Command } from 'lucide-react';
import clsx from 'clsx';
import CommandPalette from '../components/CommandPalette';

export default function Layout() {
  const location = useLocation();
  const [cmdOpen, setCmdOpen] = useState(false);
  
  const navItems = [
    { name: 'Dashboard', path: '/app', icon: LayoutDashboard },
    { name: 'Search', path: '/search', icon: Search },
    { name: 'Copilot', path: '/copilot', icon: MessageSquare },
  ];

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-text selection:bg-primary/30 relative">
      
      {/* Floating Modern Navigation Header */}
      <header className="absolute top-4 left-1/2 -translate-x-1/2 z-40 w-[95%] max-w-5xl">
        <div className="glass-panel px-6 py-3 flex items-center justify-between">
          <Link to="/app" className="flex items-center gap-3 group">
            <div className="relative">
              <BrainCircuit className="text-primary w-7 h-7 relative z-10 transition-transform group-hover:scale-110" />
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
            </div>
            <span className="text-lg font-bold tracking-widest text-text">HIREMIND</span>
          </Link>
          
          <nav className="flex items-center gap-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path || 
                               (item.path !== '/app' && location.pathname.startsWith(item.path));
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={clsx(
                    "flex items-center gap-2 px-4 py-2 rounded-full transition-all text-sm font-medium",
                    isActive 
                      ? "bg-primary/20 text-primary shadow-[0_0_15px_rgba(147,51,234,0.3)]" 
                      : "text-text-muted hover:bg-white/5 hover:text-text"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-4">
            <button 
              onClick={() => setCmdOpen(true)}
              className="flex items-center gap-2 bg-black/40 hover:bg-black/60 border border-white/10 px-3 py-1.5 rounded-lg text-sm text-text-muted transition-colors"
            >
              <Command className="w-4 h-4" />
              <span>Cmd K</span>
            </button>
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-accent p-[1px] cursor-pointer">
              <div className="w-full h-full bg-surface rounded-full flex items-center justify-center text-xs font-bold text-white">
                HR
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto pt-28 pb-12 relative z-10">
        <div className="max-w-7xl mx-auto px-8">
          <Outlet />
        </div>
      </main>

      {/* Global Background Effects */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-accent/10 blur-[120px]" />
      </div>

      {/* Command Palette Modal */}
      <CommandPalette isOpen={cmdOpen} setIsOpen={setCmdOpen} />
    </div>
  );
}
