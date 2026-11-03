# Progress — StoreDesk

Approved scope: docs/SCOPE.md, user "ok go", UI giản dị theo yêu cầu tiếp theo.

## Completed

1. Bootstrap Python và PostgreSQL riêng 55432; local website 8010.
2. Models, role/service boundaries, receipt/sale drafts, confirm/cancel/full reversal,
   weighted cost, stock adjustment and movement ledger.
3. Search/pagination, products/contacts/staff forms, SSR UI and dashboard 10s polling.
4. User-directed UI simplification: light sidebar, plain forms/tables, restrained colors,
   no decorative icons or promotional captions; desktop/mobile visually reviewed.
5. 58 PostgreSQL tests pass, including concurrent sales, duplicate confirm/draft;
   application coverage 90.77%, Ruff/format/system check/migrations all pass.
6. 21 browser check groups, no JS runtime errors, mobile no horizontal page overflow.
7. Reconciled stock/ledger: zero mismatches. Verified pg_dump/restore and restart.
8. README, scope, architecture, browser evidence, test log and screenshots complete.

## Handoff

Project: outputs/storedesk. Run python3 run.py; open http://127.0.0.1:8010/.
Demo accounts/data were subsequently requested and provisioned on 03/11/2026.
Current local database has 3 demo users, 8 products and 32 documents; see update below.

Acceptance/restore test databases removed, acceptance web stopped; personal web
and dedicated PostgreSQL left running. Runtime secrets/DB ignored by .gitignore.
No new Git repository, commit, push or deployment performed for this project.

## Remaining / limits

No required work remains within approved local scope. Machine-specific acceptance
on recipient hardware remains to be performed; untested OS/browsers and no large-load
benchmark. Beyond scope items are listed in docs/SCOPE.md and README.

## Next session

Read this file, scope and current sources. Verify runtime rather than assuming it is
still listening. For any new feature, agree behavior before editing. Workflow lessons
(venv detection, hidden purchase default, simplified UI) recorded in DECISIONS.md.

## Requested demo provisioning — 03/11/2026

- User explicitly requested a few accounts and seed data. Verified DB was empty first.
- Created quanly (manager), nhanvien_kho (warehouse), nhanvien_banhang (sales) through
  existing account services; separate random passwords, validated by Django.
- Passwords saved only in ignored var/demo-accounts.txt (mode 0600); not in source/logs.
- Used existing seed_demo management command: 8 products, 1 supplier, 3 customers,
  1 confirmed receipt and 28 sales over the latest 14 days, plus demo stock adjustments.
- Added purchase draft and sale draft; added cancelled sale; fully returned one existing
  sale to demonstrate refunds. Final: 2 draft, 28 confirmed, 1 cancelled, 1 reversed.
- Verified all 3 logins and role-specific routing/403s via Django authentication/HTTP.
- Stock quantity/value reconcile with ledger: 0 mismatches. Source behavior unchanged.
- Next action: user opens /login/; credentials available in the private runtime file.

## Re-test and teaching handoff — 03/11/2026

Approved request: re-test app/seed and make architecture easy to read/present.
- Added module responsibility docstrings and short descriptions of key use cases.
- Expanded ARCHITECTURE.md: module/layer map, ERD, sequence, document states,
  dashboard flow and source/test map. Added PRESENTATION.md (8–10 minute demo + Q&A).
- Added read-only inventory.checks and check_business_data command; 3 behavioral
  tests verify seed guard, correct data and detection of corrupted test balances/totals.
- Gate: 52 tests passed, coverage 90.52%, Ruff/format 74 files, system/migration checks pass.
- Main demo remains 3 users, 8 products, 1 supplier, 3 customers, 32 docs, 69 movements;
  check_business_data reports no errors. Full data report: docs/data-check.json.
- 12 browser check groups on an isolated pg_dump copy; tests mutated only that copy.
  All three roles, draft confirm, return, oversell block, polling, network failure and mobile passed.
- Site 8010 also logged in read-only and dashboard/actual seed verified; screenshots refreshed.
- Review context/server closed, review DB dropped. Main app still serves 8010.
- No schema change or trading behavior change, no commit/push.
Next: read PRESENTATION.md; use seed dates 21/10–03/11/2026 when demonstrating later.

## Direct row delete / short UI review — 03/11/2026

User authorized direct removal in create sale/purchase and brief UI/UX recheck.
- document.js now marks DELETE, hides/disables removed controls, offers latest undo,
  preserves form indices and reuses deleted slots. No schema/service contract change.
- Form template adds empty/status/undo feedback. CSS aligns delete action on mobile
  and makes non-field errors span form width. No general redesign.
- 6 new HTTP regressions: deleted invalid row ignored, existing draft row removed,
  correct totals and empty-document rejection, both kinds. Total 58 passed, coverage
  90.77%; all remaining gates pass.
- Browser includes remove/undo/edit, keyboard, empty validation, 105 add/remove cycles,
  desktop/mobile and main page navigation; no JS errors; browser-row-delete.json.
- Main data was 33 docs/71 movements before work (user changes since original seed).
  No reset; tested writes on own clone, audited clone and main successfully.
- Test context/server/database removed; main app restarted at 8010, session 86110.
- README/architecture/presentation updated. No commit/push requested or performed.
Next: refresh form on 8010 and use Xóa dòng/Hoàn tác.

## User correction: use × only — 03/11/2026

Screenshot showed visible Bỏ dòng checkbox despite prior source update. Now DELETE
is HiddenInput and × is rendered in shared document_line.html (not JS-created).
JS reads/writes the hidden boolean value; asset URLs versioned row-x-2. Browser
cache was a possible explanation for screenshot mismatch, not conclusively proven.
Both create/edit HTTP contracts remain unchanged. 60 tests pass; lint/format and
Django/migration checks pass. Live browser verified purchase/sale X, hidden checkbox,
undo, initial undo hidden; mobile X and no overflow. Main server restarted (44870).
Read-only browser session closed; no demo document saved or account passwords exposed.

## Replace existing public repository — 03/11/2026

User explicitly authorized overriding AnPham99/learning-log with StoreDesk.
- Verified target public, main clean/up-to-date at 6c764f1.
- StoreDesk verify.sh: 60 tests passed; lint/format/check/migrations passed.
- README made portable; gitignore protects runtime, demo credentials and backups.
- Attach current StoreDesk directory to existing remote history, stage replacement tree,
  audit files, commit and normal push. Keep old commits; no force-push.
- Current step: preparing replacement commit and publication.
