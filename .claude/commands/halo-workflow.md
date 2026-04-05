---
description: "HALO Workflow - Harness-Agentic Loopback Orchestration"
argument-hint: "[feature description]"
---

# HALO Workflow v3 (Harness-Agentic Loopback Orchestration)

You are the **HALO Workflow Main Agent**. You **directly execute** RTM-centric full traceability and TDD-based development. Sub-agents are used only for P8 (review) and JUDGE (evaluation).

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│  MAIN AGENT  (Executor + Router)                                   │
│                                                                    │
│  P1 ──→ P2 ──→ P3 ──→ P4 ──→ P5 ──→ P6 ──→ P7 ──→ P8 ──→ P9  │
│  direct direct direct direct direct direct direct  ↕    direct   │
│  ─────────── Main continuous (zero context breaks) ─ │              │
│                                                   Review  JUDGE    │
│                                                  ┌─┴─┐  ┌───┐    │
│                                                  │ ×3 │  │ ×1│    │
│                                                  └───┘  └─┬─┘    │
│                                                           │       │
│               Based on JUDGE verdict:                      │       │
│              ┌──── Test Bug → P4 ─────────────────────────┘       │
│              ├──── Impl Bug → P5                                  │
│              ├──── Test Design → P6                                │
│              └──── Arch Issue → P3                                 │
│                                                                    │
│  On context compression → recover from .workflow/phase-results/    │
├────────────────────────────────────────────────────────────────────┤
│  .workflow/    Checkpoint + State (temporary, gitignored)          │
├────────────────────────────────────────────────────────────────────┤
│  docs/ tests/ src/ reports/    Product Artifacts (permanent)       │
└────────────────────────────────────────────────────────────────────┘
```

## Workflow Process

```
  /halo-workflow "feature description"
                    │
                    ▼
  ┌───────────────────────────────────────────────────────────────────┐
  │                                                                   │
  │   P1  Requirements      [Main direct] Requirements + Constraints │
  │       Analysis           → Initialize RTM (register REQ-IDs)     │
  │         │                  Greenfield → Confirm tech stack w/user │
  │         ▼                                                         │
  │   P2  Codebase           [Main direct] Glob/Grep/Read            │
  │       Exploration        Greenfield → Auto-skip                  │
  │         │                                                         │
  │         ▼                                                         │
  │   P3  Architecture       [Main direct] Design                ◀──┐│
  │       Design             → docs/architecture/[feature].md       ││
  │         │                                                       ││
  │         ▼                                                       ││
  │   P4  Unit Test          [Main direct] TDD RED              ◀─┐││
  │       (TDD RED)          → Map Unit TC-IDs in RTM             │││
  │         │                                                     │││
  │         ▼                                                     │││
  │   P5  Implementation     [Main direct] TDD GREEN           ◀┐│││
  │       (TDD GREEN)        → Map impl locations in RTM        ││││
  │         │                                                   ││││
  │         ▼                                                   ││││
  │   P6  Integration &      [Main direct] Real env E2E       ◀┐││││
  │       E2E Test           → Map IT/E2E TC-IDs in RTM        │││││
  │         │                                                  │││││
  │         ▼                                                  │││││
  │   P7  Test Execution     [Main direct] Unit→IT→E2E→Smoke  │││││
  │                          → Record results (PASS/FAIL) in RTM│││││
  │         │                                                  │││││
  │         │  ANY FAIL → Immediately invoke JUDGE (skip P8)   │││││
  │         │  ALL PASS ↓                                      │││││
  │         ▼                                                  │││││
  │   P8  Code Review        [Sub ×3] Quality/Bugs/Security    │││││
  │                          → Main records issues in RTM       │││││
  │         │                                                  │││││
  │         ▼                                                  │││││
  │   ┌──────────┐  FAIL    JUDGE [Sub ×1] Reads RTM only:    │││││
  │   │  JUDGE   │───────→   Test Design ─────────────────────┘││││
  │   │  (Sub)   │───────→   Test Bug ─────────────────────────┘│││
  │   │          │───────→   Impl Bug ──────────────────────────┘││
  │   │          │───────→   Arch Issue ─────────────────────────┘│
  │   └────┬─────┘                                                │
  │        │ PASS                                                 │
  │        ▼                                                      │
  │   P9  Completion         [Main direct] Final report           │
  │       Report             → reports/[feature]-completion.md    │
  │                                                                │
  │   ※ Checkpoint + RTM update MUST be performed after each Phase │
  └────────────────────────────────────────────────────────────────┘
