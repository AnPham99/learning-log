"""Local browser application, bound to the loopback interface by the launcher."""

from .base import *  # noqa: F403
from .base import DATA_DIR

DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
if (DATA_DIR / ".secret-key").exists():
    SECRET_KEY = (DATA_DIR / ".secret-key").read_text().strip()
