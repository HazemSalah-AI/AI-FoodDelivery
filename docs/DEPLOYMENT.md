# Container deployment

The repository prepares deployment; it does not create cloud resources or configure DNS.
Docker Engine with Compose v2 is required. Use `master`, the current default branch.

## Local full stack

From the root, run `python scripts/setup_env.py` once to generate an ignored `.env`.
It refuses to overwrite existing credentials. Then:

```bash
docker compose --profile app up --build -d
docker compose exec backend python -m app.bootstrap
```

Open http://localhost:8080. Optionally run `docker compose exec backend python -m app.seed_demo`
on a development database for sample role accounts/catalog. Choose passwords when prompted.
Only localhost exposes the web app and development database. For host development with Vite,
use the original README instructions and `docker compose up -d db`.

## Production HTTPS

Use an approved server and domain. No AWS resources or paid services are created by these files.
Point the domain to the server, allow inbound TCP 80/443, restrict administrative access, and do
not expose PostgreSQL or backend ports. The production file is standalone, not a Compose override.

1. Clone the repository on the server. Generate a fresh `.env` with `python scripts/setup_env.py`;
   never copy development/test credentials. Add `DOMAIN=your-real-domain` to that private file.
   Keep generated hexadecimal passwords (URL-safe); protect the file with owner-only permissions.
2. Validate without printing secrets: `docker compose -f docker-compose.prod.yml config --quiet`.
3. Run `docker compose -f docker-compose.prod.yml up --build -d`.
4. Create the initial administrator: `docker compose -f docker-compose.prod.yml exec backend python -m app.bootstrap`.
5. Check `https://your-real-domain/api/v1/ready`, login, and test a real device's location permission.

Caddy obtains HTTPS certificates when DNS/reachability are correct. The production stack forces
secure cookies, an explicit HTTPS origin and PostgreSQL regardless of development settings in `.env`.
Nginx serves the built React app and proxies same-origin API requests. Only Caddy publishes ports.
The backend trusts forwarded IPs only because it is private behind this proxy chain; do not expose
its port. Nginx applies a shared per-IP authentication limit in addition to the application limiter.
The admin map needs access to OpenStreetMap; Google Fonts is optional with local font fallback.

## Update and recovery

Back up before changing application/database versions. A backup contains personal data; store it
outside the repository, encrypt it and test restoration in an isolated database. Example backup:

```bash
umask 077
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U delivery -d delivery -Fc > delivery-backup.dump
```

On an approved update, pull the tested commit, build, then explicitly run the migration before
recreating services:

```bash
git pull --ff-only
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml run --rm migrate
docker compose -f docker-compose.prod.yml up -d --force-recreate backend frontend edge
```

Check readiness and the order flow after each update. Pin a tested Git commit for rollback; do not
downgrade a production schema blindly. Restore only into a separately verified target database.
Do not use `down --volumes` on production: that deletes data and certificate storage.
This single-host MVP is not highly available. Scheduled encrypted backups, monitoring and a tested
restore procedure are operator responsibilities before real customer use. No demo seeding in production.
