# Project Status

## Current Phase
Phase 10 — integrated customer web experience completed; merchant/driver/admin dashboards next.

## Completed Phases
Backend phases 1–8 complete. Customer UI includes Arabic RTL responsive catalog/search/filter/sort, merchant browsing/favorites/reviews, authentication, cart/checkout, address management/geolocation, order history/tracking/cancellation, notifications and profile. Shared operational order actions present; role management/dashboard pages remain.

## Current Implementation State
Customer UI uses real backend APIs and HttpOnly cookie/CSRF sessions. All backend flows implemented. Operational management screens and final deployment docs remain.

## Last Completed Task
Recovered unfinished UI from nested local folder, fixed compilation, formatted source, and ran real Chromium login/checkout/pending cancellation plus mobile navigation/overflow test.

## Next Task
Implement merchant products/profile/dashboard, driver availability/location/dashboard, admin users/drivers/map/cities/dashboard; run four-role browser workflow; finalize packaging and CI browser tests.

## Pending Tasks
Operational role screens and browser tests; production Docker/reverse proxy preparation; final README/API export/deployment/handoff documentation. No paid deployment authorized.

## Known Issues
Local Git transport has no credential; authorized GitHub connector publishes reviewed commits with non-forced ref updates. Local native PostgreSQL installation/start is unavailable due environment OS restrictions; validate PostgreSQL via CI service. Legacy SQL seed remains reference only.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 verified locally on SQLite and online on PostgreSQL 17 in GitHub Actions. No schema drift.

## Tests Status
23 backend tests passed locally; 3 PostgreSQL-only tests skipped locally. Remote d9de95b CI succeeded including PostgreSQL concurrency tests. TypeScript/Vite build passed. Real Chromium customer checkout/cancellation/mobile test passed (1 test). Standard browser download failed locally; packaged Chromium used via E2E_CHROMIUM_EXECUTABLE.

## Environment / Setup Notes
Python 3.12 virtualenv .venv and Node 24 available. Run scripts/setup_env.py once (does not overwrite an existing .env); Docker Compose supplies PostgreSQL 17 on host port 5433. Never print/commit .env.

## Git / Branch Status
All work on main. Audit b12de60 is remote. Checkpoint commits are created through GitHub Git data API because local push transport lacks credentials; local and remote trees are compared before local ref synchronization. No feature branches or PRs.

## Last Stable Commit
d9de95b6c8e5c7e6fa330da557b1f8ff5fa1824e (backend delivery); use git log for customer UI checkpoint.

## How to Continue in a New Session
Read README, this file and docs/DECISIONS.md; inspect git status, branches and recent log; pull --ff-only
when clean, on main only. Inspect implemented code/migrations/tests before editing. Run checks, update this file,
review staged diff for secrets, commit and push each completed phase. No paid infrastructure authorized.
