# HALO Workflow

> [한국어 문서](i18n/ko/README.md)

**Harness-Agentic Loopback Orchestration**

A 3-layer AI agent orchestration framework for TDD-based software development with full requirements traceability.

> **[Interactive Architecture Diagram](https://FREEDOBY.github.io/halo-workflow/)**

## Quick Start

1. Copy `.claude/` folder to your project
2. Run `/halo-workflow [feature description]`

## Architecture

```
HARNESS (Orchestrator + RTM Judge)
  P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → JUDGE → P9
  RTM: ●──────●──────●───────●──────●──▶◆
       init  +UT   +impl +IT/E2E +result  Judge
                                    ↓
                     Arch Issue → P3
                     Impl Bug  → P5
                     Test Design → P6

AI AGENTS (Phase-Isolated, Tool-Restricted)
  9 sub-agents with scoped tool permissions

ARTIFACTS (File = Agent Interface)
  docs/ │ tests/ │ src/ │ .workflow/ │ reports/
```

## Phases

| Phase | Agent | Role |
|-------|-------|------|
| P1 | Requirements Analyst | Requirements analysis + RTM initialization |
| P2 | Code Explorer x3 | Codebase exploration (parallel) |
| P3 | Code Architect x3 | Architecture design (parallel) |
| P4 | Test Engineer (Unit) | TDD RED - Write unit tests |
| P5 | Implementer | TDD GREEN - Implementation |
| P6 | Test Engineer (IT/E2E) | Write integration/E2E tests |
| P7 | Test Runner | Execute full test suite |
| P8 | Code Reviewer x3 | Code review (parallel) |
| JUDGE | Harness (RTM) | RTM-based LOOPBACK evaluation |
| P9 | Report Writer | Final report |

## Key Concepts

- **RTM Timeline** -- Cumulatively updated at P1/P4/P5/P6/P7; used by Judge for evaluation
- **LOOPBACK** -- Requirements are immutable; 3 regression paths (P3/P5/P6)
- **Context Isolation** -- Sub-agents run in independent contexts, communicating only via files
- **Tool Restriction** -- Allowed tools vary by phase (e.g., exploration agents cannot write)

## License

MIT
