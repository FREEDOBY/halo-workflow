#!/usr/bin/env python3
"""Functional verification for `smoke-cli-word-counter` fixture.

Runs the produced CLI against a known input and asserts observable behavior.
Exit code 0 means the workflow's output is functionally acceptable.

Usage:
    python verify.py <artifacts_dir>

The artifacts_dir is the root that contains `src/`, `tests/`, etc. — either
the archived copy under workflow-tests/runs/... or the workspace directly.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


SAMPLE_TEXT = (
    "The quick brown fox jumps over the lazy dog.\n"
    "The fox is quick. The dog is lazy.\n"
    "Hello world, hello universe, hello everyone.\n"
)
# Expected top words (case-insensitive, punctuation stripped):
#   the=4, hello=3, is=2, fox=2, dog=2, quick=2, lazy=2, ...
# Top-1 should be "the".


def find_runnable(artifacts: Path):
    """Pick an entrypoint the workflow likely produced.

    Returns (cmd_list, cwd) pair or (None, None).
    Tries, in order:
      1. `python -m <pkg>` for a package under src/ with __main__.py
      2. direct execution of src/**/__main__.py
      3. direct execution of src/**/cli.py or main.py
      4. top-level cli.py / main.py
    """
    src = artifacts / "src"

    if src.is_dir():
        for main in src.glob("*/__main__.py"):
            pkg = main.parent.name
            return ([sys.executable, "-m", pkg], str(src))

        for main in src.glob("**/__main__.py"):
            return ([sys.executable, str(main)], str(artifacts))

        for pat in ("**/cli.py", "**/main.py"):
            for p in src.glob(pat):
                return ([sys.executable, str(p)], str(artifacts))

    for name in ("cli.py", "main.py"):
        p = artifacts / name
        if p.exists():
            return ([sys.executable, str(p)], str(artifacts))

    return (None, None)


def run_cli(base_cmd, cwd, args, timeout=30):
    cmd = list(base_cmd) + list(args)
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
    )


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: verify.py <artifacts_dir>", file=sys.stderr)
        return 2
    artifacts = Path(sys.argv[1]).resolve()
    if not artifacts.is_dir():
        print(f"not a directory: {artifacts}", file=sys.stderr)
        return 2

    base_cmd, cwd = find_runnable(artifacts)
    if base_cmd is None:
        print(
            "no runnable entrypoint found "
            "(looked for python -m <pkg>, src/**/__main__.py, cli.py, main.py)",
            file=sys.stderr,
        )
        return 11
    print(f"entrypoint: {' '.join(base_cmd)}  (cwd={cwd})")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(SAMPLE_TEXT)
        sample = f.name

    try:
        # Check 1: --top 3 succeeds and "the" is listed
        r = run_cli(base_cmd, cwd, [sample, "--top", "3"])
        print("--- --top 3 ---")
        print(r.stdout)
        if r.returncode != 0:
            print(f"FAIL: --top 3 exited {r.returncode}", file=sys.stderr)
            print(r.stderr, file=sys.stderr)
            return 12
        if "the" not in r.stdout.lower():
            print("FAIL: expected 'the' in --top 3 output", file=sys.stderr)
            return 13

        # Check 2: --top 1 returns "the" (appears 4x, the most)
        r = run_cli(base_cmd, cwd, [sample, "--top", "1"])
        print("--- --top 1 ---")
        print(r.stdout)
        if r.returncode != 0:
            print(f"FAIL: --top 1 exited {r.returncode}", file=sys.stderr)
            return 14
        if "the" not in r.stdout.lower():
            print("FAIL: --top 1 should include 'the' (4 occurrences)", file=sys.stderr)
            return 15

        # Check 3: no --top arg → should still succeed (prints all)
        r = run_cli(base_cmd, cwd, [sample])
        if r.returncode != 0:
            print(f"FAIL: no --top exited {r.returncode}", file=sys.stderr)
            print(r.stderr, file=sys.stderr)
            return 16
        # should contain multiple words
        if "the" not in r.stdout.lower() or "hello" not in r.stdout.lower():
            print("FAIL: full listing missing expected words", file=sys.stderr)
            return 17

        print("functional: OK")
        return 0
    finally:
        try:
            Path(sample).unlink()
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