```

## RTM = Single Source of Truth

The RTM is the sole source of truth for the entire workflow. Each phase updates the RTM, and JUDGE reads only the RTM to evaluate.

```
  P1           P4           P5            P6            P7       P8       JUDGE
  ●────────────●────────────●─────────────●─────────────●────────●────────▶ ◆
  │            │            │             │             │        │          │
  init RTM     +Unit TC     +impl loc     +IT/E2E TC   +result  +review   RTM only
  REQ-IDs      mapping      file:line     mapping      PASS/    issues    → Read
                                                        FAIL    reflect   → evaluate
```

### RTM Structure

```markdown
# RTM: [Feature Name]

## Metadata
- Created: [date]
- Last Updated: [date]
- Version: [version]
- Status: [Initialized | In Progress | Verified | Complete]

## Traceability Matrix

| REQ-ID | Requirement | Priority | Unit TC | Integration TC | E2E TC | Impl Location | Result | Review | Status |
|--------|-------------|----------|---------|----------------|--------|---------------|--------|--------|--------|

## Coverage Summary
- Total requirements: X
- TC mapped: N (N%)
- Implementation complete: N (N%)
- Tests passing: N (N%)

## Update History
| Date | Phase | Changes |
|------|-------|---------|
```

**RTM Column Descriptions:**
- `Result`: Recorded in P7. PASS / FAIL / - (not executed)
- `Review`: Recorded in P8. PASS / MINOR / MAJOR / CRITICAL / - (not reviewed)
- `Status`: Registered → Unit TC Mapped → Implemented → All TC Mapped → Verified → Complete

---

## Core Principles

```
1. Main Agent First: P1~P7 executed directly by main. Sub-agents for P8 (review) and JUDGE (evaluation) only.
2. RTM = Single Source of Truth: Every phase updates RTM. JUDGE reads RTM only to evaluate.
3. File = Interface: Inter-agent communication and context recovery via file system only.
4. Constraint Verification: External dependency assumptions must be verified by actual calls.
5. Real E2E: E2E tests run in real environment. No mocks.
6. LOOPBACK does not change requirements: Requirement changes start a new cycle.
7. Max 5 LOOPBACK, per-phase 2 max: Exceeded → Partial Report → P9.
```

---

## Execution Model

### Main Agent Direct Execution (8 Phases)

| Phase | Role | RTM Update |
|-------|------|------------|
| P1 | Requirements Analysis + Constraint Verification | Initialize RTM (register REQ-IDs) |
| P2 | Codebase Exploration | - (skip if Greenfield) |
| P3 | Architecture Design | - |
| P4 | Unit Test (TDD RED) | Unit TC-ID mapping |
| P5 | Implementation (TDD GREEN) | Impl location (file:line) mapping |
| P6 | Integration + E2E Test | IT/E2E TC-ID mapping |
| P7 | Test Execution + Smoke Test | Result (PASS/FAIL) recording |
| P9 | Completion Report | Status → Complete |

**P1→P7 main continuous execution. Zero context breaks.**

### Sub-Agents (2 Points)

| Phase | Role | Input | Output |
|-------|------|-------|--------|
| P8 | Code Review ×3 parallel | src/, tests/, docs/ | Issue messages → Main records in RTM |
| JUDGE | RTM Evaluation ×1 | RTM file only | Verdict message → Main executes LOOPBACK |

### Sub-Agent Prompt Rules

```
Prohibited: Summarizing/quoting previous phase artifacts in the prompt
Required: Pass file paths only; agent reads files directly
```

---

## Context Management

### Checkpoints (After Each Phase — Mandatory)

**This is not optional. The last action of each phase MUST be writing the checkpoint.**

```
After each phase completion:
  1. Update .workflow/state.json (current_phase, completed_phases)
  2. Write .workflow/phase-results/P{N}.md (schema below)
  3. Update RTM (phase progress status)
```

### Checkpoint Schema

```markdown
# Phase Result: P{N} - [Phase Name]

## Status
COMPLETE | FAIL | SKIPPED

## Artifacts
- [list of file paths]

## Key Decisions
- [decisions and rationale]

## Context Snapshot
- [reading only this section should be sufficient to resume after context compression]

## RTM Delta
- [content added/changed in RTM during this phase]

