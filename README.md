# HALO Workflow

> [한국어 문서](i18n/ko/README.md)

**H**arness · **A**gentic · **L**oopback · **O**rchestration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A 3-layer **AI agent orchestration** framework that runs a full TDD development cycle — from requirements analysis to code review — with **RTM (Requirements Traceability Matrix)**-driven traceability and intelligent **loopback** recovery.

Built for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). The **harness** orchestrates 9 phase-isolated **agentic** sub-agents, automatically regressing to the right phase when tests fail or reviews surface issues.

> **[Interactive Architecture Diagram](https://FREEDOBY.github.io/halo-workflow/)**

## Quick Start

1. Copy `.claude/` folder to your project
2. Run `/halo-workflow [feature description]`

## Architecture

### 3-Layer Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: HARNESS  (Orchestrator + State Machine + RTM Judge)              │
│                                                                             │
│    ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐       │
│    │ P1 │─→│ P2 │─→│ P3 │─→│ P4 │─→│ P5 │─→│ P6 │─→│ P7 │─→│ P8 │       │
│    └────┘  └────┘  └────┘  └────┘  └────┘  └────┘  └────┘  └────┘       │
│                                                         │                   │
│                                                    ┌────▼────┐  ┌────┐     │
│                                                    │  JUDGE  │─→│ P9 │     │
│                                                    └────┬────┘  └────┘     │
│                          LOOPBACK ◀─────────────────────┘                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 2: AI AGENTS  (Phase-Isolated, Tool-Restricted Sub-Agents)          │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 3: ARTIFACTS  (File System = Agent Interface)                       │
│    docs/  │  tests/  │  src/  │  .workflow/  │  reports/                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Workflow Process

```
  /halo-workflow "Add user authentication"
                    │
                    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │   P1  Requirements      Analyze feature → Generate RTM             │
  │       Analyst            docs/requirements/[feature]-rtm.md        │
  │         │                                                           │
  │         ▼                                                           │
  │   P2  Code Explorer     Explore codebase patterns (x3 parallel)    │
  │       x3 agents                                                     │
  │         │                                                           │
  │         ▼                                                           │
  │   P3  Code Architect    Design architecture (x3 parallel)      ◀─┐ │
  │       x3 agents          docs/architecture/[feature].md          │ │
  │         │                                                        │ │
  │         ▼                                                        │ │
  │   P4  Test Engineer     Write unit tests (TDD RED)               │ │
  │       (Unit)             tests/unit/[feature].*                   │ │
  │         │                                                        │ │
  │         ▼                                                        │ │
  │   P5  Implementer       Implement code (TDD GREEN)           ◀─┐│ │
  │                          src/[feature]/*                        ││ │
  │         │                                                      ││ │
  │         ▼                                                      ││ │
  │   P6  Test Engineer     Write integration & E2E tests      ◀─┐││ │
  │       (IT/E2E)           tests/integration/, tests/e2e/      │││ │
  │         │                                                    │││ │
  │         ▼                                                    │││ │
  │   P7  Test Runner       Execute all tests → Update RTM      │││ │
  │                                                              │││ │
  │         │                                                    │││ │
  │         ▼                                                    │││ │
  │   P8  Code Reviewer     Review code quality (x3 parallel)   │││ │
  │       x3 agents                                              │││ │
  │         │                                                    │││ │
  │         ▼                                                    │││ │
  │   ┌──────────┐   FAIL   RTM-based root cause analysis:      │││ │
  │   │  JUDGE   │────────→  Test Design Issue ─────────────────┘││ │
  │   │ (RTM)    │────────→  Implementation Bug ─────────────────┘│ │
  │   │          │────────→  Architecture Issue ──────────────────┘ │
  │   └────┬─────┘                                                  │
  │        │ PASS                                                   │
  │        ▼                                                        │
  │   P9  Report Writer     Generate completion report              │
  │                          reports/[feature]-completion.md        │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

### RTM Timeline (Single Source of Truth)

```
  P1           P4           P5            P6            P7          JUDGE
  ●────────────●────────────●─────────────●─────────────●──────────▶ ◆
  │            │            │             │             │             │
  init RTM     map Unit     map impl      map IT/E2E   record       evaluate
  REQ-IDs      test cases   locations     test cases   results      pass/fail
```

### LOOPBACK Policy

| Trigger | Root Cause | Regression Target |
|---------|-----------|-------------------|
| P7: Unit/Integration FAIL | Implementation bug | **→ P5** (Implementer) |
| P7: E2E FAIL | Test design issue | **→ P6** (Test Engineer) |
| P7: Integration FAIL (coupling) | Architecture issue | **→ P3** (Architect) |
| P8: Code quality issue | Implementation fix needed | **→ P5** (Implementer) |
| P8: CRITICAL issue | Architecture redesign needed | **→ P3** (Architect) |

> **Limits**: Max 5 total LOOPBACKs, max 2 per phase. Exceeded → Partial Report → P9.

## Phases

| Phase | Agent | Parallel | Tools | Output |
|-------|-------|:--------:|-------|--------|
| P1 | Requirements Analyst | - | Read, Glob, Grep, Write | `docs/requirements/` |
| P2 | Code Explorer | x3 | Read, Glob, Grep | _(internal)_ |
| P3 | Code Architect | x3 | Read, Glob, Grep, Write | `docs/architecture/` |
| P4 | Test Engineer (Unit) | - | Read, Write, Edit, Bash | `tests/unit/` |
| P5 | Implementer | - | Read, Write, Edit, Bash | `src/[feature]/` |
| P6 | Test Engineer (IT/E2E) | - | Read, Write, Edit | `tests/integration/`, `tests/e2e/` |
| P7 | Test Runner | - | Read, Bash | RTM results |
| P8 | Code Reviewer | x3 | Read, Glob, Grep | _(in report)_ |
| JUDGE | Harness (RTM) | - | RTM Read | LOOPBACK decision |
| P9 | Report Writer | - | Read, Write | `reports/` |

## Key Concepts

- **RTM is the Single Source of Truth** -- Cumulatively updated at P1/P4/P5/P6/P7; used by Judge for pass/fail evaluation
- **File = Agent Interface** -- Sub-agents communicate exclusively through the file system, never directly
- **LOOPBACK never changes requirements** -- Requirements are immutable; 3 regression paths (P3/P5/P6)
- **Context Isolation** -- Each sub-agent runs in an independent context with scoped tool permissions
- **TDD-First** -- P4 writes failing tests (RED) → P5 makes them pass (GREEN) → P7 verifies

## License

MIT
