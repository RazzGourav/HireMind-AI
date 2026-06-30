import { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { BrainCircuit, ArrowRight, CheckCircle2, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Landing() {
  return (
    <div className="min-h-screen bg-background text-text selection:bg-primary/30 relative overflow-hidden flex flex-col">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 150, repeat: Infinity, ease: "linear" }}
          className="absolute -top-[20%] -left-[10%] w-[60%] h-[60%] rounded-full bg-primary/10 blur-[150px]" 
        />
        <motion.div 
          animate={{ rotate: -360 }}
          transition={{ duration: 120, repeat: Infinity, ease: "linear" }}
          className="absolute top-[40%] -right-[10%] w-[50%] h-[50%] rounded-full bg-accent/10 blur-[150px]" 
        />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiLz48L3N2Zz4=')] [mask-image:linear-gradient(to_bottom,white,transparent,white)]" />
      </div>

      {/* Navbar */}
      <header className="relative z-10 border-b border-white/5 bg-background/50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BrainCircuit className="w-8 h-8 text-primary" />
            <span className="text-xl font-bold tracking-widest text-text">HIREMIND</span>
          </div>
          <div className="flex items-center gap-6 text-sm font-medium">
            <a href="#" className="text-text-muted hover:text-text transition-colors">Architecture</a>
            <Link to="/app" className="btn-primary flex items-center gap-2 px-5 rounded-full">
              Try Live Demo <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 relative z-10 flex flex-col items-center justify-center text-center px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary text-sm font-medium mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            SaaS MVP v1.0 Live
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 max-w-4xl leading-tight">
            The Future of <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-blue-400 to-accent animate-gradient">
              Explainable Hiring Intelligence
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-text-muted max-w-2xl mx-auto mb-10 leading-relaxed">
            Find the right engineer, understand exactly why they match your requirements, 
            and hire with total confidence using our AI-first reasoning engine.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/app" className="btn-primary text-lg px-8 py-4 rounded-full flex items-center gap-2 hover:scale-105 transition-transform">
              Launch Intelligence OS
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </motion.div>

        {/* Benchmarks / Stats */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-24 max-w-5xl mx-auto w-full"
        >
          {[
            { label: "Ranking Accuracy", value: "95%" },
            { label: "Semantic Retrieval", value: "120ms" },
            { label: "Candidate Pool", value: "12,458" },
            { label: "CPU Architecture", value: "<5 Min" },
          ].map((stat, i) => (
            <div key={i} className="glass-panel p-6 text-center border-t-2 border-t-primary/50 relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="text-3xl md:text-4xl font-bold text-text mb-2 relative z-10">{stat.value}</div>
              <div className="text-sm text-text-muted font-medium relative z-10">{stat.label}</div>
            </div>
          ))}
        </motion.div>

        {/* Animated Pipeline Visualization */}
        <motion.div 
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mt-32 w-full max-w-6xl mx-auto"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold">Interactive Reasoning Pipeline</h2>
            <p className="text-text-muted mt-2">How raw data becomes actionable hiring intelligence.</p>
          </div>
          
          <div className="glass-panel p-8 md:p-12 relative overflow-hidden">
            {/* Simple animated flow for MVP */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 relative z-10">
              {['Job Description', 'Vector DB', 'Semantic Search', 'Hybrid Ranker', 'Explainability AI'].map((step, idx, arr) => (
                <Fragment key={step}>
                  <motion.div 
                    initial={{ scale: 0.8, opacity: 0 }}
                    whileInView={{ scale: 1, opacity: 1 }}
                    transition={{ delay: idx * 0.15 }}
                    viewport={{ once: true }}
                    className="flex flex-col items-center gap-3 p-4 bg-surface/80 rounded-2xl border border-white/10 flex-1 min-w-[140px]"
                  >
                    <CheckCircle2 className="w-6 h-6 text-accent" />
                    <span className="text-sm font-semibold text-center">{step}</span>
                  </motion.div>
                  {idx < arr.length - 1 && (
                    <div className="hidden md:block text-primary/50">
                      <ChevronRight className="w-6 h-6" />
                    </div>
                  )}
                  {idx < arr.length - 1 && (
                    <div className="md:hidden text-primary/50 rotate-90 my-2">
                      <ChevronRight className="w-6 h-6" />
                    </div>
                  )}
                </Fragment>
              ))}
            </div>
          </div>
        </motion.div>
      </main>
      
      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 py-8 text-center text-sm text-text-muted mt-24">
        <div className="flex items-center justify-center gap-6 mb-4">
          <a href="http://localhost:8000/docs" className="hover:text-text transition-colors">API Docs (Swagger)</a>
        </div>
        <p>© 2026 Redrob SaaS MVP</p>
      </footer>
    </div>
  );
}
