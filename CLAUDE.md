# HALO Workflow Project

## Usage
```
/halo-workflow [feature description]
```

## Core Principles
- **RTM is Single Source of Truth** -- `docs/requirements/*-rtm.md`
- **File = Agent Interface** -- All inter-agent communication is file-system only
- **LOOPBACK never changes requirements** -- No P1 regression (requirement changes = new cycle)
- **Max 5 LOOPBACK, per-phase 2 max** -- Exceeding limit generates a Partial Report

## 3-Layer Architecture
1. **Harness** -- Main orchestrator, state machine, RTM Judge
2. **AI Agents** -- Phase-isolated sub-agents with restricted tool access
3. **Artifacts** -- File system (docs/, tests/, src/, reports/)

## Agent Definitions
Phase-specific agents are defined in `.claude/commands/agents/`.
The main orchestrator loads the corresponding agent prompt upon entering each phase.