## Next Phase Input
- [file paths the next phase needs to read]
```

### Context Compression Recovery

```
1. .workflow/state.json → current phase
2. RTM → overall progress status
3. .workflow/phase-results/ → Context Snapshot, Key Decisions
4. Resume from there
```

### state.json Schema

```json
{
  "feature": "[feature-slug]",
  "current_phase": "P1",
  "loopback_count": 0,
  "loopback_per_phase": {},
  "completed_phases": [],
  "greenfield": false,
  "rtm_path": "docs/requirements/[feature]-rtm.md",
  "started_at": "[date]"
}
```

---

## Test Levels

```
Level 0: UNIT TEST      → Mocks allowed, isolated verification.     Written in P4, executed in P5 (TDD)
Level 1: INTEGRATION    → Minimal mocks, module interaction.        Written in P6, executed in P7
Level 2: E2E TEST       → No mocks, real environment.               Written in P6, executed in P7
Level 3: SMOKE TEST     → Server startup + core feature verified.   Executed in P7
```

---

## Artifact Structure

```
docs/
├── requirements/
│   ├── [feature].md             # Requirements (P1)
│   └── [feature]-rtm.md        # RTM — Single Source of Truth
└── architecture/
    └── [feature].md             # Architecture (P3)

tests/
├── unit/                        # Unit Tests (P4)
├── integration/                 # Integration Tests (P6)
└── e2e/                         # E2E Tests (P6)

src/[feature]/                   # Implementation (P5)

.workflow/                       # Temporary, gitignored
├── state.json
├── loopback-context.md
└── phase-results/P{N}.md

reports/[feature]-completion.md  # Completion Report (P9)
```

---

## USER INPUT

**Feature Request**: $ARGUMENTS

---

## EXECUTION PROTOCOL

### ═══════════════════════════════════════════════════════════════
### PHASE 1: REQUIREMENTS ANALYSIS (Main Direct)
### ═══════════════════════════════════════════════════════════════

**Output**: `docs/requirements/[feature].md`, `docs/requirements/[feature]-rtm.md`

#### 1.1 Context Gathering + Greenfield Detection

```
1. Analyze project structure (Glob, Grep)
2. Identify existing code patterns, tech stack, dependencies
3. Identify related modules/files

Greenfield detection:
  If no code in src/ or no build config/dependency files → Greenfield
```

#### 1.1.1 System Decisions (Greenfield Only — User Confirmation)

Executed only for Greenfield projects. Automatically skipped if existing code is detected.

```
Confirm with user:
1. Language/Runtime
2. Framework
3. Deployment environment
4. External dependencies
5. Other constraints

After approval → Record in requirements doc "System Decisions" section
Entire workflow proceeds autonomously afterward (no additional user gates)
```

#### 1.2 Requirements Derivation

```
Derive: Core features, edge cases, NFR (performance/security), constraints
```

#### 1.3 Ambiguity Handling

Greenfield tech decisions require user confirmation. All other ambiguities are resolved automatically and documented.

#### 1.4 Constraint Verification

```
External API → Verify via actual calls
Deployment env → Confirm runtime constraints
Runtime compatibility → Verify library support
Record results in requirements doc "Verified Constraints" section
```

#### 1.5 Requirements Document

```markdown
# Requirements: [Feature Name]

## 1. Functional Requirements
| REQ-ID | Requirement | Priority | Acceptance Criteria |

## 2. Non-Functional Requirements
| NFR-ID | Category | Requirement | Measurement |

## 3. Edge Cases
| EDGE-ID | Scenario | Expected Behavior | Related REQ |

## 4. Constraints (Verified)
## 5. System Decisions (Greenfield — User Approved)
## 6. Decisions (Auto-resolved)
```

#### 1.6 RTM Initialization

```markdown
| REQ-ID | Requirement | Priority | Unit TC | Integration TC | E2E TC | Impl Location | Result | Review | Status |
| REQ-001 | ... | P1 | - | - | - | - | - | - | Registered |
```

#### 1.7 Completion

```
□ Requirements doc + RTM initialization complete
□ Constraint verification complete
□ state.json initialized (greenfield flag)
□ .workflow/phase-results/P1.md written
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 2: CODEBASE EXPLORATION (Main Direct)
### ═══════════════════════════════════════════════════════════════

#### 2.0 Greenfield Skip Gate

```
greenfield == true → Skip. Record SKIPPED in P2.md. Proceed to P3.
greenfield == false → Execute below.
```

#### 2.1 Exploration

```
1. Project structure (Glob)
2. Similar features (Grep)
3. Architecture (Read entry points, service layers)
4. Test patterns (examine existing test structure)
5. Read key files directly
```

#### 2.2 Completion

```
□ .workflow/phase-results/P2.md written
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 3: ARCHITECTURE DESIGN (Main Direct)
### ═══════════════════════════════════════════════════════════════

**Output**: `docs/architecture/[feature].md`

#### 3.1 Design

```
Design directly based on P1~P2 context.

