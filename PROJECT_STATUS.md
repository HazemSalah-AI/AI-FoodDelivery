# Project Status

## Current Phase
Phase 7.2–7.5 — account management, catalog and addresses completed; cart/checkout next.

## Completed Phases
Audit, executable foundation, relational schema/migrations, API design/architecture; JWT sessions, Argon2, CSRF, origin checks, account activation checks, role dependencies, registration/login/logout/profile, explicit admin bootstrap.

## Current Implementation State
Identity, catalog, account management and address APIs implemented. Order workflows, role UIs and final deployment packaging remain.

## Last Completed Task
Implemented role-protected admin user creation/activation, merchant profile/approval, category/product management, search/filter/sort/pagination, cities/areas and owned address CRUD with archive/default rules.

## Next Task
Implement transactional server cart, checkout repricing/stock reservation/idempotency, order history and merchant/customer transitions.

## Pending Tasks
Phases 2–11: foundation, migrations, API, architecture, security, domains, tests, UI, deployment preparation.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 verified locally on SQLite and online on PostgreSQL 17 in GitHub Actions. No schema drift.

## Tests Status
14 backend tests passed; Ruff check/format pass. Tests cover catalog cross-owner denial, categories, active merchant visibility, admin roles, duplicate accounts, address defaults/ownership/archive and field/query validation. PostgreSQL fixture sequences explicitly synchronized after deterministic test seeding.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
All work on main. Audit b12de60 is remote. Checkpoint commits are created through GitHub Git data API because local push transport lacks credentials; local and remote trees are compared before local ref synchronization. No feature branches or PRs.

## Last Stable Commit
9352715a8a9a112076aea9f83a1fafa05c6d0b8c (authentication); use git log for catalog checkpoint.

## How to Continue in a New Session
Read README, this file and docs/DECISIONS.md; inspect git status, branches and recent log; pull --ff-only
when clean, on main only. Inspect implemented code/migrations/tests before editing. Run checks, update this file,
review staged diff for secrets, commit and push each completed phase. No paid infrastructure authorized.
