#!/usr/bin/env python3
"""HALO workflow fixture evaluator.

Reads .workflow/, RTM, P8 review docs, and artifact paths from the current
workspace, aggregates metrics, and compares them against a fixture's
oracle.json. Writes an archived metrics.json under workflow-tests/runs/.

Usage:
    python workflow-tests/scripts/evaluate.py <fixture>
    python workflow-tests/scripts/evaluate.py <fixture> --workspace /path/to/project
    python workflow-tests/scripts/evaluate.py <fixture> --save-baseline
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Directories that the workflow generates in the project root.
# These are moved into the run archive after evaluation so the root is
# left clean for the next fixture run. Only moved for greenfield fixtures.
WORKFLOW_ARTIFACT_DIRS = ("docs", "src", "tests", "reports", ".workflow")


def load_state(workspace):
    p = workspace / ".workflow" / "state.json"
    if not p.exists():
        return {"_missing": True}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"_parse_error": str(e)}


def find_rtm(workspace):
    req_dir = workspace / "docs" / "requirements"
    if not req_dir.exists():
        return None
    matches = sorted(req_dir.glob("*-rtm.md"))
    return matches[0] if matches else None


def parse_rtm(rtm_path):
    """Parse the Traceability Matrix table out of an RTM markdown file.

    Returns a list of dict rows keyed by column header.
    """
    text = rtm_path.read_text(encoding="utf-8")
    rows = []
    headers = None
    in_table = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and "REQ-ID" in s and "Requirement" in s:
            headers = [c.strip() for c in s.strip("|").split("|")]
            in_table = True
            continue
        if not in_table:
            continue
        if not s.startswith("|"):
            in_table = False
            continue
        inner = s.strip("|").replace("|", "").strip()
        if inner and set(inner) <= set("-: "):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if headers and len(cells) == len(headers):
            row = dict(zip(headers, cells))
            if row.get("REQ-ID", "").startswith("REQ-"):
                rows.append(row)
    return rows


def _mapped(cell):
    v = (cell or "").strip()
    return v not in ("", "-")


def analyze_rtm(rows):
    total = len(rows)
    any_tc = sum(
        1
        for r in rows
        if _mapped(r.get("Unit TC"))
        or _mapped(r.get("Integration TC"))
        or _mapped(r.get("E2E TC"))
    )
    return {
        "total_reqs": total,
        "result_pass": sum(1 for r in rows if r.get("Result", "").upper() == "PASS"),
        "unit_tc_mapped": sum(1 for r in rows if _mapped(r.get("Unit TC"))),
        "any_tc_mapped": any_tc,
        "impl_location_mapped": sum(1 for r in rows if _mapped(r.get("Impl Location"))),
        "integration_tc_mapped": sum(1 for r in rows if _mapped(r.get("Integration TC"))),
        "e2e_tc_mapped": sum(1 for r in rows if _mapped(r.get("E2E TC"))),
        "review_ok": sum(
            1 for r in rows if r.get("Review", "").upper() in ("PASS", "MINOR", "-", "")
        ),
    }


def parse_last_review(workspace):
    reviews_dir = workspace / ".workflow" / "reviews"
    if not reviews_dir.exists():
        return {"exists": False}
    files = list(reviews_dir.glob("P8-cycle-*.md"))
    if not files:
        return {"exists": False}

    def cycle_num(p):
        m = re.search(r"cycle-(\d+)", p.name)
        return int(m.group(1)) if m else -1

    files.sort(key=cycle_num)
    last = files[-1]
    text = last.read_text(encoding="utf-8")
    info = {
        "exists": True,
        "file": str(last.relative_to(workspace)).replace("\\", "/"),
        "cycle": cycle_num(last),
    }

    # Parse severity counts out of the ## Summary section. Tolerates:
    #   "CRITICAL: 0 | MAJOR: 0 | MINOR: 5"  (pipe-separated, one line)
    #   "CRITICAL: 0, MAJOR: 0, MINOR: 5"    (comma-separated)
    #   "- **CRITICAL: 0**"                   (bullet, markdown bold, multi-line)
    summary_match = re.search(r"##\s*Summary\b(.+?)(?=\n##\s|\Z)", text, re.DOTALL)
    scope = summary_match.group(1) if summary_match else text
    parsed = True
    for label in ("CRITICAL", "MAJOR", "MINOR"):
        m = re.search(
            rf"\b{label}\b\**\s*[:=]\s*\**\s*(\d+)",
            scope,
            re.IGNORECASE,
        )
        if m:
            info[label] = int(m.group(1))
        else:
            parsed = False
    if not parsed:
        info["_parse_error"] = True
    return info


def check_artifacts(patterns, workspace):
    out = {}
    for pat in patterns:
        full = str(workspace / pat)
        matches = glob.glob(full, recursive=True)
        out[pat] = len(matches)
    return out


def move_artifacts(workspace, dest_dir):
    """Move workflow-generated content from workspace into dest_dir.

    Preserves scaffolding: the top-level directories (docs/, src/, etc.)
    and any .gitkeep files stay in the workspace — only their workflow-
    generated children are moved. Returns the list of top-level names
    from which something was actually moved.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    moved = []
    for name in WORKFLOW_ARTIFACT_DIRS:
        src = workspace / name
        if not src.exists() or not src.is_dir():
            continue
        children = [c for c in src.iterdir() if c.name != ".gitkeep"]
        if not children:
            continue
        target = dest_dir / name
        target.mkdir(parents=True, exist_ok=True)
        for child in children:
            shutil.move(str(child), str(target / child.name))
        moved.append(name)
    return moved