Include:
- File structure (create/modify)
- Interface contracts (public function signatures) — P4, P5 follow these
- Data flow
- Integration points
```

#### 3.2 Architecture Document

```markdown
# Architecture: [Feature Name]
## 1. Design Overview
## 2. File Structure
## 3. Interface Contract
## 4. Data Flow
## 5. Integration Points
```

#### 3.3 Completion

```
□ docs/architecture/[feature].md written
□ .workflow/phase-results/P3.md written
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 4: UNIT TEST — TDD RED (Main Direct)
### ═══════════════════════════════════════════════════════════════

**Output**: `tests/unit/[feature].*`
**RTM Update**: Unit TC-ID mapping

#### 4.1 Unit Test Writing

```
1. Isolation: Mock/Stub external dependencies
2. AAA: Arrange → Act → Assert
3. Map REQ-IDs via @requirement annotations
4. Test only functions defined in architecture interface contracts
```

#### 4.2 RTM Update: Unit TC Mapping

```
Record Unit TC-IDs for each REQ in RTM. Add update history entry.
```

#### 4.3 RED Confirmation

```
Run all Unit Tests → Confirm FAIL (no implementation yet)
```

#### 4.4 Completion

```
□ Unit TC-IDs mapped in RTM
□ RED confirmed
□ .workflow/phase-results/P4.md written
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 5: IMPLEMENTATION — TDD GREEN (Main Direct)
### ═══════════════════════════════════════════════════════════════

**Output**: `src/[feature]/*`
**RTM Update**: Impl location (file:line) mapping

#### 5.1 Implementation

```
1. Incremental: Pass one test at a time
2. Follow architecture interface contracts
3. Security check: Input validation, sensitive data handling
```

#### 5.2 RTM Update: Impl Location Mapping

```
Record impl location (file:line) for each REQ in RTM. Add update history entry.
```

#### 5.3 GREEN Confirmation

```
Run all Unit Tests → Confirm PASS
```

#### 5.4 Completion

```
□ Impl locations mapped in RTM
□ GREEN confirmed
□ .workflow/phase-results/P5.md written
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 6: INTEGRATION & E2E TEST (Main Direct)
### ═══════════════════════════════════════════════════════════════

**Output**: `tests/integration/*`, `tests/e2e/*`
**RTM Update**: Integration TC + E2E TC mapping

#### 6.1 Integration Test

```
Minimal mocks. Verify actual module interactions. @requirement annotations.
```

#### 6.2 E2E Strategy Decision

```
Determine project type:
  Web frontend → Browser automation + server startup
  Web API      → HTTP client + real server
  CLI          → Subprocess execution + stdout verification
  Library      → Integration is sufficient (E2E not applicable)
```

#### 6.3 E2E Environment Setup + E2E Test Writing

```
Required: Real environment (no mocks). Given-When-Then. @requirement annotations.
Prohibited: fetch/HTTP mocks, DOM mocks, "E2E-style" unit tests.
```

#### 6.4 RTM Update: IT/E2E TC Mapping

```
Record Integration/E2E TC-IDs in RTM. Add update history entry.
```

#### 6.5 Completion

```
□ IT/E2E TC-IDs mapped in RTM
□ .workflow/phase-results/P6.md written
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 7: TEST EXECUTION (Main Direct)
### ═══════════════════════════════════════════════════════════════

**RTM Update**: Test results (PASS/FAIL) recording

#### 7.1 Execution Order

```
Step 1: UNIT TEST → Step 2: INTEGRATION → Step 3: E2E → Step 4: SMOKE
```

#### 7.2 E2E Quality Verification

```
Regardless of test PASS/FAIL:
  □ No mock/stub/spy in E2E code?
  □ Real server started?
  □ Requests sent to real endpoints?
If not met → Record FAIL in RTM
```

#### 7.3 RTM Update: Test Result Recording

```
Record test results (PASS/FAIL) in RTM Result column for each REQ.
Add update history entry.
```

#### 7.4 Branching

```
ALL PASS → Proceed to P8
ANY FAIL → Record FAIL in RTM, then immediately spawn JUDGE (skip P8)
```

#### 7.5 Completion

```
□ Results recorded in RTM
□ .workflow/phase-results/P7.md written
  (Write checkpoint even on FAIL, then proceed to JUDGE)
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 8: CODE REVIEW (Sub-Agents ×3 Parallel)
### ═══════════════════════════════════════════════════════════════

**Executed only when P7 ALL PASS.**

#### 8.1 Parallel Review

```
Agent 1: Quality/DRY/Readability — src/, docs/architecture/
Agent 2: Bugs/Correctness        — src/, tests/
Agent 3: Conventions/Security    — src/, docs/requirements/

Report only issues with 80%+ confidence.
```

#### 8.2 Main: Record Review Results in RTM

```
After collecting issues from ×3 sub-agents:
  → Record review results in RTM Review column for each REQ (PASS/MINOR/MAJOR/CRITICAL)
  → Add P8 entry to update history
  → Spawn JUDGE sub-agent (pass RTM path only)
```

---

### ═══════════════════════════════════════════════════════════════
### JUDGE: RTM-BASED LOOPBACK EVALUATION (Sub-Agent ×1)
### ═══════════════════════════════════════════════════════════════

**Purpose**: Eliminate main agent bias. Read RTM only for objective evaluation.

**Input**: `docs/requirements/[feature]-rtm.md` — Read only the RTM file.
**Output**: Return verdict as message (no file writes)

The RTM contains all necessary information:
- REQ-ID ↔ TC-ID mapping
- Impl location (file:line)
- Test results (PASS/FAIL)
- Review results (PASS/MINOR/MAJOR/CRITICAL)

May additionally Read test/implementation files traced back from RTM as needed.

#### Spawn Timing

```
1. P7 ANY FAIL → Skip P8, immediately invoke JUDGE
2. After P8 completion → JUDGE (confirm PASS or determine LOOPBACK)
```

#### RTM Evaluation Process

```
STEP 1: Identify REQ-IDs with FAIL or MAJOR/CRITICAL in RTM
STEP 2: Trace REQ-ID → TC-ID → impl location (file:line)
STEP 3: Read test/impl code directly as needed to classify root cause
STEP 4: Return verdict

Root cause classification:
  Test Bug:    Wrong test expectations, assertion errors → P4
  Impl Bug:    Logic errors, unhandled exceptions → P5
  Test Design: E2E scenario/env issues, mock usage → P6
  Arch Issue:  Module interface mismatch, design flaws → P3
```

#### JUDGE Return Format

```
## Verdict: PASS | LOOPBACK
## Target Phase: P3 | P4 | P5 | P6
## Root Cause: [Test Bug | Impl Bug | Test Design | Arch Issue]
## Failed Items:
  - [TC-ID or review issue] — [error summary]
## RTM Trace:
  - TC-ID → REQ-ID → file:line
## Instructions: [specific fix instructions]
```

---

### ═══════════════════════════════════════════════════════════════
### LOOPBACK EXECUTION (Main Agent)
### ═══════════════════════════════════════════════════════════════

After receiving JUDGE verdict:

#### PASS → Proceed to P9

#### LOOPBACK →

```
1. Record in .workflow/loopback-context.md:
   ## LOOPBACK #N
   - Cause / Failed Items / RTM Trace / Target / Instructions

2. Update state.json (loopback_count++, loopback_per_phase)

3. Check limits:
   same_phase 2 times → Escalate to higher phase (P5→P3, P6→P3, P4→P3)
   total > 5 → Partial Report → P9

4. Regress to target phase and fix

5. Re-execution scope (from regression phase to end):
   P3 regression: P3 → P4 → P5 → P6 → P7 → [P8] → JUDGE
   P4 regression: P4 → P5 → P6 → P7 → [P8] → JUDGE
   P5 regression: P5 → P6 → P7 → [P8] → JUDGE
   P6 regression: P6 → P7 → [P8] → JUDGE
```

#### Artifact Update Matrix

```
→ P3 (Arch Issue):   RTM ✅  Arch ✅  Tests ✅  Impl ✅
→ P4 (Test Bug):     RTM ✅  Arch -   Tests ✅  Impl -
→ P5 (Impl Bug):     RTM ✅  Arch -   Tests -   Impl ✅
→ P6 (Test Design):  RTM ✅  Arch -   Tests ✅  Impl -
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 9: COMPLETION REPORT (Main Direct)
### ═══════════════════════════════════════════════════════════════

**Output**: `reports/[feature]-completion.md`

```markdown
# Completion Report: [Feature Name]

## Metadata
- Workflow: HALO v3
- Completed: [date]
- LOOPBACK count: N

## 1. Feature Summary
## 2. Artifact List
## 3. RTM Final State
## 4. Code Review Results
## 5. Test Results
## 6. LOOPBACK History
## 7. Next Steps
```

---

## WORKFLOW FLAGS

```
--autonomous        # Autonomous mode (default)
--skip-review       # Skip P8 code review
--skip-exploration  # Skip P2 codebase exploration
--skip-architecture # Skip P3 architecture design
--max-loops N       # Max LOOPBACK count (default: 5)
```

---

## NOW EXECUTING...

**Feature Request**: $ARGUMENTS

**Phase 1: REQUIREMENTS ANALYSIS starting...**
