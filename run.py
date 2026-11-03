#!/usr/bin/env python3
"""Start StoreDesk locally; no credentials stored in source."""

import argparse
import os
import socket
import subprocess
import sys
import threading
import urllib.request
import webbrowser
from pathlib import Path

from scripts.environment import prepare

ROOT = Path(__file__).resolve().parent


def open_when_ready(url):
    import time

    for _ in range(60):
        try:
            with urllib.request.urlopen(url, timeout=1):
                webbrowser.open(url)
                return
        except OSError:
            time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description="StoreDesk — kho và bán hàng local")
    parser.add_argument("--port", type=int, default=8010)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--stop-db", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Cổng phải từ 1 đến 65535.")
    if not (args.prepare_only or args.stop_db):
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("127.0.0.1", args.port))
            except OSError as error:
                raise RuntimeError(
                    f"Cổng {args.port} đang được dùng. Chạy với --port khác."
                ) from error
    python, data = prepare(ROOT)
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        os.execv(str(python), [str(python), str(ROOT / "run.py"), *sys.argv[1:]])
    from scripts.database import start_database, stop_database

    if args.stop_db:
        stop_database(data)
        return
    start_database(data, (data / ".db-password").read_text().strip())
    env = {**os.environ, "STOREDESK_DATA_DIR": str(data)}
    for command in ["migrate", "check"]:
        subprocess.run([str(python), str(ROOT / "manage.py"), command], env=env, check=True)
    if args.prepare_only:
        return
    url = f"http://127.0.0.1:{args.port}/"
    print(f"StoreDesk → {url} (Ctrl+C để dừng web; database giữ dữ liệu)", flush=True)
    if not args.no_browser:
        threading.Thread(target=open_when_ready, args=(url,), daemon=True).start()
    server = subprocess.Popen(
        [
            str(python),
            str(ROOT / "manage.py"),
            "runserver",
            f"127.0.0.1:{args.port}",
            "--noreload",
            "--insecure",
        ],
        env=env,
    )
    try:
        server.wait()
    except KeyboardInterrupt:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(f"Không thể chạy StoreDesk: {error}", file=sys.stderr)
        sys.exit(1)
