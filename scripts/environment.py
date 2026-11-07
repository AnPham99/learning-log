import os
import secrets
import subprocess
import sys
from pathlib import Path


def prepare(root):
    data = Path(os.environ.get("STOREDESK_DATA_DIR", root / "var")).resolve()
    data.mkdir(parents=True, exist_ok=True, mode=0o700)
    for name in [".secret-key", ".db-password"]:
        path = data / name
        if not path.exists():
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w") as output:
                output.write(secrets.token_urlsafe(48))
    candidates = [
        root / ".venv" / "Scripts" / "python.exe",
        root / ".venv" / "bin" / "python.exe",
        root / ".venv" / "bin" / "python",
    ]
    python = next((path for path in candidates if path.exists()), candidates[0])
    if not python.exists():
        subprocess.run([sys.executable, "-m", "venv", str(root / ".venv")], check=True)
        python = next((path for path in candidates if path.exists()), candidates[0])
    if not python.exists():
        raise RuntimeError("Không tìm thấy Python trong môi trường .venv.")
    probe = subprocess.run([str(python), "-c", "import django, psycopg"], capture_output=True)
    if probe.returncode:
        subprocess.run(
            [str(python), "-m", "pip", "install", "-r", str(root / "requirements.txt")], check=True
        )
    return python, data
