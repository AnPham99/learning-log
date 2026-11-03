"""Manage only this project's isolated local PostgreSQL cluster."""

import os
import shutil
import subprocess
from pathlib import Path


def postgres_bin():
    if command := shutil.which("pg_config"):
        return Path(subprocess.check_output([command, "--bindir"], text=True).strip())
    raise RuntimeError(
        "Cần PostgreSQL 15+. macOS: brew install postgresql@15. "
        "Hoặc dùng PostgreSQL ngoài qua PGHOST/PGPASSWORD."
    )


def start_database(data_dir, password):
    import psycopg

    if os.environ.get("PGHOST"):
        return
    binary = postgres_bin()
    cluster = data_dir / "postgres"
    socket_dir = data_dir / "socket"
    socket_dir.mkdir(exist_ok=True, mode=0o700)
    if not (cluster / "PG_VERSION").exists():
        subprocess.run(
            [
                str(binary / "initdb"),
                "-D",
                str(cluster),
                "-U",
                "storedesk",
                "--auth-local=trust",
                "--auth-host=scram-sha-256",
                "--pwfile",
                str(data_dir / ".db-password"),
                "--encoding=UTF8",
                "--locale=C",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    running = (
        subprocess.run(
            [str(binary / "pg_ctl"), "-D", str(cluster), "status"], capture_output=True
        ).returncode
        == 0
    )
    port = os.environ.get("PGPORT", "55432")
    if not running:
        subprocess.run(
            [
                str(binary / "pg_ctl"),
                "-D",
                str(cluster),
                "-l",
                str(data_dir / "postgres.log"),
                "-o",
                f"-h 127.0.0.1 -p {port} -k {socket_dir}",
                "-w",
                "start",
            ],
            check=True,
        )
    with psycopg.connect(
        host="127.0.0.1",
        port=port,
        user="storedesk",
        password=password,
        dbname="postgres",
        autocommit=True,
    ) as conn:
        if not conn.execute("SELECT 1 FROM pg_database WHERE datname = 'storedesk'").fetchone():
            conn.execute("CREATE DATABASE storedesk")


def stop_database(data_dir):
    if os.environ.get("PGHOST"):
        return
    binary = postgres_bin()
    subprocess.run(
        [str(binary / "pg_ctl"), "-D", str(data_dir / "postgres"), "-m", "fast", "-w", "stop"],
        check=True,
    )
