# Learning Log Implementation Plan

**Goal:** Deliver the complete local Learning Log described in `docs/SPEC.md`.

**Architecture:** Django modular monolith, grouped by feature. Models own persistence
structure; selectors own reads and owner scoping; services own validated writes;
web views adapt HTTP; forms validate user input; templates and static assets own UI.

**Tech Stack:** Python 3.12+, Django 6.1.2, SQLite, HTML/CSS, minimal JavaScript,
pytest-django, coverage and Ruff. Execute in this task, without auto-commits.

## Work and verification

- [ ] Write HTTP acceptance tests in `tests/test_accounts.py` and
  `tests/test_journal_web.py`. Run `.venv/bin/python -m pytest -q` against the
  empty URL configuration: expect failures for missing application routes.
- [ ] Implement account registration and Django authentication in `src/accounts/`;
  implement journal models, selectors, services and HTTP adapters in `src/journal/`.
  Add migrations. Rerun tests: expect account, journal and ownership tests to pass.
- [ ] Add responsive Vietnamese templates and local static assets in `src/templates/`
  and `src/static/`. Verify empty, populated, invalid and unauthorized page states.
- [ ] Write failing launcher and command tests, implement `run.py`, `scripts/` and
  `start.command`. Verify one-command bootstrap and database persistence on restart.
- [ ] Verify with pytest coverage >=80%, Ruff, Django system checks, migration
  consistency and a real browser flow at desktop and mobile sizes.
- [ ] Complete `README.md`, `docs/ARCHITECTURE.md`, and harness evidence; leave
  the verified local app running and provide the start command and project path.

## Risks

The initial installation requires package downloads. The launcher binds only to
127.0.0.1; a conflicting port must produce an actionable error. Database writes
must always enforce topic ownership, including entry creation and editing.
