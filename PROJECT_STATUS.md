# Project Status

## Current Phase
Phase 11 — production packaging checkpoint implemented; remote container validation follows this push.

## Completed Phases
Backend phases 1–8 complete. Customer, merchant, driver and admin Arabic RTL interfaces complete, including operational dashboards, account/catalog/area management, assignment/reassignment and admin-only driver location.

## Current Implementation State
All four role workflows remain implemented. Container packaging is pushed; first CI found an incorrect Docker COPY path for migrations. Corrected to backend/migrations and its matching build-context allowlist. Remote runtime verification is being repeated. No live deployment or paid infrastructure created.

## Last Completed Task
Implemented container/HTTPS packaging, readiness, private API cache headers, session-expiry recovery and CI. Fixed the migration directory COPY path identified by the first remote container build.

## Next Task
Verify the packaging checkpoint CI results and fix any failures within this checkpoint. Next development checkpoint: finish the API import/export artifact and concise final acceptance/handoff documentation. Do not restart completed implementation.

## Pending Tasks
Remote container CI confirmation; API import/export artifact and final acceptance/handoff review. No live deployment authorized.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 verified locally on SQLite and online on PostgreSQL 17 in GitHub Actions. No schema drift.

## Tests Status
23 backend tests passed locally; 3 PostgreSQL-only tests skipped locally (run by CI). Migration upgrade/check/downgrade now verifies readiness; auth test verifies private no-store headers. All 4 Chromium browser journeys passed including expired-session recovery. TypeScript/Vite build, Ruff and YAML parsing passed. Docker is absent locally; new CI builds both images and boots PostgreSQL/migrations/API/Nginx, validates Caddy and reruns browser tests.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
Latest user instruction requires the existing default branch. GitHub reports master. Local master was fast-forwarded through all tested main commits; this checkpoint is published to master without force push. main remains preserved. Connector publishes Git data commits because local Git has no write credentials.

## Last Stable Commit
17a3ed8863675b58059fba184bbcc80126ab9a80 — complete four-role UI and browser coverage, before this packaging checkpoint.

## How to Continue in a New Session
Read this file first and inspect only files relevant to Next Task. Use the current GitHub default branch (master at this checkpoint), inspect git status, and pull --ff-only when clean. Complete one useful tested checkpoint, update this file, review for secrets, commit and push, then stop unless instructed otherwise. No paid infrastructure or live deployment authorized.
