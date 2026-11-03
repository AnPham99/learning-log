# StoreDesk — approved scope

Source: user request for Django inventory/sales/dashboard, and "ok go" approving
single store, single warehouse, internal sales, manual cash/bank payments and
10-second dashboard refresh. Separate project; no migration of Learning Log.

## Acceptance
1. First-run manager setup; manager creates warehouse/sales accounts. Role checks
   enforced in services and HTTP. No public signup after setup.
2. Products (SKU, name, category, unit, selling price, low-stock threshold, active),
   suppliers and customers: searchable lists, creation and edit. Used records archived.
3. Multi-line purchase receipts: draft, confirm, cancel. Confirm increases stock.
4. Multi-line sales: draft, confirm with payment (cash/bank), cancel/return entire sale.
   Confirm decreases stock. Product prices/names snapshot when saving draft; weighted-average cost snapshot at
   confirmation; discount fixed VND amount; fully paid sales only, no debt.
5. Confirm is idempotent. Drafts do not affect stock. Confirmed documents immutable.
   Reversal keeps audit history. Receipt reversal rejected if stock has been sold or
   a later movement exists. Sale full return restores original cost and stock once.
6. No negative stock under concurrent sales. Use PostgreSQL row locks and atomic
   transactions; deterministic product locking. Persistent inventory movement ledger.
7. Manager inventory adjustment requires reason and creates ledger entry.
8. Dashboard: revenue (net completed sales minus dated full returns), collected cash,
   refunds, gross profit using moving weighted-average cost, daily chart, top products,
   recent sales and low-stock products. Date filter <=366 days; local Vietnam timezone;
   JSON polling every 10 seconds without losing date filter; visible refresh/error state.
9. Paginated searchable operational lists, Vietnamese responsive SSR UI; local assets.
10. Local runner prepares environment, manages isolated PostgreSQL cluster (55432),
    migrates, launches loopback web (8010), opens browser. Durable files under var/.
    Support external PostgreSQL environment configuration. README + tests + handoff.

Decisions: generic unit-count retail products; integer quantities, VND with 0 decimal
places, no VAT/shipping/variants/expiry/serial/multiple warehouses. No online checkout,
partial payment, partial return, accounting compliance or cloud deployment. These
require separate scope. User subsequently authorized replacing the existing public AnPham99/learning-log repo with StoreDesk on 03/11/2026.

## Verification
Tests on actual PostgreSQL, including multithread concurrent sales/duplicate confirm,
rollback, reversal, permissions, CSRF, price snapshots and dashboard date semantics.
Browser verify complete manager flow plus restricted user, desktop/mobile and polling.

## Direct row removal — user request 03/11/2026

Create/edit sale and purchase forms have a direct Xóa dòng button, immediate removal
and undo for the latest removal. Deleted invalid fields do not block save; empty
documents remain rejected. Repeated delete/add reuses slots without breaking formset
indices. Verify create/edit for both kinds, keyboard, mobile and remaining totals.
