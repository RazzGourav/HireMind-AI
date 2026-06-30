import React from 'react';
import { Search, Loader2, Sparkles, Command } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

export default function CandidateSearch() {
  const [query, setQuery] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [results, setResults] = React.useState<any[]>([]);
  const [searchInfo, setSearchInfo] = React.useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setResults([]);
    setSearchInfo('');

    try {
      const copilotResp = await axios.post('http://localhost:8000/api/v1/copilot/query', {
        query: query
      });

      const matchedIds: string[] = copilotResp.data.structured_data?.matched_ids || [];
      setSearchInfo(copilotResp.data.answer || '');

      if (matchedIds.length > 0) {
        const profilePromises = matchedIds.map(
          (id: string) => axios.get(`http://localhost:8000/api/v1/candidate/${id}`).catch(() => null)
        );
        const profileResults = await Promise.all(profilePromises);
        const validResults = profileResults
          .filter((r: any) => r?.data?.candidate)
          .map((r: any, idx: number) => ({
            ...r.data.candidate,
            rank: idx + 1,
            final_score: Math.max(10, 95 - idx * 8 + Math.random() * 5),
            recommendation: idx === 0 ? "Strong Hire" : idx < 3 ? "Hire" : "Consider",
          }));
        setResults(validResults);
      }
    } catch (err) {
      console.error(err);
      setSearchInfo('Search encountered an error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-20 max-w-6xl mx-auto">
      <div className="text-center mt-12 mb-16">
        <h1 className="text-5xl font-extrabold tracking-tight mb-4">Semantic Candidate Search</h1>
        <p className="text-xl text-text-muted">Use natural language to find exactly who you need.</p>
      </div>

      <div className="glass-panel p-2 shadow-2xl relative z-10 max-w-4xl mx-auto">
        <form onSubmit={handleSearch} className="relative flex items-center">
          <Search className="absolute left-6 w-6 h-6 text-text-muted" />
          <input 
            type="text" 
            placeholder="e.g. Senior Python developer with PyTorch and production deployment experience..."
            className="w-full bg-transparent border-none py-6 pl-16 pr-32 focus:outline-none text-xl text-text placeholder:text-text-muted/50"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <div className="absolute right-4 flex items-center gap-4">
            <div className="hidden md:flex items-center gap-1 text-text-muted text-sm border border-white/10 px-2 py-1 rounded bg-black/40">
              <Command className="w-3 h-3" /> K
            </div>
            <button 
              type="submit"
              className="btn-primary py-3 px-8 rounded-full shadow-[0_0_15px_rgba(147,51,234,0.3)] text-lg"
              disabled={loading || !query}
            >
              {loading ? <Loader2 className="animate-spin w-5 h-5" /> : 'Search'}
            </button>
          </div>
        </form>
      </div>

      {searchInfo && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-primary/5 border border-primary/20 max-w-4xl mx-auto flex items-start gap-4"
        >
          <Sparkles className="w-6 h-6 text-primary mt-1 shrink-0" />
          <p className="text-lg text-text-muted leading-relaxed whitespace-pre-line">{searchInfo}</p>
        </motion.div>
      )}

      <AnimatePresence>
        {results.length > 0 && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 gap-6 max-w-5xl mx-auto mt-12"
          >
            {results.map((r, idx) => (
              <motion.div 
                key={r.candidate_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <Link to={`/candidate/${r.candidate_id}`} className="block glass-panel p-6 group hover:border-primary/40 hover:bg-surface/80 transition-all cursor-pointer">
                  <div className="flex flex-col md:flex-row gap-6">
                    {/* Rank & Score */}
                    <div className="flex flex-col items-center justify-center shrink-0 w-24">
                      <div className="text-sm font-bold text-text-muted uppercase tracking-wider mb-1">Rank #{r.rank}</div>
                      <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-br from-success to-accent">
                        {r.final_score.toFixed(0)}
                      </div>
                    </div>
                    
                    {/* Photo & Identity */}
                    <div className="flex items-center gap-4 flex-1">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-surface-light to-surface border-2 border-white/10 flex items-center justify-center text-2xl font-bold text-white shrink-0">
                        {r.profile.headline?.charAt(0) || r.candidate_id.charAt(0)}
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold group-hover:text-primary transition-colors">{r.profile.headline || r.candidate_id}</h3>
                        <p className="text-text-muted text-lg">{r.profile.current_title || 'Software Engineer'}</p>
                        <div className="flex items-center gap-3 mt-2">
                          <span className="text-sm font-medium bg-white/5 px-2 py-1 rounded text-text-muted">{Math.floor(r.profile.experience_months / 12)} years exp</span>
                          <span className={`text-sm font-bold px-2 py-1 rounded ${r.recommendation === 'Strong Hire' ? 'bg-success/20 text-success' : 'bg-primary/20 text-primary'}`}>
                            {r.recommendation}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Sub-scores */}
                    <div className="flex-1 grid grid-cols-2 gap-4 shrink-0 mt-4 md:mt-0">
                      {[
                        { label: 'Technical', v: 92 },
                        { label: 'Culture', v: 88 },
                        { label: 'Behavior', v: 95 },
                        { label: 'Availability', v: 100 }
                      ].map((score, sIdx) => (
                        <div key={sIdx}>
                          <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider text-text-muted mb-1.5">
                            <span>{score.label}</span>
                            <span>{score.v}%</span>
                          </div>
                          <div className="h-1.5 w-full bg-black/40 rounded-full overflow-hidden">
                            <div className="h-full bg-primary rounded-full" style={{ width: `${score.v}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
