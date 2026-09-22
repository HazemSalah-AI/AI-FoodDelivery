# Project Status

## Current Phase
Phase 10 complete — all four role experiences validated. Final production preparation next.

## Completed Phases
Backend phases 1–8 complete. Customer, merchant, driver and admin Arabic RTL interfaces complete, including operational dashboards, account/catalog/area management, assignment/reassignment and admin-only driver location.

## Current Implementation State
All four roles use actual backend APIs. Browser delivery flow validated through rejection, reassignment, delivery and review. Production deployment preparation remains.

## Last Completed Task
Added driver availability/heartbeat/explicit location sharing, admin account creation and suspension, merchant approval, driver map and delivery areas.

## Next Task
Prepare production Docker/reverse proxy configuration, expand CI to browser/container checks, finalize README/API/deployment/handoff documentation.

## Pending Tasks
Production packaging; final README/API/deployment documentation and expanded CI. No paid deployment authorized.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 verified locally on SQLite and online on PostgreSQL 17 in GitHub Actions. No schema drift.

## Tests Status
4 Chromium browser tests passed: customer checkout/cancel/mobile, merchant management, admin account/area management, full four-role delivery/reassignment/location privacy/review. Backend 23 passed locally; 3 PostgreSQL-only concurrency tests skipped locally and passed in prior CI. TypeScript/Vite build and Ruff pass. Admin map layout reviewed; external map rendering depends on OpenStreetMap network access.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
All work on main. Audit b12de60 is remote. Checkpoint commits are created through GitHub Git data API because local push transport lacks credentials; local and remote trees are compared before local ref synchronization. No feature branches or PRs.

## Last Stable Commit
3cccabdcba8fa3ee29ab681b5360ebce0e055832 (merchant dashboard and management).

## How to Continue in a New Session
Read README, this file and docs/DECISIONS.md; inspect git status, branches and recent log; pull --ff-only
when clean, on main only. Inspect implemented code/migrations/tests before editing. Run checks, update this file,
review staged diff for secrets, commit and push each completed phase. No paid infrastructure authorized.
