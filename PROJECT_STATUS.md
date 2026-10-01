# Project Status

## Current Phase
API import/export and concise acceptance/handoff checkpoint complete and locally validated (2026-10-01).

## Completed Phases
Backend phases 1–8, all four Arabic RTL role interfaces, phase 11 deployment packaging, and API
import/export plus acceptance/handoff complete. Operational dashboards, account/catalog/area
management, assignment/reassignment and admin-only driver location are implemented.

## Current Implementation State
All four role workflows and container packaging are implemented. docs/api/ contains an unmodified
OpenAPI 3.1 snapshot, a cookie/CSRF-aware Postman v2.1 collection and a blank local environment,
covering all 55 operations. docs/API_CLIENT.md explains import, login, role switches and retry keys.
docs/ACCEPTANCE_HANDOFF.md records evidence and remaining limits. No live hosting, DNS changes or
paid cloud resources were created. Application code and migrations are unchanged in this checkpoint.

## Last Completed Task
Added scripts/export_api.py with database-free deterministic generation, runtime input validation,
route/doc coverage and --check drift detection; CI now runs the exporter lint/format and drift checks.
Corrected API docs for runtime path parameter names, full-model PATCH inputs, decimal coordinates,
origin validation and availability heartbeat behavior. Documented generated OpenAPI security/error/
untyped-response gaps and backend-only /openapi.json and /docs URLs. Completed the focused handoff
review and reran existing backend/browser acceptance checks plus all-operation Newman verification.
Final export refinement derives optional filter values from schema enums and safely JSON-escapes
credential strings; the client rerun passed with quotes/backslashes and the optional role filter.

## Next Task
This requested checkpoint is complete. Await a separately authorized next checkpoint. Before real
customer rollout, follow docs/DEPLOYMENT.md and docs/ACCEPTANCE_HANDOFF.md for HTTPS/device checks,
monitoring, encrypted backups and a tested restore. An optional contract-only follow-up can add
accurate runtime OpenAPI cookie/CSRF declarations, error metadata and typed operational responses.

## Pending Tasks
No tasks remain within this checkpoint. Actual hosting/domain setup needs separate authorization
and credentials. Operator launch checks, load/capacity verification and physical-device testing remain.

## Known Issues
Generated OpenAPI lacks cookie/CSRF security declarations and most domain errors; automatic 422
differs from the custom error envelope, and health/readiness/location-update success bodies are
untyped. Companion docs/collection cover the usable workflow. /ready checks a nonempty revision,
not migration-head/schema equality. Postman desktop import, physical-device GPS, other browsers,
live HTTPS deployment, backup restoration, monitoring and load capacity are not verified. External
admin map sends selected coordinates to OpenStreetMap and requires access. Dependency deprecation
warnings are non-failing; legacy SQL seed is reference only. Windows shared pytest temp permissions
required a fresh task-owned --basetemp; the rerun passed. No complete security-audit signoff is implied.

## Important Architecture Decisions
See docs/DECISIONS.md. Unified auth identity, separate assignments, one-merchant cart, canonical state machine.

## Database / Migration Status
Revision 342305e2a522 verified again on a disposable local PostgreSQL 17 container with alembic
upgrade head/check, and by existing SQLite migration tests. No schema drift; no migration changes.
Disposable API/database processes and private test files were cleaned up.

## Tests Status
Fresh local checks: all 26 backend tests passed on PostgreSQL 17, including 3 concurrency cases;
alembic upgrade/check; backend/exporter Ruff lint and format; TypeScript/Vite production build;
all 4 Chromium browser tests; OpenAPI 3.1 and official Postman v2.1 JSON schema validation; live
/openapi.json equals the snapshot; Newman 6.2.2 sent 69 requests covering all 55 operations with
69 passing assertions; exporter --check, intentional stale-output/invalid-example rejection, CI YAML
and git diff --check passed. Container evidence is inherited from unchanged deployment files:
GitHub Actions run 35771970349 on eae8735; both jobs rechecked successful. Initial checkpoint
9cbe073 passed both jobs in run 36921976684, including the new artifact check. Final export-only
refinement has passed local schema/exporter/Newman verification; its remote run is pending.

## Environment / Setup Notes
Python 3.12.14 virtualenv .venv, Node 24.15 and Docker are available in this worktree. Export from
root with python scripts/export_api.py; use --check for verification. Export does not need .env,
database connectivity or test-only schema validators/Newman packages. Normal app setup remains in
README.md: run scripts/setup_env.py once; never print/commit .env. Tests used isolated ephemeral
credentials and a disposable PostgreSQL container, with no existing database modified.

## Git / Branch Status
Existing default branch is master. This app-created worktree started detached at 64f8d06; master
is checked out in the primary worktree, whose files/branch were not moved. Initial checkpoint
9cbe07358f29f910206155cb0babab9d5ffa1c2e was committed here and published to master using a
normal non-forced local Git push; remote SHA verified. Other worktrees and main remain preserved.
Publish the tested export-only refinement the same way; its publication/remote CI are pending.

## Last Stable Commit
Deployment runtime baseline: eae87353f5ac7617338e801479d23bc7407ef5e0, validated in GitHub Actions
run 35771970349. Resume baseline: 64f8d06c46e2de71d28e4d9a7823b9b452c38d0b. The following API
handoff checkpoint 9cbe07358f29f910206155cb0babab9d5ffa1c2e passed remote run 36921976684.
Resolve the final export refinement through git log after its publication.

## How to Continue in a New Session
Read this file and docs/ACCEPTANCE_HANDOFF.md first. This checkpoint is complete: do not restart a
broad audit or rebuild completed features. Use the current GitHub default branch and inspect git
status/worktree ownership before a clean fast-forward pull. Regenerate API artifacts after route/
model changes and run --check. Complete only the next user-authorized checkpoint, update this file,
review for secrets, commit/push without force and stop. No live deployment or paid infrastructure
is authorized by this checkpoint.
