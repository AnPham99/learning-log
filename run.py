#!/usr/bin/env python3
"""One command to prepare and run the entire local application."""

import argparse
import os
import subprocess
from pathlib import Path

from scripts.bootstrap import ensure_environment, ensure_local_data
from scripts.server import ensure_port_available, serve

PROJECT_DIR = Path(__file__).resolve().parent


def valid_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Cổng phải là một số từ 1 đến 65535.") from error
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("Cổng phải nằm trong khoảng 1–65535.")
    return port


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chạy Learning Log trên máy của bạn.")
    parser.add_argument("--port", type=valid_port, default=8000, help="Cổng local, mặc định 8000")
    parser.add_argument("--no-browser", action="store_true", help="Không tự mở trình duyệt")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        ensure_port_available(args.port)
        python = ensure_environment(PROJECT_DIR)
        data_dir = Path(os.environ.get("LEARNING_LOG_DATA_DIR", PROJECT_DIR / "var")).resolve()
        secret_key = ensure_local_data(PROJECT_DIR, data_dir)
        env = os.environ.copy()
        env.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings.local",
                "LEARNING_LOG_SECRET_KEY": secret_key,
                "LEARNING_LOG_DATA_DIR": str(data_dir),
                "PYTHONUNBUFFERED": "1",
            }
        )
        subprocess.run(
            [
                str(python),
                str(PROJECT_DIR / "manage.py"),
                "migrate",
                "--noinput",
            ],
            cwd=PROJECT_DIR,
            env=env,
            check=True,
        )
        subprocess.run(
            [
                str(python),
                str(PROJECT_DIR / "manage.py"),
                "check",
            ],
            cwd=PROJECT_DIR,
            env=env,
            check=True,
        )
        return serve(
            project_dir=PROJECT_DIR,
            python=python,
            port=args.port,
            browser=not args.no_browser,
            env=env,
        )
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(f"\nKhông thể khởi chạy: {error}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
