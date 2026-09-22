# Project Status

## Current Phase
Phase 6 / 7.1 — authentication and authorization foundation implemented; catalog and account-management domains next.

## Completed Phases
Audit, executable foundation, relational schema/migrations, API design/architecture; JWT sessions, Argon2, CSRF, origin checks, account activation checks, role dependencies, registration/login/logout/profile, explicit admin bootstrap.

## Current Implementation State
Working authenticated API and revocable sessions. Catalog and order domain routes are next; frontend still foundation only.

## Last Completed Task
Implemented security and validated registration, duplicate handling, logout replay rejection, CSRF/origin checks, public-role rejection, suspended sessions and auth throttling.

## Next Task
Implement admin account management, merchant catalog/profile, cities/areas, addresses and public browsing with ownership tests.

## Pending Tasks
Phases 2–11: foundation, migrations, API, architecture, security, domains, tests, UI, deployment preparation.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 verified locally on SQLite and online on PostgreSQL 17 in GitHub Actions. No schema drift.

## Tests Status
10 backend tests passed; Ruff passes. GitHub Actions on schema and API-design commits succeeded, including online PostgreSQL 17 migration upgrade/check and frontend build.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
All work on main. Audit b12de60 is remote. Checkpoint commits are created through GitHub Git data API because local push transport lacks credentials; local and remote trees are compared before local ref synchronization. No feature branches or PRs.

## Last Stable Commit
4f05c86868c9a60d4ec6a86f5d9973297b4c1e5c (API contracts); use git log for security checkpoint.

## How to Continue in a New Session
Read README, this file and docs/DECISIONS.md; inspect git status, branches and recent log; pull --ff-only
when clean, on main only. Inspect implemented code/migrations/tests before editing. Run checks, update this file,
review staged diff for secrets, commit and push each completed phase. No paid infrastructure authorized.
