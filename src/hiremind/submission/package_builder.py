import os
import zipfile
from pathlib import Path


class PackageBuilder:
    """Builds the final ZIP package for the hackathon."""

    def __init__(self, output_dir: Path, zip_name: str = "submission.zip"):
        self.output_dir = output_dir
        self.zip_name = zip_name
        self.zip_path = self.output_dir / self.zip_name

        # Files and directories to include based on user's spec
        self.include_paths = [
            "src",
            "frontend",
            "configs",
            "artifacts",
            "outputs",
            "reports",
            "submission",
            "scripts",
            "tests",
            "docs",
            "README.md",
            "Dockerfile.backend",
            "Dockerfile.frontend",
            "docker-compose.yml",
            "LICENSE",
            "Makefile",
        ]

    def build(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(self.zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for item in self.include_paths:
                p = Path(item)
                if p.is_dir():
                    for root, dirs, files in os.walk(p):
                        # skip caches, venvs, and compiled files
                        if any(
                            skip in root
                            for skip in ["__pycache__", ".venv", "node_modules", ".git"]
                        ):
                            continue
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file_path)
                elif p.exists():
                    zipf.write(p, p.name)

        return self.zip_path
