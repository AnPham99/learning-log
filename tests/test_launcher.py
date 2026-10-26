import socket
import sys

import pytest


def test_local_data_initialization_preserves_secret_and_database(tmp_path):
    from scripts.bootstrap import ensure_local_data

    first_key = ensure_local_data(tmp_path)
    database = tmp_path / "var" / "learning_log.sqlite3"
    database.write_bytes(b"existing database")
    second_key = ensure_local_data(tmp_path)
    assert len(first_key) >= 50
    assert first_key == second_key
    assert database.read_bytes() == b"existing database"


def test_runtime_detects_installed_requirements():
    from scripts.bootstrap import runtime_ready

    assert runtime_ready(sys.executable)


def test_port_collision_has_actionable_error():
    from scripts.server import ensure_port_available

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        with pytest.raises(RuntimeError, match="--port"):
            ensure_port_available(port)


def test_custom_launcher_options():
    from run import parse_args

    args = parse_args(["--port", "8001", "--no-browser"])
    assert args.port == 8001
    assert args.no_browser


def test_recently_closed_server_port_can_be_reused():
    from scripts.server import ensure_port_available

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        client = socket.create_connection(("127.0.0.1", port), timeout=2)
        connection, _ = listener.accept()
        connection.close()
        client.close()
    ensure_port_available(port)


@pytest.mark.parametrize("port", ["0", "65536", "invalid"])
def test_invalid_port_is_rejected(port):
    from run import parse_args

    with pytest.raises(SystemExit):
        parse_args(["--port", port])
