# Project Status

## Current Phase
Phases 4–5 — API contracts and transaction/access architecture documented; security implementation next.

## Completed Phases
Phase 1 audit (b12de60); Phase 2 executable foundation (71343b3); Phase 3 adds all core models, explicit reversible migration, database documentation and main-branch CI.

## Current Implementation State
Models and migration cover users, sessions, catalog, carts, purchases, history, driver assignments, notifications, reviews, favorites and audit. Business APIs remain to be implemented.

## Last Completed Task
Documented all important endpoint methods, access, inputs, responses, validation, pagination/search/sort and error conventions.

## Next Task
Implement the documented authentication and authorization contracts with role, CSRF, revocation and validation tests.

## Pending Tasks
Phases 2–11: foundation, migrations, API, architecture, security, domains, tests, UI, deployment preparation.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 creates 19 application tables (plus Alembic version tracking). Use alembic upgrade head on a fresh database; historical SQL is not auto-imported.

## Tests Status
4 backend tests pass from schema checkpoint; API contract cross-checked against original requirements and model ownership. Documentation whitespace validation passed.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
All work on main. Audit b12de60 is remote. Checkpoint commits are created through GitHub Git data API because local push transport lacks credentials; local and remote trees are compared before local ref synchronization. No feature branches or PRs.

## Last Stable Commit
16dc978b2782e63b5cb22e3b38ce354174e76113 (schema); prior stages published to main.

## How to Continue in a New Session
Read README, this file and docs/DECISIONS.md; inspect git status, branches and recent log; pull --ff-only
when clean, on main only. Inspect implemented code/migrations/tests before editing. Run checks, update this file,
review staged diff for secrets, commit and push each completed phase. No paid infrastructure authorized.
