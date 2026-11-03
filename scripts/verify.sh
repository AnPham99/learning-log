#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
.venv/bin/python -m pytest --cov --cov-report=term-missing -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
