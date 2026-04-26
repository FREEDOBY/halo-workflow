"""Verify brownfield-cli-config-loader fixture.

Test 1 — baseline behavior preserved: CLI prints config values without
env override.
Test 2 — new feature: CONFIG_OVERRIDE_<KEY> overrides file value.

Both run against the workflow-produced src/, which should now contain
the env override implementation while keeping load_config() backwards
compatible.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: verify.py <artifacts_dir>", file=sys.stderr)
        return 2
    artifacts = Path(sys.argv[1]).resolve()
    src = artifacts / "src"
    if not src.exists():
        print(f"src not found in {artifacts}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as td:
        cfg = Path(td) / "test.json"
        cfg.write_text('{"port": 8080, "host": "localhost"}', encoding="utf-8")

        env_clean = {
            k: v for k, v in os.environ.items()
            if not k.startswith("CONFIG_OVERRIDE_")
        }
        env_clean["PYTHONPATH"] = str(src)

        # Test 1: baseline behavior — no override env vars
        r1 = subprocess.run(
            [sys.executable, "-m", "configloader", str(cfg)],
            capture_output=True, text=True, env=env_clean, timeout=10,
        )
        if r1.returncode != 0:
            print(f"Test 1 (no override) exit={r1.returncode}", file=sys.stderr)
            print("STDERR:", r1.stderr, file=sys.stderr)
            return 1
        if "8080" not in r1.stdout:
            print(f"Test 1: expected 8080 in stdout, got: {r1.stdout!r}", file=sys.stderr)
            return 1
        print("Test 1 OK: baseline load works (port=8080)")

        # Test 2: env override — CONFIG_OVERRIDE_PORT=9090 must take precedence
        env_with = dict(env_clean)
        env_with["CONFIG_OVERRIDE_PORT"] = "9090"
        r2 = subprocess.run(
            [sys.executable, "-m", "configloader", str(cfg)],
            capture_output=True, text=True, env=env_with, timeout=10,
        )
        if r2.returncode != 0:
            print(f"Test 2 (with override) exit={r2.returncode}", file=sys.stderr)
            print("STDERR:", r2.stderr, file=sys.stderr)
            return 1
        if "9090" not in r2.stdout:
            print(f"Test 2: expected 9090 in stdout (overridden), got: {r2.stdout!r}", file=sys.stderr)
            return 1
        print("Test 2 OK: env override works (port=9090)")

        return 0


if __name__ == "__main__":
    sys.exit(main())
