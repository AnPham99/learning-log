# Decisions

- Approved baseline: one store/warehouse, internal staff sales, VND, manual full
  payment, 10-second dashboard polling. Requirements: docs/SCOPE.md + chat "ok go".
- Separate outputs/storedesk. Learning Log code and repository not changed.
- Use installed PostgreSQL 15.17, own cluster port 55432; application 8010.
  Do not change existing PostgreSQL 5432 or any external database.
- No new framework/frontend runtime: Django 6.1.2 and psycopg 3.3.6, SSR + local JS.
- Moving weighted-average cost; confirmed docs immutable; full return only.
  Reject reversing receipt after later stock movement.
- User correction 03/11: plain operational UI. Removed dark/lime branding,
  decorative icons, eyebrow captions and marketing text; checked desktop/mobile again.
- Launcher initially compared resolved executable paths; venv Python was a symlink
  to host Python, so import failed. Corrected to compare sys.prefix (actual environment).
  Verified subsequent python3 run.py bootstrap succeeds.
- Browser verification exposed missing default for hidden purchase payment_method.
  Set initial cash and added HTTP regression test. No inventory data was affected.
- Final handoff will retain empty personal DB; browser/demo data uses isolated DB.
  No default password, automatic seed, Git commit/push or cloud deployment.

- Teaching re-test: document actual modular-monolith/MVT + service architecture, not
  claim framework-independent Clean Architecture. Catalog/inventory simple reads stay in views.
- Corrected SCOPE wording: sale name/price snapshots already occur at draft save, cost
  at confirmation, as existing README/source state. No pricing behavior changed.
- Added read-only data audit as executable evidence for lecturer; standalone calls use
  REPEATABLE READ. Mutating browser rehearsal uses a cloned database; main seed preserved.

- Direct row deletion uses Django formset DELETE rather than renumbering/removing
  controls. Disabled removed fields cannot trigger native validation; DELETE remains
  enabled. Reuse deleted slots to avoid exhausting max form count during repeated edits.
  Latest undo preserves values and keyboard focus moves to another action/add button.

- User correction: direct removal should be a small ×, not checkbox/text button.
  Render control in HTML and keep DELETE as HiddenInput so asset failures cannot
  expose framework checkbox. Version the changed assets to force refresh.
