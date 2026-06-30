import { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { MapPin, Building, Briefcase, Calendar, ExternalLink, Plus, Loader2, GitCommit, ChevronDown, Check, Zap, Globe, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

import SkillGalaxy from '../components/SkillGalaxy';

export default function CandidateProfile() {
  const { id } = useParams();
  const location = useLocation();
  const explanation = location.state?.explanation;
  const [candidate, setCandidate] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [enrichOpen, setEnrichOpen] = useState(false);
  const [enrichText, setEnrichText] = useState('');
  const [enrichLoading, setEnrichLoading] = useState(false);

  const fetchCandidate = async () => {
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/candidate/${id}`);
      setCandidate(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidate();
  }, [id]);

  const handleEnrich = async () => {
    if (!enrichText.trim()) return;
    setEnrichLoading(true);
    try {
      // API call to the new enrichment endpoint
      await axios.post(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/candidate/${id}/enrich`, { text: enrichText });
      setEnrichOpen(false);
      setEnrichText('');
      // Refresh candidate data to see updated scores/skills if applicable
      await fetchCandidate();
    } catch (err) {
      console.error("Failed to enrich", err);
      alert("Enrichment failed. Check backend connection.");
    } finally {
      setEnrichLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!candidate || !candidate.candidate) {
    return <div className="text-center text-text-muted mt-20">Candidate not found.</div>;
  }

  const { profile, skills } = candidate.candidate;
  // Use real score from explanation if available, otherwise mock
  const score = explanation ? Math.round(explanation.final_score) : 94.2; 

  return (
    <div className="animate-in fade-in duration-500 pb-20 max-w-7xl mx-auto">
      <div className="flex flex-col lg:flex-row gap-8">
        
        {/* Left Column: Core Identity (GitHub Profile Style) */}
        <div className="w-full lg:w-1/4 space-y-6 shrink-0">
          <div className="relative group">
            <div className="w-full aspect-square rounded-full bg-gradient-to-tr from-surface-light to-surface border-4 border-surface shadow-2xl flex items-center justify-center text-6xl font-bold text-white overflow-hidden relative">
              <div className="absolute inset-0 bg-primary/20 blur-2xl group-hover:bg-primary/40 transition-colors" />
              <span className="relative z-10">{profile.headline?.charAt(0) || id?.charAt(0)}</span>
            </div>
            
            {/* Animated Score Badge */}
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", bounce: 0.5, delay: 0.2 }}
              className="absolute -bottom-4 -right-4 w-20 h-20 bg-surface rounded-full border-4 border-background flex items-center justify-center flex-col shadow-[0_0_20px_rgba(147,51,234,0.4)] z-20"
            >
              <span className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-success to-accent">{score}</span>
              <span className="text-[9px] font-bold text-text-muted uppercase tracking-wider">Score</span>
            </motion.div>
          </div>

          <div>
            <h1 className="text-3xl font-bold text-text tracking-tight">{profile.headline || id}</h1>
            <p className="text-xl text-text-muted font-light mt-1">{profile.current_title || 'Software Engineer'}</p>
          </div>

          <button 
            onClick={() => setEnrichOpen(true)}
            className="w-full btn-primary bg-surface border border-primary/30 text-primary hover:bg-primary/10 flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" /> Enrich Profile
          </button>

          <div className="space-y-4 text-sm font-medium pt-4 border-t border-white/5">
            <div className="flex items-center gap-3 text-text-muted hover:text-text transition-colors">
              <Building className="w-5 h-5 text-text-muted/70" />
              <span>{profile.current_company || 'Independent'}</span>
            </div>
            <div className="flex items-center gap-3 text-text-muted hover:text-text transition-colors">
              <MapPin className="w-5 h-5 text-text-muted/70" />
              <span>{profile.country || 'Remote'}</span>
            </div>
            <div className="flex items-center gap-3 text-text-muted hover:text-text transition-colors">
              <Briefcase className="w-5 h-5 text-text-muted/70" />
              <span>{Math.floor(profile.experience_months / 12)} Years Exp</span>
            </div>
            <div className="flex items-center gap-3 text-text-muted hover:text-text transition-colors">
              <Calendar className="w-5 h-5 text-text-muted/70" />
              <span className="text-success">Available in 30 Days</span>
            </div>
          </div>

          <div className="flex items-center gap-4 pt-4 border-t border-white/5">
            <a href="#" className="w-10 h-10 rounded-full bg-surface-light flex items-center justify-center text-text-muted hover:text-white hover:bg-[#333] transition-colors"><Globe className="w-5 h-5" /></a>
            <a href="#" className="w-10 h-10 rounded-full bg-surface-light flex items-center justify-center text-text-muted hover:text-white hover:bg-[#0077b5] transition-colors"><Globe className="w-5 h-5" /></a>
            <a href="#" className="w-10 h-10 rounded-full bg-surface-light flex items-center justify-center text-text-muted hover:text-white hover:bg-primary transition-colors"><ExternalLink className="w-5 h-5" /></a>
          </div>
        </div>

        {/* Middle Column: Career & Behavior */}
        <div className="w-full lg:w-2/4 space-y-8">
          
          {/* Behavioral Signals Dashboard */}
          <div className="card">
            <h2 className="text-lg font-bold flex items-center gap-2 mb-6">
              <Zap className="w-5 h-5 text-warning" />
              Behavioral Signals
            </h2>
            <div className="space-y-5">
              {[
                { label: 'Recruiter Response Rate', val: 92, color: 'from-success to-accent' },
                { label: 'Interview Completion', val: 100, color: 'from-primary to-blue-500' },
                { label: 'Profile Completeness', val: 85, color: 'from-warning to-yellow-500' },
                { label: 'GitHub Activity', val: 76, color: 'from-secondary to-gray-400' }
              ].map(sig => (
                <div key={sig.label}>
                  <div className="flex justify-between text-xs font-bold uppercase tracking-wider text-text-muted mb-2">
                    <span>{sig.label}</span>
                    <span>{sig.val}%</span>
                  </div>
                  <div className="h-2 w-full bg-black/40 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${sig.val}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className={`h-full bg-gradient-to-r ${sig.color} rounded-full`}
                    />
                  </div>
                </div>
              ))}
              
              <div className="grid grid-cols-3 gap-4 pt-4 mt-4 border-t border-white/5">
                <div className="bg-surface-light/50 p-3 rounded-xl text-center">
                  <div className="text-[10px] uppercase font-bold text-text-muted">Open to Work</div>
                  <div className="font-bold text-success mt-1">YES</div>
                </div>
                <div className="bg-surface-light/50 p-3 rounded-xl text-center">
                  <div className="text-[10px] uppercase font-bold text-text-muted">Notice</div>
                  <div className="font-bold text-text mt-1">30 Days</div>
                </div>
                <div className="bg-surface-light/50 p-3 rounded-xl text-center">
                  <div className="text-[10px] uppercase font-bold text-text-muted">Last Active</div>
                  <div className="font-bold text-text mt-1">Yesterday</div>
                </div>
              </div>
            </div>
          </div>

          {/* Career Timeline */}
          <div className="card">
            <h2 className="text-lg font-bold mb-6">Career Timeline</h2>
            <div className="relative pl-6 space-y-8 before:absolute before:inset-y-0 before:left-[11px] before:w-[2px] before:bg-white/10">
              {[
                { year: '2026', title: profile.current_title || 'Senior ML Engineer', co: profile.current_company || 'Tech Corp', desc: profile.summary || 'Leading AI initiatives.' },
                { year: '2024', title: 'Machine Learning Engineer', co: 'Startup AI', desc: 'Deployed models to production.' },
                { year: '2022', title: 'Software Engineer', co: 'Enterprise Inc', desc: 'Backend development in Python.' }
              ].map((role, i) => (
                <div key={i} className="relative">
                  <div className="absolute -left-[30px] w-4 h-4 rounded-full bg-surface border-2 border-primary z-10 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                  </div>
                  <div className="bg-surface-light/30 border border-white/5 p-4 rounded-2xl hover:bg-surface-light/50 transition-colors">
                    <div className="flex justify-between items-start mb-1">
                      <h3 className="font-bold text-text">{role.title}</h3>
                      <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-1 rounded-lg">{role.year}</span>
                    </div>
                    <div className="text-sm font-medium text-text-muted mb-2">{role.co}</div>
                    <p className="text-sm text-text-muted/80">{role.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: AI Insights & Explainability */}
        <div className="w-full lg:w-1/4 space-y-6">
          
          <div className="card bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20">
            <h2 className="text-sm font-bold text-primary uppercase tracking-widest mb-3">AI Verdict</h2>
            <div className="text-2xl font-black text-text mb-4">{explanation?.recommendation || 'Excellent Match'}</div>
            <p className="text-sm text-text-muted leading-relaxed">
              {explanation?.recruiter_summary || 'Candidate possesses deep production ML experience and exactly matches all required skills. Behavioral signals indicate high reliability.'}
            </p>
          </div>

          <div className="card p-0 overflow-hidden">
            <SkillGalaxy skills={skills} />
          </div>

          {/* AI Decision Tree / Explainability */}
          <div className="card">
            <h2 className="text-sm font-bold uppercase tracking-widest text-text-muted mb-6">AI Decision Tree</h2>
            <div className="space-y-1 relative">
              <div className="absolute left-4 top-4 bottom-4 w-0.5 bg-white/10 z-0" />
              
              {explanation?.strengths ? explanation.strengths.map((s: any, i: number) => (
                <div key={`s-${i}`} className="flex items-center gap-4 relative z-10 py-2">
                  <div className="w-8 h-8 rounded-full bg-surface border border-white/10 flex items-center justify-center shrink-0">
                    <Check className="w-4 h-4 text-success" />
                  </div>
                  <div className="flex-1 bg-surface-light/40 border border-white/5 rounded-lg px-3 py-2 flex justify-between items-center group relative cursor-help">
                    <span className="text-xs font-medium">{s.label}</span>
                    <span className="text-xs font-bold text-success">+</span>
                    {/* Tooltip */}
                    <div className="absolute hidden group-hover:block bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 bg-background border border-white/10 p-2 rounded text-[10px] text-text-muted shadow-xl z-50">
                      {s.description}
                    </div>
                  </div>
                </div>
              )) : null}

              {explanation?.concerns ? explanation.concerns.map((c: any, i: number) => (
                <div key={`c-${i}`} className="flex items-center gap-4 relative z-10 py-2">
                  <div className="w-8 h-8 rounded-full bg-surface border border-white/10 flex items-center justify-center shrink-0">
                    <AlertTriangle className="w-4 h-4 text-warning" />
                  </div>
                  <div className="flex-1 bg-surface-light/40 border border-white/5 rounded-lg px-3 py-2 flex justify-between items-center group relative cursor-help">
                    <span className="text-xs font-medium">{c.label}</span>
                    <span className={`text-xs font-bold ${c.severity === 'high' ? 'text-danger' : 'text-warning'}`}>-</span>
                    {/* Tooltip */}
                    <div className="absolute hidden group-hover:block bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 bg-background border border-white/10 p-2 rounded text-[10px] text-text-muted shadow-xl z-50">
                      {c.description}
                    </div>
                  </div>
                </div>
              )) : (
                // Fallback Mock
                [
                  { label: 'Semantic Retrieval Match', val: '+12', color: 'text-success' },
                  { label: 'Python & PyTorch', val: '+8', color: 'text-success' },
                  { label: 'Production ML Exp', val: '+15', color: 'text-success' },
                  { label: 'Notice Period (30d)', val: '+5', color: 'text-success' },
                  { label: 'Missing CI/CD', val: '-4', color: 'text-danger' }
                ].map((node, i) => (
                  <div key={i} className="flex items-center gap-4 relative z-10 py-2">
                    <div className="w-8 h-8 rounded-full bg-surface border border-white/10 flex items-center justify-center shrink-0">
                      <GitCommit className="w-4 h-4 text-text-muted" />
                    </div>
                    <div className="flex-1 bg-surface-light/40 border border-white/5 rounded-lg px-3 py-2 flex justify-between items-center">
                      <span className="text-xs font-medium">{node.label}</span>
                      <span className={`text-xs font-bold ${node.color}`}>{node.val}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      </div>

      {/* AI Candidate Enrichment Studio Drawer */}
      <AnimatePresence>
        {enrichOpen && (
          <>
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setEnrichOpen(false)}
              className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50"
            />
            <motion.div 
              initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed top-0 right-0 h-full w-full max-w-md bg-surface border-l border-white/10 shadow-2xl z-50 flex flex-col"
            >
              <div className="p-6 border-b border-white/5 bg-surface/50">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary text-[10px] font-bold tracking-widest mb-4">
                  <SparklesIcon className="w-3 h-3" /> ENRICHMENT STUDIO
                </div>
                <h2 className="text-2xl font-bold">Enrich Profile</h2>
                <p className="text-sm text-text-muted mt-2">
                  Add external data, interview notes, or missing links. Embeddings and scores will recalculate instantly without altering the raw dataset.
                </p>
              </div>
              
              <div className="flex-1 p-6 overflow-y-auto">
                <label className="block text-sm font-bold text-text-muted uppercase tracking-wider mb-3">
                  Additional Information
                </label>
                <textarea 
                  className="w-full h-48 bg-background border border-white/10 rounded-xl p-4 text-text placeholder:text-text-muted/50 focus:outline-none focus:border-primary transition-colors resize-none"
                  placeholder="e.g., 'Strong communicator. Has a GitHub repository with production Vector DB implementations. Cleared internal tech screen with 9/10.'"
                  value={enrichText}
                  onChange={e => setEnrichText(e.target.value)}
                />
                
                <div className="mt-6 space-y-3">
                  <div className="text-xs font-bold uppercase text-text-muted tracking-wider">Suggested Actions</div>
                  <button className="w-full flex items-center justify-between p-3 rounded-xl border border-white/5 hover:bg-white/5 text-sm font-medium transition-colors">
                    Upload Resume DOCX <ChevronDown className="w-4 h-4 text-text-muted" />
                  </button>
                  <button className="w-full flex items-center justify-between p-3 rounded-xl border border-white/5 hover:bg-white/5 text-sm font-medium transition-colors">
                    Add GitHub/LinkedIn URLs <ChevronDown className="w-4 h-4 text-text-muted" />
                  </button>
                  <button className="w-full flex items-center justify-between p-3 rounded-xl border border-white/5 hover:bg-white/5 text-sm font-medium transition-colors">
                    Paste Interview Feedback <ChevronDown className="w-4 h-4 text-text-muted" />
                  </button>
                </div>
              </div>
              
              <div className="p-6 border-t border-white/5 bg-background/50 flex gap-4">
                <button onClick={() => setEnrichOpen(false)} className="flex-1 px-4 py-3 rounded-xl font-bold text-text hover:bg-white/5 transition-colors">
                  Cancel
                </button>
                <button 
                  onClick={handleEnrich} 
                  disabled={enrichLoading || !enrichText.trim()}
                  className="flex-2 px-8 py-3 rounded-xl font-bold bg-primary text-white hover:bg-purple-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {enrichLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><Check className="w-5 h-5" /> Save & Recalculate</>}
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

function SparklesIcon(props: any) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2ZM19 4L19.75 6.25L22 7L19.75 7.75L19 10L18.25 7.75L16 7L18.25 6.25L19 4Z" />
    </svg>
  );
}
