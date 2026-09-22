"""Run browser tests against an isolated migrated database; no external systems modified."""

import os
import secrets
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]


def wait_ready(url, process):
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError("Test server exited before becoming ready")
        try:
            with urllib.request.urlopen(url, timeout=1):
                return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError(f"Test server did not start: {url}")


def main():
    with tempfile.TemporaryDirectory(prefix="delivery-e2e-") as directory:
        env = os.environ.copy()
        password = secrets.token_urlsafe(24)
        env.update(
            DATABASE_URL="sqlite:///" + str(Path(directory) / "e2e.db"),
            JWT_SECRET=secrets.token_hex(48),
            ENVIRONMENT="test",
            SECURE_COOKIES="false",
            ALLOWED_ORIGINS='["http://127.0.0.1:5173","http://localhost:5173"]',
            DEMO_PASSWORD=password,
            E2E_PASSWORD=password,
        )
        processes = []
        log_path = root / "frontend" / "test-results" / "servers.log"
        log_path.parent.mkdir(exist_ok=True)
        with log_path.open("w") as log:
            try:
                subprocess.run(
                    [sys.executable, "-m", "alembic", "upgrade", "head"],
                    cwd=root / "backend",
                    env=env,
                    check=True,
                )
                subprocess.run(
                    [sys.executable, "-m", "app.seed_demo"],
                    cwd=root / "backend",
                    env=env,
                    check=True,
                )
                api = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "uvicorn",
                        "app.main:create_app",
                        "--factory",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8000",
                    ],
                    cwd=root / "backend",
                    env=env,
                    stdout=log,
                    stderr=log,
                    start_new_session=os.name != "nt",
                )
                processes.append(api)
                wait_ready("http://127.0.0.1:8000/api/v1/health", api)
                npm = "npm.cmd" if os.name == "nt" else "npm"
                web = subprocess.Popen(
                    [
                        npm,
                        "run",
                        "dev",
                        "--",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "5173",
                        "--strictPort",
                    ],
                    cwd=root / "frontend",
                    env=env,
                    stdout=log,
                    stderr=log,
                    start_new_session=os.name != "nt",
                )
                processes.append(web)
                wait_ready("http://127.0.0.1:5173", web)
                result = subprocess.run(
                    [npm, "exec", "playwright", "test"], cwd=root / "frontend", env=env, check=False
                )
                return result.returncode
            finally:
                for process in reversed(processes):
                    if os.name != "nt":
                        try:
                            os.killpg(process.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                    else:
                        subprocess.run(
                            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                            check=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()


if __name__ == "__main__":
    sys.exit(main())
