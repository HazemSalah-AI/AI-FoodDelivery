# Project Status

## Current Phase
Phases 7–8 — backend MVP domains implemented and locally validated; PostgreSQL concurrency CI and frontend integration next.

## Completed Phases
Audit; foundation; schema/migrations; API design; security; all backend domains including assignments/reassignment, delivery, heartbeat/location, notifications, dashboards, merchant reviews and favorites.

## Current Implementation State
All core role APIs and business transitions work. Role interfaces and production packaging remain. Driver location uses an explicit admin-only response schema; writing location returns only timestamp.

## Last Completed Task
Verified full assignment rejection/reassignment/acceptance/pickup/delivery flow, COD reporting, notification ownership, merchant reviews, favorites and stale-driver handling. Added three PostgreSQL race tests.

## Next Task
Validate PostgreSQL CI; build integrated customer screens, then merchant/driver/admin dashboards with browser workflow tests.

## Pending Tasks
Phases 2–11: foundation, migrations, API, architecture, security, domains, tests, UI, deployment preparation.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 verified locally on SQLite and online on PostgreSQL 17 in GitHub Actions. No schema drift.

## Tests Status
23 tests passed locally; 3 PostgreSQL concurrency tests skipped locally by explicit environment guard. Ruff passes. Concurrency tests cover accept-vs-cancel, two orders assigned to one driver, and competing checkouts for one unit. PostgreSQL execution must be confirmed in CI before claiming those passed.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
All work on main. Audit b12de60 is remote. Checkpoint commits are created through GitHub Git data API because local push transport lacks credentials; local and remote trees are compared before local ref synchronization. No feature branches or PRs.

## Last Stable Commit
99bfcf1f919e27296d0e36d711a0b45738196a41 (checkout); use git log for delivery checkpoint.

## How to Continue in a New Session
Read README, this file and docs/DECISIONS.md; inspect git status, branches and recent log; pull --ff-only
when clean, on main only. Inspect implemented code/migrations/tests before editing. Run checks, update this file,
review staged diff for secrets, commit and push each completed phase. No paid infrastructure authorized.
