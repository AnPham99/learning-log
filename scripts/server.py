"""Start the loopback server, wait for readiness and optionally open the browser."""

import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


def ensure_port_available(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind(("127.0.0.1", port))
        except OSError as error:
            alternative = port + 1 if port < 65535 else 8000
            raise RuntimeError(
                f"Cổng {port} đang được sử dụng. Mở app đang chạy hoặc dùng: "
                f"python3 run.py --port {alternative}"
            ) from error


def open_when_ready(url: str, process: subprocess.Popen) -> None:
    deadline = time.monotonic() + 25
    while process.poll() is None and time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    webbrowser.open(url)
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.2)


def serve(*, project_dir: Path, python: Path, port: int, browser: bool, env: dict) -> int:
    url = f"http://127.0.0.1:{port}/"
    print(f"\nLearning Log → {url}\nNhấn Ctrl+C để dừng. Dữ liệu được giữ lại.\n", flush=True)
    process = subprocess.Popen(
        [
            str(python),
            str(project_dir / "manage.py"),
            "runserver",
            f"127.0.0.1:{port}",
            "--noreload",
            "--insecure",
        ],
        cwd=project_dir,
        env=env,
    )
    if browser:
        threading.Thread(target=open_when_ready, args=(url, process), daemon=True).start()
    try:
        return process.wait()
    except KeyboardInterrupt:
        print("\nĐang dừng Learning Log…", flush=True)
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        return 0
