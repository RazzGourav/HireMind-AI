import os
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_project_environment() -> None:
    project_root = Path(__file__).resolve().parents[1]
    src_path = project_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    if os.getenv("VIRTUAL_ENV") or os.getenv("HIREMIND_BOOTSTRAPPED"):
        return

    venv_python = _venv_python(project_root)
    if venv_python.exists():
        env = os.environ.copy()
        env["HIREMIND_BOOTSTRAPPED"] = "1"
        completed = subprocess.run([str(venv_python), *sys.argv], env=env, check=False)
        raise SystemExit(completed.returncode)

    uv_path = shutil.which("uv")
    if uv_path is None:
        return

    env = os.environ.copy()
    env["HIREMIND_BOOTSTRAPPED"] = "1"
    env.setdefault("UV_CACHE_DIR", str(project_root / ".uv-cache"))
    completed = subprocess.run([uv_path, "run", "python", *sys.argv], env=env, check=False)
    raise SystemExit(completed.returncode)


def _venv_python(project_root: Path) -> Path:
    if os.name == "nt":
        return project_root / ".venv" / "Scripts" / "python.exe"
    return project_root / ".venv" / "bin" / "python"
