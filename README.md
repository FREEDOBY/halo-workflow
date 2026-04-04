# HALO Workflow v3

**H**arness · **A**gentic · **L**oopback · **O**rchestration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI agent orchestration framework that runs a full TDD development cycle — from requirements analysis to code review — with **RTM (Requirements Traceability Matrix)**-driven traceability and intelligent **loopback** recovery.

Built for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). The **main agent** directly executes all 8 sequential phases (P1~P7, P9) with zero context breaks. Sub-agents are used only for **P8 code review** and **JUDGE RTM evaluation**.

> **[Interactive Architecture Diagram](https://FREEDOBY.github.io/halo-workflow/)**

## Quick Start

1. Copy `.claude/` folder to your project
2. Run `/halo-workflow [feature description]`

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│  MAIN AGENT  (Executor + Router)                                   │
│                                                                    │
│  P1 ──→ P2 ──→ P3 ──→ P4 ──→ P5 ──→ P6 ──→ P7 ──→ P8 ──→ P9  │
│  직접   직접   직접   직접   직접   직접   직접    ↕     직접    │
│  ──────── Main continuous (zero context breaks) ─  │              │
│                                                  Review  JUDGE    │
│                                                  ┌─┴─┐  ┌───┐    │
│                                                  │ ×3 │  │ ×1│    │
│                                                  └───┘  └─┬─┘    │
│              JUDGE reads RTM only → classifies:          │       │
│              ┌──── Test Bug → P4 ────────────────────────┘       │
│              ├──── Impl Bug → P5                                  │
│              ├──── Test Design → P6                                │
│              └──── Arch Issue → P3                                 │
├────────────────────────────────────────────────────────────────────┤
│  .workflow/    Checkpoint + State (temporary, gitignored)          │
├────────────────────────────────────────────────────────────────────┤
│  docs/ tests/ src/ reports/    Product Artifacts (permanent)       │
└────────────────────────────────────────────────────────────────────┘
```

## RTM = Single Source of Truth

Every phase updates the RTM. JUDGE reads only the RTM to evaluate.

```
  P1           P4           P5            P6            P7       P8       JUDGE
  ●────────────●────────────●─────────────●─────────────●────────●────────▶ ◆
  │            │            │             │             │        │          │
  init RTM     +Unit TC     +impl loc     +IT/E2E TC   +result  +review   RTM only
  REQ-IDs      mapping      file:line     mapping      PASS/    issues    → evaluate
                                                        FAIL    reflect   → loopback
```

## Core Principles

| Principle | Description |
|-----------|-------------|
| **RTM = Single Source of Truth** | Every phase updates RTM. JUDGE reads RTM only. |
| **Main Agent First** | P1~P7 main direct. Sub-agents for P8 (review) and JUDGE only. |
| **Constraint Verification** | External API/deployment assumptions verified by actual calls (P1). |
| **Real E2E** | E2E tests run in real environment. No mocks. |
| **File = Interface** | Inter-agent communication and context recovery via file system only. |
| **LOOPBACK ≠ Requirement Change** | Requirements immutable; 4 regression paths (P3/P4/P5/P6). |

## Phases

### Main Agent Direct (8 Phases)

| Phase | Role | RTM Update |
|-------|------|------------|
| P1 | Requirements + Constraint Verification | Init RTM (REQ-IDs) |
| P2 | Codebase Exploration (Greenfield: auto-skip) | - |
| P3 | Architecture Design | - |
| P4 | Unit Test (TDD RED) | + Unit TC mapping |
| P5 | Implementation (TDD GREEN) | + Impl location (file:line) |
| P6 | Integration & E2E Test (real env) | + IT/E2E TC mapping |
| P7 | Test Execution + Smoke | + Result (PASS/FAIL) |
| P9 | Completion Report | Status → Complete |

### Sub-Agents (2 Points)

| Phase | Role | Agents | Purpose |
|-------|------|--------|---------|
| P8 | Code Review | ×3 parallel | Quality / Bugs / Security → issues to RTM |
| JUDGE | RTM Evaluation | ×1 | Read RTM only → classify root cause → LOOPBACK |

### LOOPBACK Policy

| Root Cause | Regression Target |
|-----------|-------------------|
| Test Bug (assertion error, wrong expectation) | **→ P4** |
| Impl Bug (logic error, unhandled exception) | **→ P5** |
| Test Design (E2E scenario, env issue, mock usage) | **→ P6** |
| Arch Issue (interface mismatch, design flaw) | **→ P3** |

> **Limits**: Max 5 total, max 2 per phase. Same phase twice → escalate (P5→P3). Exceeded → Partial Report → P9.

> **Re-execution**: From regression phase to end (e.g., P5 → P5→P6→P7→P8→JUDGE).

## Test Levels

```
Level 0: UNIT TEST        — Mocks allowed, isolated (P4/P5 TDD)
Level 1: INTEGRATION TEST — Minimal mocks, module interaction (P6/P7)
Level 2: E2E TEST         — NO mocks, real server/browser/API (P6/P7)
Level 3: SMOKE TEST       — Server up + core feature verified (P7)
```

## License

MIT
