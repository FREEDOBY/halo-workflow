# HALO Workflow v2

> [한국어 문서](i18n/ko/README.md)

**H**arness · **A**gentic · **L**oopback · **O**rchestration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI agent orchestration framework that runs a full TDD development cycle — from requirements analysis to code review — with **RTM (Requirements Traceability Matrix)**-driven traceability and intelligent **loopback** recovery.

Built for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). The **main agent** directly executes 6 sequential phases while spawning **sub-agents only for parallel work** (scouting, competing designs, multi-perspective review).

> **[Interactive Architecture Diagram](https://FREEDOBY.github.io/halo-workflow/)**

## Quick Start

1. Copy `.claude/` folder to your project
2. Run `/halo-workflow [feature description]`

## Architecture

### Hybrid Execution Model

```
┌───────────────────────────────────────────────────────────────────┐
│  MAIN AGENT  (Executor + Router + RTM Judge)                      │
│                                                                    │
│  P1 ──→ P2 ──→ P3 ──→ P4 ──→ P5 ──→ P6 ──→ P7 ──→ P8 ──→ P9  │
│  직접    ↕      ↕     직접   직접   직접   직접    ↕     직접    │
│        정찰    경쟁                              리뷰           │
│       ┌─┴─┐  ┌─┴─┐                             ┌─┴─┐            │
│       │×2∼3│ │×2∼3│                             │ ×3 │            │
│       └─┬─┘  └─┬─┘                             └───┘            │
│     메인 Read  메인 Read+확정                                     │
│                                                                    │
│               JUDGE (P7/P8 이후)                                   │
│              ┌──── Impl Bug → P5                                  │
│              ├──── Test Design → P6                                │
│              └──── Arch Issue → P3                                 │
├────────────────────────────────────────────────────────────────────┤
│  .workflow/    Checkpoint + State (temporary, gitignored)          │
├────────────────────────────────────────────────────────────────────┤
│  docs/ tests/ src/ reports/    Product Artifacts (permanent)       │
└────────────────────────────────────────────────────────────────────┘
```

### Workflow Process

```
  /halo-workflow "feature description"
                    │
                    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │   P1  Requirements      [Main] Analyze + Constraint Verification   │
  │       Analysis           → docs/requirements/[feature].md, RTM     │
  │         │                                                           │
  │         ▼                                                           │
  │   P2  Codebase           [Sub-agents scout → Main reads directly]  │
  │       Exploration        Scouts report key files → Main reads them │
  │         │                                                           │
  │         ▼                                                           │
  │   P3  Architecture       [Sub-agents compete → Main finalizes] ◀─┐ │
  │       Design             3 proposals → Main reviews + confirms    │ │
  │         │                → docs/architecture/[feature].md         │ │
  │         ▼                                                         │ │
  │   P4  Unit Test          [Main] TDD RED                           │ │
  │       (TDD RED)          → tests/unit/*, RTM update               │ │
  │         │                                                         │ │
  │         ▼                                                         │ │
  │   P5  Implementation     [Main] TDD GREEN                    ◀─┐│ │
  │       (TDD GREEN)        → src/[feature]/*, RTM update          ││ │
  │         │                                                       ││ │
  │         ▼                                                       ││ │
  │   P6  Integration &      [Main] Real E2E required           ◀─┐││ │
  │       E2E Test           → tests/integration/*, tests/e2e/*   │││ │
  │         │                                                     │││ │
  │         ▼                                                     │││ │
  │   P7  Test Execution     [Main] Unit→IT→E2E→Smoke Test      │││ │
  │       + Smoke Test       → RTM results                        │││ │
  │         │                                                     │││ │
  │         ▼                                                     │││ │
  │   P8  Code Review        [Sub-agents ×3] Quality/Bugs/Security│││ │
  │                          → Issues → Main judges               │││ │
  │         │                                                     │││ │
  │         ▼                                                     │││ │
  │   ┌──────────┐   FAIL   RTM reverse trace → root cause:     │││ │
  │   │  JUDGE   │────────→  Impl Bug ──────────────────────────┘││ │
  │   │  (Main)  │────────→  Test Design ────────────────────────┘│ │
  │   │          │────────→  Arch Issue ──────────────────────────┘ │
  │   └────┬─────┘                                                  │
  │        │ PASS                                                   │
  │        ▼                                                        │
  │   P9  Completion         [Main] Final report                    │
  │       Report             → reports/[feature]-completion.md     │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

### RTM Timeline (Single Source of Truth)

```
  P1           P4           P5            P6            P7          JUDGE
  ●────────────●────────────●─────────────●─────────────●──────────▶ ◆
  │            │            │             │             │             │
  init RTM     map Unit     map impl      map IT/E2E   record       evaluate
  REQ-IDs      TC-IDs       file:line     TC-IDs       PASS/FAIL    root cause
```

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Main Agent First** | Sequential phases executed directly. Sub-agents for parallel only. |
| **Constraint Verification** | External API/deployment assumptions verified by actual calls (P1). |
| **Real E2E** | E2E tests run in real environment. No mocks. No "E2E-style" unit tests. |
| **RTM = Single Source of Truth** | RTM cumulatively updated at P1/P4/P5/P6/P7; Judge evaluates from RTM. |
| **File = Interface** | Inter-agent communication and context recovery via file system only. |
| **LOOPBACK ≠ Requirement Change** | Requirements are immutable; 3 regression paths (P3/P5/P6). |

## Phases

### Main Agent Direct (6 Phases)

| Phase | Role | Output |
|-------|------|--------|
| P1 | Requirements Analysis + Constraint Verification | `docs/requirements/` |
| P4 | Unit Test (TDD RED) | `tests/unit/` |
| P5 | Implementation (TDD GREEN) | `src/[feature]/` |
| P6 | Integration & E2E Test (real environment) | `tests/integration/`, `tests/e2e/` |
| P7 | Test Execution + Smoke Test | RTM results |
| P9 | Completion Report | `reports/` |

### Sub-Agent Parallel (3 Phases)

| Phase | Role | Agents | Sub-Agent Job | Main Agent Job |
|-------|------|--------|---------------|----------------|
| P2 | Codebase Exploration | ×2∼3 | **Scout**: Report key file lists | Read reported files directly |
| P3 | Architecture Design | ×2∼3 | **Compete**: Write proposals + ref files | Read proposals + ref code, finalize |
| P8 | Code Review | ×3 | **Review**: Report issues by perspective | Synthesize judgment |

### LOOPBACK Policy

| Trigger | Root Cause | Regression Target |
|---------|-----------|-------------------|
| P7: Unit/Integration FAIL | Impl Bug | **→ P5** |
| P7: E2E FAIL | Test Design | **→ P6** |
| P7: Integration FAIL (coupling) | Arch Issue | **→ P3** |
| P7: E2E uses mocks | E2E not met | **→ P6** |
| P8: MAJOR | Impl fix needed | **→ P5** |
| P8: CRITICAL | Arch redesign | **→ P3** |

> **Limits**: Max 5 total LOOPBACKs, max 2 per phase. Exceeded → Partial Report → P9.

## Test Levels

```
Level 0: UNIT TEST        — Mocks allowed, isolated module testing (P4/P5 TDD)
Level 1: INTEGRATION TEST — Minimal mocks, module interaction testing (P6/P7)
Level 2: E2E TEST         — NO mocks, real server/browser/API (P6/P7)
Level 3: SMOKE TEST       — Server up + core feature verified once (P7)
```

## License

MIT
