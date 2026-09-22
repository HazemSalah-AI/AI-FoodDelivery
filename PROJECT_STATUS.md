# Project Status

## Current Phase
Phase 2 — executable foundation completed; database implementation next.

## Completed Phases
Phase 1 audit published to main as b12de60. Phase 2 adds bootable FastAPI and React/TypeScript/Vite, typed configuration, secure environment generator, database session foundation and PostgreSQL Compose service.

## Current Implementation State
Backend health and OpenAPI work; frontend builds. Business endpoints and migrations not implemented yet.

## Last Completed Task
Validated app boot, configuration rejection and frontend production build.

## Next Task
Implement relational models and explicit Alembic migrations, then publish API design and authentication.

## Pending Tasks
Phases 2–11: foundation, migrations, API, architecture, security, domains, tests, UI, deployment preparation.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Session management and SQLite foreign-key enforcement implemented; migration schema is next.

## Tests Status
2 backend tests passed; Ruff check and format passed; TypeScript and Vite production build passed. TestClient upstream deprecation warnings are informational.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
All work on main. Audit b12de60 is remote. Checkpoint commits are created through GitHub Git data API because local push transport lacks credentials; local and remote trees are compared before local ref synchronization. No feature branches or PRs.

## Last Stable Commit
b12de600b151db2dd94cb57121530e53e51c1f28 (audit); use git log for the foundation checkpoint.

## How to Continue in a New Session
Read README, this file and docs/DECISIONS.md; inspect git status, branches and recent log; pull --ff-only
when clean, on main only. Inspect implemented code/migrations/tests before editing. Run checks, update this file,
review staged diff for secrets, commit and push each completed phase. No paid infrastructure authorized.