def run_verify(script, artifacts_path, run_dir, repo_root):
    """Execute the fixture's verify.py against the artifact directory.

    Returns dict describing what happened (ran/ok/exit_code/stdout/stderr).
    If run_dir is provided, stdout+stderr are also written to verify.log.
    """
    try:
        proc = subprocess.run(
            [sys.executable, str(script), str(artifacts_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as e:
        result = {
            "ran": True,
            "ok": False,
            "timeout": True,
            "exit_code": None,
            "stdout": e.stdout or "",
            "stderr": e.stderr or "",
        }
    except Exception as e:
        return {"ran": False, "ok": False, "error": str(e)}
    else:
        result = {
            "ran": True,
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    if run_dir is not None:
        log = run_dir / "verify.log"
        log.write_text(
            f"$ {sys.executable} {script} {artifacts_path}\n\n"
            f"=== STDOUT (exit={result.get('exit_code')}) ===\n"
            f"{result.get('stdout', '')}"
            f"\n=== STDERR ===\n{result.get('stderr', '')}",
            encoding="utf-8",
        )
        try:
            result["log_file"] = str(log.relative_to(repo_root)).replace("\\", "/")
        except ValueError:
            result["log_file"] = str(log)
    return result


def compare_with_oracle(metrics, oracle):
    checks = []
    exp = oracle.get("expected", {})
    state = metrics.get("state", {}) or {}
    rtm = metrics.get("rtm", {}) or {}
    rev = metrics.get("review", {}) or {}
    arts = metrics.get("artifacts", {}) or {}

    if "loopback_count_max" in exp:
        if state.get("_missing") or state.get("_parse_error"):
            checks.append(("loopback_count", False, "state.json unavailable"))
        else:
            v = state.get("loopback_count", 0)
            limit = exp["loopback_count_max"]
            checks.append(
                (f"loopback_count <= {limit}", v <= limit, f"actual={v}")
            )

    if "total_reqs_min" in exp:
        v = rtm.get("total_reqs", 0)
        lim = exp["total_reqs_min"]
        checks.append((f"total_reqs >= {lim}", v >= lim, f"actual={v}"))

    def _all_mapped(flag_key, stat_key):
        if not exp.get(flag_key):
            return
        total = rtm.get("total_reqs", 0)
        cnt = rtm.get(stat_key, 0)
        ok = total > 0 and cnt == total
        checks.append((flag_key, ok, f"{cnt}/{total}"))

    _all_mapped("all_reqs_result_pass", "result_pass")
    _all_mapped("all_reqs_have_unit_tc", "unit_tc_mapped")
    _all_mapped("all_reqs_have_any_tc", "any_tc_mapped")
    _all_mapped("all_reqs_have_impl_location", "impl_location_mapped")
    _all_mapped("all_reqs_have_integration_tc", "integration_tc_mapped")
    _all_mapped("all_reqs_have_e2e_tc", "e2e_tc_mapped")

    if "review_critical_max" in exp:
        v = rev.get("CRITICAL", 0) if rev.get("exists") else 0
        lim = exp["review_critical_max"]
        checks.append((f"review_critical <= {lim}", v <= lim, f"actual={v}"))
    if "review_major_max" in exp:
        v = rev.get("MAJOR", 0) if rev.get("exists") else 0
        lim = exp["review_major_max"]
        checks.append((f"review_major <= {lim}", v <= lim, f"actual={v}"))

    if exp.get("functional_ok"):
        func = metrics.get("functional", {}) or {}
        if not func.get("ran"):
            reason = func.get("reason") or func.get("error") or "verify.py not run"
            checks.append(("functional_ok", False, reason))
        elif func.get("timeout"):
            checks.append(("functional_ok", False, "timeout (>120s)"))
        else:
            ok = bool(func.get("ok"))
            checks.append(
                ("functional_ok", ok, f"exit={func.get('exit_code')}")
            )

    for pat in exp.get("artifacts_must_exist", []):
        v = arts.get(pat, 0)
        checks.append((f"artifact exists: {pat}", v > 0, f"matches={v}"))

    return checks


def format_report(fixture, metrics, checks):
    out = [f"=== Fixture: {fixture} ===", ""]

    state = metrics.get("state", {}) or {}
    if state.get("_missing"):
        out.append("State: .workflow/state.json NOT FOUND")
    elif state.get("_parse_error"):
        out.append(f"State: parse error — {state['_parse_error']}")
    else:
        out.append("State:")
        out.append(f"  loopback_count:      {state.get('loopback_count', '?')}")
        out.append(f"  loopback_per_phase:  {state.get('loopback_per_phase', {})}")
        out.append(f"  completed_phases:    {state.get('completed_phases', [])}")
    out.append("")

    rtm = metrics.get("rtm") or {}
    if not rtm:
        out.append("RTM: not found")
    else:
        total = rtm.get("total_reqs", 0)
        out.append(f"RTM: {rtm.get('rtm_path', '?')}")
        out.append(f"  total_reqs:             {total}")
        out.append(f"  result_pass:            {rtm.get('result_pass', 0)}/{total}")
        out.append(f"  unit_tc_mapped:         {rtm.get('unit_tc_mapped', 0)}/{total}")
        out.append(f"  integration_tc_mapped:  {rtm.get('integration_tc_mapped', 0)}/{total}")
        out.append(f"  e2e_tc_mapped:          {rtm.get('e2e_tc_mapped', 0)}/{total}")
        out.append(f"  impl_location_mapped:   {rtm.get('impl_location_mapped', 0)}/{total}")
    out.append("")

    rev = metrics.get("review") or {}
    out.append("P8 Review (last cycle):")
    if not rev.get("exists"):
        out.append("  (no review docs found)")
    elif rev.get("_parse_error"):
        out.append(f"  file: {rev.get('file')} — summary parse error")
    else:
        out.append(f"  file:     {rev.get('file')}")
        out.append(f"  cycle:    {rev.get('cycle')}")
        out.append(f"  CRITICAL: {rev.get('CRITICAL', 0)}")
        out.append(f"  MAJOR:    {rev.get('MAJOR', 0)}")
        out.append(f"  MINOR:    {rev.get('MINOR', 0)}")
    out.append("")

    arts = metrics.get("artifacts") or {}
    if arts:
        out.append("Artifacts:")
        for pat, n in arts.items():
            out.append(f"  {pat}: {n} match(es)")
        out.append("")

    func = metrics.get("functional") or {}
    out.append("Functional Verify:")
    if not func.get("ran"):
        reason = func.get("reason") or func.get("error") or "n/a"
        out.append(f"  (not run — {reason})")
    elif func.get("timeout"):
        out.append("  TIMEOUT (>120s)")
    else:
        mark = "OK" if func.get("ok") else "FAIL"
        out.append(f"  {mark} (exit={func.get('exit_code')})")
        if func.get("log_file"):
            out.append(f"  log: {func['log_file']}")
    out.append("")

    out.append("Oracle Checks:")
    passed = 0
    for name, ok, detail in checks:
        mark = "PASS" if ok else "FAIL"
        out.append(f"  [{mark}] {name}  ({detail})")
        if ok:
            passed += 1
    out.append("")
    out.append(f"Result: {passed}/{len(checks)} checks PASS")

    moved = metrics.get("archived_artifacts")
    if moved:
        out.append("")
        out.append(
            f"Archived artifacts → {metrics.get('archived_artifacts_dir', '?')}  "
            f"(moved: {', '.join(moved)})"
        )
    elif "archived_artifacts_skipped_reason" in metrics:
        out.append("")
        out.append(
            f"Artifact move skipped ({metrics['archived_artifacts_skipped_reason']})"
        )
    return "\n".join(out)


def main():
    # Windows consoles default to cp949 on Korean locales, which can't
    # encode characters like em-dash that appear in reports.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", help="fixture name (subdir of workflow-tests/fixtures)")
    parser.add_argument("--workspace", default=".", help="project root to inspect (default: cwd)")
    parser.add_argument("--save-baseline", action="store_true")
    parser.add_argument("--no-archive", action="store_true",
                        help="skip runs/ archive entirely — no metrics.json, no artifact move")
    parser.add_argument("--keep-artifacts", action="store_true",
                        help="write metrics.json but leave artifacts in the workspace "
                             "(useful for iterative debugging)")
    args = parser.parse_args()

    tests_root = Path(__file__).resolve().parent.parent
    fixture_dir = tests_root / "fixtures" / args.fixture
    oracle_path = fixture_dir / "oracle.json"
    if not oracle_path.exists():
        print(f"oracle.json not found: {oracle_path}", file=sys.stderr)
        return 2
    oracle = json.loads(oracle_path.read_text(encoding="utf-8"))

    workspace = Path(args.workspace).resolve()

    state = load_state(workspace)

    rtm_path = find_rtm(workspace)
    if rtm_path:
        rtm_stats = analyze_rtm(parse_rtm(rtm_path))
        rtm_stats["rtm_path"] = str(rtm_path.relative_to(workspace)).replace("\\", "/")
    else:
        rtm_stats = {}

    review = parse_last_review(workspace)
    arts = check_artifacts(
        oracle.get("expected", {}).get("artifacts_must_exist", []), workspace
    )

    metrics = {
        "fixture": args.fixture,
        "evaluated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "state": state,
        "rtm": rtm_stats,
        "review": review,
        "artifacts": arts,
    }

    # ---- Archive (move artifacts for greenfield fixtures) --------------
    run_dir = None
    artifacts_path = workspace
    if not args.no_archive:
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_dir = tests_root / "runs" / args.fixture / ts
        run_dir.mkdir(parents=True, exist_ok=True)

        if args.keep_artifacts:
            metrics["archived_artifacts"] = []
            metrics["archived_artifacts_skipped_reason"] = "--keep-artifacts"
        elif oracle.get("greenfield") is True:
            moved = move_artifacts(workspace, run_dir / "artifacts")
            metrics["archived_artifacts"] = moved
            metrics["archived_artifacts_dir"] = str(
                (run_dir / "artifacts").relative_to(tests_root.parent)
            ).replace("\\", "/")
            artifacts_path = run_dir / "artifacts"
        else:
            metrics["archived_artifacts"] = []
            metrics["archived_artifacts_skipped_reason"] = (
                "fixture is not greenfield; artifact move not yet supported"
            )

    # ---- Functional verify (run verify.py against artifacts) ------------
    verify_script = fixture_dir / "verify.py"
    if verify_script.exists():
        metrics["functional"] = run_verify(
            verify_script, artifacts_path, run_dir, tests_root.parent
        )
    else:
        metrics["functional"] = {"ran": False, "reason": "no verify.py in fixture"}

    # ---- Compare with oracle (now includes functional_ok) ---------------
    checks = compare_with_oracle(metrics, oracle)
    metrics["oracle_checks"] = [
        {"name": n, "pass": ok, "detail": d} for n, ok, d in checks
    ]
    all_pass = all(ok for _, ok, _ in checks) if checks else False
    metrics["oracle_result"] = {
        "passed": sum(1 for _, ok, _ in checks if ok),
        "total": len(checks),
        "all_pass": all_pass,
    }

    # ---- Write final metrics.json + latest.json -------------------------
    if run_dir is not None:
        (run_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        latest = tests_root / "runs" / args.fixture / "latest.json"
        latest.parent.mkdir(parents=True, exist_ok=True)
        latest.write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # ---- Baseline -------------------------------------------------------
    if args.save_baseline:
        baseline_dir = tests_root / "baselines"
        baseline_dir.mkdir(parents=True, exist_ok=True)
        out = baseline_dir / f"{args.fixture}.json"
        out.write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Saved baseline: {out.relative_to(tests_root.parent)}")

    print(format_report(args.fixture, metrics, checks))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
