# Project Status

## Current Phase
Phase 10 — customer and merchant experiences completed; driver/admin management screens next.

## Completed Phases
Backend phases 1–8 complete. Customer UI includes Arabic RTL responsive catalog/search/filter/sort, merchant browsing/favorites/reviews, authentication, cart/checkout, address management/geolocation, order history/tracking/cancellation, notifications and profile. Shared operational order actions present; role management/dashboard pages remain.

## Current Implementation State
Customer UI uses real backend APIs and HttpOnly cookie/CSRF sessions. All backend flows implemented. Operational management screens and final deployment docs remain.

## Last Completed Task
Implemented live role dashboards, merchant product add/edit/availability, category add/edit and business open/close profile. Admin-only merchant listing exposes unapproved businesses for management without changing public visibility.

## Next Task
Implement driver availability/heartbeat/location sharing and admin users/drivers/map/city/area management. Run complete four-role browser delivery journey and finalize deployment preparation.

## Pending Tasks
Operational role screens and browser tests; production Docker/reverse proxy preparation; final README/API export/deployment/handoff documentation. No paid deployment authorized.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 verified locally on SQLite and online on PostgreSQL 17 in GitHub Actions. No schema drift.

## Tests Status
Customer and merchant browser tests both passed (2 Chromium tests), including checkout/cancel, mobile overflow, product creation/hide/show and business open/close. TypeScript/Vite build passes; catalog authorization tests and Ruff pass. Backend 23 local tests plus 3 PostgreSQL concurrency tests already verified in remote CI.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
All work on main. Audit b12de60 is remote. Checkpoint commits are created through GitHub Git data API because local push transport lacks credentials; local and remote trees are compared before local ref synchronization. No feature branches or PRs.

## Last Stable Commit
80530278348ba2e5e2b30e806dc161432e46a95b (customer UI); use git log for merchant UI checkpoint.

## How to Continue in a New Session
Read README, this file and docs/DECISIONS.md; inspect git status, branches and recent log; pull --ff-only
when clean, on main only. Inspect implemented code/migrations/tests before editing. Run checks, update this file,
review staged diff for secrets, commit and push each completed phase. No paid infrastructure authorized.
