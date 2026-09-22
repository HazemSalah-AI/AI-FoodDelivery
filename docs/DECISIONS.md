# Architecture and business decisions

## 2026-09-22 — initial audit

- Baseline `83648e8` contains diagrams, SQL learning scripts and Git notes; no runnable app, dependency files, migrations, README, status file or tests. At initial audit, the only branch was unprotected `master`. Superseded by the user's explicit instruction below.
- Preserve `DataBase/` as historical reference. Its seed uses plaintext examples; it is NOT application bootstrap data. No automatic import or destructive migration of a user's existing database.
- Rename `Docs/` to `docs/` to match requested paths and avoid two names differing only by case on Windows.
- Canonical order states: Pending, Accepted, Preparing, Ready, OnDelivery, Delivered, Rejected, Cancelled. The ERD's Assigned is assignment state; Picked_Up means OnDelivery. Driver acceptance does not imply physical pickup. Ignore erroneous cancellation arrows after acceptance; explicit written cancellation rule governs.
- Assignment is a separate table with Pending/Accepted/Rejected/Completed states. Assign only Ready orders; one active assignment per order and driver. Reject releases the reservation. Preserve history.
- Unified users table for credentials and a single role, with separate merchant and driver profiles. This avoids duplicating security and enables one notification recipient FK, including admins. Domain ownership remains explicit.
- One merchant per cart and order. Reserve stock at checkout and restore on rejection/cancellation transactionally. Preserve item names/prices and address snapshot at checkout.
- Prices are EGP decimal values; delivery fee is initially zero, stated in checkout. No commission or driver earnings formula was supplied, so report COD collected separately, never call that driver income.
- Merchant reviews are in DFD and approved notes: allow one review per delivered order, merchant only. Favorites are in the use-case diagram and can use a simple customer/merchant relation.
- Driver availability uses a 30-minute heartbeat timeout from the use-case notes. An active assignment also blocks further assignment, regardless of the availability toggle.
- Local accounts are bootstrapped by explicit CLI with prompted/env passwords; no default reusable passwords. Admin creates merchant/driver users. Customer registration cannot choose privileged roles.
- PostgreSQL is authoritative; SQLite may be used for fast integration checks only, with explicit FK enforcement. PostgreSQL migration and concurrency behavior require dedicated validation.

## 2026-09-22 — continuation on main

- User explicitly requires all development/checkpoints directly on `main`; no feature branches or pull requests. Remote `main` was absent, so it was created from existing baseline `83648e8`, preserving history. The local branch was renamed to `main`.
- GitHub connector branch creation now succeeds. Use authenticated GitHub operations for checkpoints if local Git transport has no write credential. Never force push; verify each remote tree and branch after publishing.
