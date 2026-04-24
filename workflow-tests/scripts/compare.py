#!/usr/bin/env python3
"""Diff baseline metrics vs. the latest recorded run for a fixture.

Usage:
    python workflow-tests/scripts/compare.py <fixture>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def _line(name, base, curr):
    if base == curr:
        return None
    return f"  {name:32s}  baseline={base!r}  ->  current={curr!r}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture")
    args = parser.parse_args()

    tests_root = Path(__file__).resolve().parent.parent
    base_p = tests_root / "baselines" / f"{args.fixture}.json"
    curr_p = tests_root / "runs" / args.fixture / "latest.json"

    if not base_p.exists():
        print(f"no baseline: {base_p}", file=sys.stderr)
        return 2
    if not curr_p.exists():
        print(f"no current run: {curr_p} (run evaluate.py first)", file=sys.stderr)
        return 2

    base = _load(base_p)
    curr = _load(curr_p)

    print(f"=== Compare: {args.fixture} ===")
    print(f"Baseline evaluated_at: {base.get('evaluated_at')}")
    print(f"Current  evaluated_at: {curr.get('evaluated_at')}")
    print()

    diffs = []

    bs = base.get("state") or {}
    cs = curr.get("state") or {}
    for k in ("loopback_count", "completed_phases", "loopback_per_phase"):
        d = _line(f"state.{k}", bs.get(k), cs.get(k))
        if d:
            diffs.append(d)

    br = base.get("rtm") or {}
    cr = curr.get("rtm") or {}
    for k in (
        "total_reqs",
        "result_pass",
        "unit_tc_mapped",
        "integration_tc_mapped",
        "e2e_tc_mapped",
        "impl_location_mapped",
    ):
        d = _line(f"rtm.{k}", br.get(k), cr.get(k))
        if d:
            diffs.append(d)

    brv = base.get("review") or {}
    crv = curr.get("review") or {}
    for k in ("CRITICAL", "MAJOR", "MINOR"):
        d = _line(f"review.{k}", brv.get(k, 0), crv.get(k, 0))
        if d:
            diffs.append(d)

    bor = base.get("oracle_result") or {}
    cor = curr.get("oracle_result") or {}
    d = _line(
        "oracle.passed",
        f"{bor.get('passed')}/{bor.get('total')}",
        f"{cor.get('passed')}/{cor.get('total')}",
    )
    if d:
        diffs.append(d)

    if not diffs:
        print("No metric differences between baseline and current run.")
    else:
        print("Differences:")
        for d in diffs:
            print(d)

    return 0


if __name__ == "__main__":
    sys.exit(main())
