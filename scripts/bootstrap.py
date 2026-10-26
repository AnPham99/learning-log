"""Prepare the isolated Python environment and persistent local data."""

import json
import secrets
import subprocess
import sys
import venv
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]


def runtime_ready(python: str | Path) -> bool:
    expected = dict(
        line.split("==", 1)
        for line in (PROJECT_DIR / "requirements.txt").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    )
    probe = (
        "import importlib.metadata as m, json; "
        f"expected=json.loads({json.dumps(json.dumps(expected))}); "
        "assert all(m.version(name)==version for name,version in expected.items())"
    )
    result = subprocess.run([str(python), "-c", probe], capture_output=True, check=False)
    return result.returncode == 0


def ensure_environment(project_dir: Path) -> Path:
    if sys.version_info < (3, 12):  # noqa: UP036 - The standalone launcher checks older interpreters.
        raise RuntimeError("Ứng dụng cần Python 3.12 trở lên. Hãy cài Python mới rồi chạy lại.")
    environment = project_dir / ".venv"
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not python.exists():
        print("Đang tạo môi trường Python riêng…", flush=True)
        venv.create(environment, with_pip=True)
    if not runtime_ready(python):
        print("Đang cài thư viện. Lần cài đầu cần kết nối Internet…", flush=True)
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "-r",
                str(project_dir / "requirements.txt"),
            ],
            check=True,
        )
    return python


def ensure_local_data(project_dir: Path, data_dir: Path | None = None) -> str:
    directory = data_dir or project_dir / "var"
    directory.mkdir(parents=True, exist_ok=True)
    secret_file = directory / ".secret-key"
    if not secret_file.exists():
        try:
            with secret_file.open("x") as file:
                file.write(secrets.token_urlsafe(50))
            secret_file.chmod(0o600)
        except FileExistsError:
            pass  # Another launcher has already created the shared local key.
    return secret_file.read_text().strip()
