# Project Status

## Current Phase
Phase 7.6–7.9 — transactional cart/checkout and order lifecycle completed; assignment/location/notification APIs next.

## Completed Phases
Audit, executable foundation, relational schema/migrations, API design/architecture; JWT sessions, Argon2, CSRF, origin checks, account activation checks, role dependencies, registration/login/logout/profile, explicit admin bootstrap.

## Current Implementation State
Functional auth/catalog/cart/checkout/order APIs. Order state transitions are explicit and tested. Assignment and ancillary APIs plus frontend integration remain.

## Last Completed Task
Implemented server-side cart, one-merchant enforcement, current-price checkout, stock reservation, idempotency, address/item snapshots, order privacy/ownership, state-machine transitions, history and transactional notifications.

## Next Task
Implement admin assignment, driver acceptance/rejection/delivery/location, notification reads, dashboards, merchant reviews and favorites; add end-to-end backend tests and PostgreSQL concurrency tests.

## Pending Tasks
Phases 2–11: foundation, migrations, API, architecture, security, domains, tests, UI, deployment preparation.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 verified locally on SQLite and online on PostgreSQL 17 in GitHub Actions. No schema drift.

## Tests Status
20 backend tests passed locally; Ruff passes. Latest catalog checkpoint GitHub Actions succeeded on PostgreSQL 17. Checkout tests verify repricing, retry safety, rollback, stock restoration once, address ownership, snapshot preservation and cancellation denial after acceptance.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
All work on main. Audit b12de60 is remote. Checkpoint commits are created through GitHub Git data API because local push transport lacks credentials; local and remote trees are compared before local ref synchronization. No feature branches or PRs.

## Last Stable Commit
d826e68e1e3292b45375e4b3a20a2d292f8bfc07 (catalog); use git log for checkout checkpoint.

## How to Continue in a New Session
Read README, this file and docs/DECISIONS.md; inspect git status, branches and recent log; pull --ff-only
when clean, on main only. Inspect implemented code/migrations/tests before editing. Run checks, update this file,
review staged diff for secrets, commit and push each completed phase. No paid infrastructure authorized.
