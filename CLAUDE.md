# HALO Workflow Project

## Usage
```
/halo-workflow [feature description]
```

## Core Principles
- **Main Agent First** — Sequential work is done by the main agent directly. Sub-agents for parallel only.
- **RTM = Single Source of Truth** — `docs/requirements/*-rtm.md`
- **File = Interface** — Inter-agent communication and context recovery via file system only
- **Constraint Verification** — External API/deployment assumptions must be verified by actual calls
- **Real E2E** — E2E tests run in real environment. No mocks allowed.
- **LOOPBACK never changes requirements** — Requirement changes = new cycle
- **Max 5 LOOPBACK, per-phase 2 max** — Exceeding limit generates a Partial Report

## Execution Model
- **Main direct** (6 Phases): P1 requirements, P4 tests, P5 implementation, P6 IT/E2E, P7 execution, P9 report
- **Sub-agents** (3 Phases): P2 scouting, P3 competing designs, P8 review

## Sub-Agent Roles
- **P2 Scouts**: Report key file lists → Main reads directly
- **P3 Competing Designs**: Design proposals + referenced code → Main reviews and finalizes
- **P8 Reviewers**: Report issues by perspective → Main synthesizes judgment

## Agent Definitions
Sub-agent definitions (P2, P3, P8) are in `.claude/commands/agents/`.
