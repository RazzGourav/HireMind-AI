import { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, Trophy, TrendingUp, AlertTriangle, Star, DollarSign, Brain, Download } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import clsx from 'clsx';
import { motion } from 'framer-motion';

export default function DashboardHome() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [topCandidates, setTopCandidates] = useState<any[]>([]);
  const [rankingLoading, setRankingLoading] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setTopCandidates([]);
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const response = await axios.post('http://localhost:8000/api/v1/job/parse', formData);
      setResult(response.data);
      await fetchTopCandidates(response.data);
    } catch (err) {
      console.error(err);
      alert("Failed to parse JD. Supported formats: .docx, .md, .txt");
    } finally {
      setLoading(false);
    }
  };

  const fetchTopCandidates = async (parsedResult: any) => {
    setRankingLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/ranking/run', {
        jd_reqs: parsedResult,
        params: {
          top_k: 20,
          max_notice_days: 90,
          include_explanations: true
        }
      });
      
      if (response.data?.results) {
        // Map RankingResponse schema to the format Dashboard expects
        const rankedCandidates = response.data.results.map((c: any) => ({
          candidate_id: c.candidate_id,
          rank: c.rank,
          profile: c.profile_summary || { headline: 'Unknown', current_title: 'Unknown', experience_months: 0 },
          score: Math.round(c.final_score),
          explanation: c.explanation,
          subscores: {
             technical: Math.round(c.technical_score),
             career: Math.round(c.career_score),
             behavior: Math.round(c.behavior_score),
             knowledge: Math.round(c.knowledge_score)
          }
        }));
        setTopCandidates(rankedCandidates);
      }
    } catch (err) {
      console.error('Failed to fetch top candidates:', err);
    } finally {
      setRankingLoading(false);
    }
  };

  const downloadCSV = () => {
    if (topCandidates.length === 0) return;
    
    // CSV Header matching submission format exactly
    let csvContent = "data:text/csv;charset=utf-8,candidate_id,rank,score,reasoning\n";
    
    // Append rows
    topCandidates.forEach(c => {
      const scoreFormat = (c.score || 0).toFixed(4); // e.g. 100.0000 format
      const rawReasoning = c.explanation?.recruiter_summary || "No reasoning generated.";
      // Proper CSV escaping for reasoning string
      const escapedReasoning = `"${rawReasoning.replace(/"/g, '""')}"`;
      
      csvContent += `${c.candidate_id},${c.rank},${scoreFormat},${escapedReasoning}\n`;
    });
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "submission.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-20">
      {/* Header Greeting */}
      <div>
        <motion.h1 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-4xl font-extrabold tracking-tight"
        >
          Hello, <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">Recruiter</span>
        </motion.h1>
        <div className="flex items-center gap-6 text-sm text-text-muted mt-3 font-medium">
          <span className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-success animate-pulse" /> AI Ready</span>
          <span>12,458 Candidates</span>
          <span>12 Active Jobs</span>
        </div>
      </div>

      {/* AI Insights Section */}
      <div>
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary" />
          AI Insights
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { icon: TrendingUp, color: 'text-success', bg: 'bg-success/10', text: 'Candidate quality increased 12%' },
            { icon: AlertTriangle, color: 'text-warning', bg: 'bg-warning/10', text: '6 candidates inactive >90 days' },
            { icon: Star, color: 'text-yellow-400', bg: 'bg-yellow-400/10', text: 'Found 3 hidden gems matching JD' },
            { icon: DollarSign, color: 'text-accent', bg: 'bg-accent/10', text: 'Average requested salary 22 LPA' },
          ].map((insight, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="glass-panel p-4 flex items-start gap-4 group hover:bg-white/5 transition-colors cursor-default"
            >
              <div className={`p-2 rounded-lg ${insight.bg}`}>
                <insight.icon className={`w-5 h-5 ${insight.color}`} />
              </div>
              <p className="text-sm font-medium text-text-muted group-hover:text-text transition-colors leading-snug">
                {insight.text}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Main Grid: Upload JD & Top Matches */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Upload */}
        <div className="lg:col-span-1 space-y-6">
          <div className="card h-full flex flex-col">
            <h2 className="text-lg font-bold mb-6">New Job Requirement</h2>
            
            <div 
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className={clsx(
                "flex-1 border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all",
                file ? "border-primary bg-primary/5" : "border-white/10 hover:border-white/20 hover:bg-white/5"
              )}
            >
              {file ? (
                <>
                  <FileText className="w-12 h-12 text-primary mb-4" />
                  <p className="font-medium text-lg text-text truncate max-w-full px-4">{file.name}</p>
                  <button 
                    onClick={handleUpload}
                    disabled={loading}
                    className="btn-primary mt-8 w-full"
                  >
                    {loading ? 'Analyzing Neural Embeddings...' : 'Parse & Retrieve'}
                  </button>
                </>
              ) : (
                <>
                  <div className="p-4 rounded-full bg-white/5 mb-4">
                    <UploadCloud className="w-8 h-8 text-text-muted" />
                  </div>
                  <p className="font-medium text-text mb-2">Drag and drop Job Description</p>
                  <p className="text-xs text-text-muted mb-8">Supports DOCX, TXT, or MD</p>
                  <label className="btn-primary cursor-pointer w-full text-center">
                    Browse Files
                    <input type="file" accept=".docx,.md,.txt" className="hidden" onChange={(e) => e.target.files && setFile(e.target.files[0])} />
                  </label>
                </>
              )}
            </div>

            {/* Parsed Result Preview */}
            {result && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-6 p-4 bg-success/10 rounded-xl border border-success/20"
              >
                <h3 className="flex items-center gap-2 text-sm font-bold text-success mb-3">
                  <CheckCircle2 className="w-4 h-4" /> Parsed Requirements
                </h3>
                <div className="flex flex-wrap gap-1.5">
                  {result.required_skills.slice(0, 8).map((s: string) => (
                    <span key={s} className="text-[10px] uppercase tracking-wider font-bold bg-black/40 text-success px-2 py-1 rounded">
                      {s}
                    </span>
                  ))}
                  {result.required_skills.length > 8 && (
                    <span className="text-[10px] uppercase tracking-wider font-bold bg-black/40 text-text-muted px-2 py-1 rounded">
                      +{result.required_skills.length - 8} more
                    </span>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Right Column: AI Recommendations */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-400" />
              AI Recommendations
            </h2>
            <div className="flex items-center gap-4">
              {topCandidates.length > 0 && (
                <button 
                  onClick={downloadCSV}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold bg-white/10 hover:bg-white/20 text-white transition-colors border border-white/5 shadow-lg"
                >
                  <Download className="w-4 h-4" /> Export CSV
                </button>
              )}
              {topCandidates.length > 0 && (
                <span className="text-sm font-medium text-text-muted hidden sm:inline">
                  Confidence Threshold: <span className="text-success">High (&gt;85%)</span>
                </span>
              )}
            </div>
          </div>

          {!result && !rankingLoading && topCandidates.length === 0 && (
            <div className="glass-panel h-64 flex flex-col items-center justify-center text-text-muted border-dashed">
              <Brain className="w-12 h-12 mb-4 opacity-20" />
              <p>Upload a JD to generate AI recommendations.</p>
            </div>
          )}

          {rankingLoading && (
            <div className="glass-panel p-8 space-y-6">
              {[1, 2, 3].map(i => (
                <div key={i} className="flex gap-4 animate-pulse">
                  <div className="w-16 h-16 rounded-xl bg-white/5" />
                  <div className="flex-1 space-y-3 py-1">
                    <div className="h-4 bg-white/5 rounded w-1/3" />
                    <div className="h-3 bg-white/5 rounded w-1/4" />
                    <div className="h-2 bg-white/5 rounded w-full" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {topCandidates.length > 0 && (
            <div className="space-y-4">
              {topCandidates.map((c, idx) => (
                <motion.div
                  key={c.candidate_id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <Link
                    to={`/candidate/${c.candidate_id}`}
                    state={{ explanation: c.explanation }}
                    className="block glass-panel p-5 group hover:border-primary/50 hover:shadow-[0_0_30px_rgba(147,51,234,0.15)] transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-5">
                        <div className="relative">
                          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-xl font-bold text-white shadow-lg">
                            #{c.rank}
                          </div>
                          {idx === 0 && (
                            <div className="absolute -top-2 -right-2 bg-yellow-400 text-black text-[10px] font-bold px-2 py-0.5 rounded-full shadow">
                              BEST
                            </div>
                          )}
                        </div>
                        <div>
                          <h3 className="text-lg font-bold group-hover:text-primary transition-colors">
                            {c.profile.headline || c.candidate_id}
                          </h3>
                          <p className="text-sm text-text-muted mt-1">
                            {c.profile.current_title || 'Software Engineer'} • {Math.floor(c.profile.experience_months / 12)} years exp
                          </p>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <div className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-success to-accent">
                          {c.score}%
                        </div>
                        <div className="text-xs font-semibold text-text-muted uppercase tracking-widest mt-1">
                          Match Score
                        </div>
                      </div>
                    </div>

                    <div className="mt-5 pt-5 border-t border-white/5 grid grid-cols-4 gap-4">
                      {/* AI Sub-scores */}
                      {[
                        { label: 'Technical', val: c.subscores.technical },
                        { label: 'Knowledge', val: c.subscores.knowledge },
                        { label: 'Behavior', val: c.subscores.behavior },
                        { label: 'Career', val: c.subscores.career }
                      ].map((score, sIdx) => (
                        <div key={sIdx}>
                          <div className="flex justify-between text-xs mb-1.5 font-medium">
                            <span className="text-text-muted">{score.label}</span>
                            <span className="text-text">{score.val}%</span>
                          </div>
                          <div className="h-1.5 w-full bg-black/40 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-primary to-accent rounded-full"
                              style={{ width: `${score.val}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    {c.explanation?.recruiter_summary && (
                      <div className="mt-4 p-3 bg-surface rounded-xl border border-white/5 text-sm text-text-muted leading-relaxed flex items-start gap-3">
                        <Brain className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                        <span className="italic">{c.explanation.recruiter_summary}</span>
                      </div>
                    )}
                  </Link>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
