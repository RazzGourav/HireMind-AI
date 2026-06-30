from pathlib import Path
from typing import Any, Dict

import yaml


class MetadataGenerator:
    """Generates the metadata.yaml file required for submission."""

    def __init__(self):
        self.metadata: Dict[str, Any] = {
            "team_name": "HireMind AI",
            "repository": "https://github.com/your-username/HireMind-AI",
            "sandbox_url": "https://hiremind-ai-demo.example.com",
            "architecture": "Hybrid FAISS Dense Vector + Skill Ontology Graph Search",
            "model": "LLaMA-3-8B / GPT-4o (Reasoning & Ranking)",
            "embedding_model": "all-MiniLM-L6-v2 (Dense Encoding)",
            "ranking_strategy": "Hybrid Retrieval -> Re-ranking via LLM Reasoner",
            "hardware": "Standard CPU (Intel/AMD) or GPU, 16GB RAM minimum",
            "runtime": "Python 3.13, Node.js 20, Docker Compose",
            "memory_usage": "< 8GB during Hybrid Search (Lazy loaded)",
            "ai_tools_used": [
                "FAISS",
                "SentenceTransformers",
                "Google Gemini/Cursor",
                "Vite React",
            ],
            "license": "MIT",
        }

    def update_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def generate(self, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            yaml.dump(self.metadata, f, default_flow_style=False, sort_keys=False)
        return output_path
