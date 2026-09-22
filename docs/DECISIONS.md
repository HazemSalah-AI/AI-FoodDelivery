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

## 2026-09-22 — operational browser experience

- Role-specific Arabic RTL screens call the same authorized APIs as the integration tests. Drivers explicitly enable location sharing in their browser; sharing stops when the app closes. Heartbeats run while the page is visible. Availability expires after 30 minutes without activity.
- Only the admin screen retrieves driver coordinates. Its map embeds OpenStreetMap for the selected driver's last reported location, with the timestamp shown. No location is synthesized. OpenStreetMap receives the selected coordinates to render the map; no paid map service or API key is used.
- Driver rejection releases an assignment; the admin chooses another available driver. Driver acceptance is separate from pickup and cash collection/delivery confirmation.
- Dashboards display lifetime counts and delivered COD totals; these totals are not driver earnings. The delivery fee remains zero per the earlier MVP decision.

## 2026-09-22 — deployment checkpoint and branch instruction

- Latest user instruction supersedes the earlier main-only instruction: work on the existing default branch. GitHub reports `master`. Fast-forward master through the tested main history, then publish this checkpoint there without deleting main or rewriting history.
- Production uses private PostgreSQL/backend/frontend containers and a Caddy HTTPS edge; development retains PostgreSQL-only mode and adds an opt-in full app profile. Migrations run explicitly before API startup. Both app images run as non-root users.
- API responses disable caching of session/order/location data. Readiness verifies database connectivity and a nonempty migration revision; liveness remains independent. Session expiry returns the browser to login, and proxy errors receive a readable fallback.
- Container builds and runtime checks run in GitHub Actions because Docker is not available in this workspace. No live deployment, DNS changes or paid resources are part of this checkpoint.
