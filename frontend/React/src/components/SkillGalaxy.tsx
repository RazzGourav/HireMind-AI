import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

export default function SkillGalaxy({ skills }: { skills: any[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dim, setDim] = useState({ w: 400, h: 300 });

  useEffect(() => {
    if (containerRef.current) {
      setDim({
        w: containerRef.current.clientWidth,
        h: containerRef.current.clientHeight
      });
    }
  }, []);

  // Construct Neo4j style graph data
  const graphData = {
    nodes: [{ id: 'Candidate', name: 'Candidate', val: 10, color: '#9333ea' }],
    links: [] as any[]
  };

  skills.slice(0, 15).forEach((s, idx) => {
    const isDomain = idx % 3 === 0;
    const color = isDomain ? '#06b6d4' : '#3b82f6';
    graphData.nodes.push({ id: s.name, name: s.name, val: 5, color });
    graphData.links.push({ source: 'Candidate', target: s.name });
  });

  return (
    <div ref={containerRef} className="w-full h-64 bg-background/50 rounded-xl overflow-hidden border border-white/5 relative">
      <div className="absolute top-2 left-2 text-xs font-bold text-text-muted uppercase tracking-widest z-10">Skill Galaxy</div>
      <ForceGraph2D
        width={dim.w}
        height={dim.h}
        graphData={graphData}
        nodeLabel="name"
        nodeColor={(n: any) => n.color}
        linkColor={() => 'rgba(255,255,255,0.1)'}
        nodeRelSize={4}
        linkWidth={1}
      />
    </div>
  );
}
