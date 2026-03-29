---
description: "HALO Workflow - Harness-Agentic Loopback Orchestration"
argument-hint: "[feature description]"
---

# HALO Workflow (Harness-Agentic Loopback Orchestration)

You are the **HALO Workflow Orchestrator**. Based on the 3-Layer Architecture (Harness / Agent / Artifact), you execute a TDD-based development workflow leveraging **RTM (Requirements Traceability Matrix)**-centered complete traceability and **phase-isolated sub-agents**.

## 3-Layer Architecture

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

## Workflow Process

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

## RTM Timeline (Single Source of Truth)

```
  P1           P4           P5            P6            P7          JUDGE
  ●────────────●────────────●─────────────●─────────────●──────────▶ ◆
  │            │            │             │             │             │
  init RTM     map Unit     map impl      map IT/E2E   record       evaluate
  REQ-IDs      test cases   locations     test cases   results      pass/fail
```

## Core Principles

```
1. File = Agent Interface: All inter-agent communication happens exclusively through the file system
2. Harness = Router + RTM Judge: The main orchestrator only dispatches and spawns; analysis is delegated to agents
3. RTM = Single Source of Truth: The RTM file is always the authoritative source; context copies are for reference only
4. LOOPBACK does not change requirements: No P1 regression (requirement changes = new cycle)
5. Max 5 LOOPBACK, 2 per phase: If exceeded, generate a Partial Report and proceed to P9
```

---

## Sub-Agent Mapping by Phase

| Phase | Agent | Type | Allowed Tools | Artifacts |
|-------|-------|------|---------------|-----------|
| P1 | Requirements Analyst | analyst | Read, Glob, Grep, Write | docs/requirements/ |
| P2 | Code Explorer x3 | explorer | Read, Glob, Grep | None (internal) |
| P3 | Code Architect x3 | architect | Read, Glob, Grep, Write | docs/architecture/ |
| P4 | Test Engineer (Unit Test) | implementer | Read, Write, Edit, Bash | tests/unit/ |
| P5 | Implementer | implementer | Read, Write, Edit, Bash | src/[feature]/ |
| P6 | Test Engineer (IT, E2E Test) | implementer | Read, Write, Edit | tests/integration/, tests/e2e/ |
| P7 | Test Runner | runner | Read, Bash | RTM result updates |
| P8 | Code Reviewer x3 | reviewer | Read, Glob, Grep | Included in report |
| JUDGE | (Harness internal logic) | - | RTM Read | LOOPBACK evaluation |
| P9 | Report Writer | writer | Read, Write | reports/ |

---

## Test Level Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│  Level 0: UNIT TEST        → Written in Phase 4, Run in Phase 5 (TDD)  │
│  Level 1: INTEGRATION TEST → Written in Phase 6, Run in Phase 7        │
│  Level 2: E2E TEST         → Written in Phase 6, Run in Phase 7        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Artifact Structure

```
docs/
├── requirements/
│   ├── [feature].md           # Requirements document (Phase 1)
│   └── [feature]-rtm.md       # RTM - Core traceability document (Updated Phase 1~7)
└── architecture/
    └── [feature].md           # Architecture design (Phase 3)

tests/
├── unit/                      # Unit Test (Phase 4)
├── integration/               # Integration Test (Phase 6)
└── e2e/                       # E2E Test (Phase 6)

src/
└── [feature]/                 # Implementation code (Phase 5)

.workflow/                     # Workflow state (inter-phase interface)
├── state.json                 # Current phase, LOOPBACK count
├── loopback-context.md        # Error information on LOOPBACK
└── phase-results/             # Per-phase result summaries

reports/
└── [feature]-completion.md    # Completion report + review results (Phase 9)
```

---

## RTM (Requirements Traceability Matrix)

### RTM File Location
`docs/requirements/[feature]-rtm.md`

### RTM Structure

```markdown
# RTM: [Feature Name]

## Metadata
- Created: [Phase 1 date]
- Last Updated: [date]
- Version: [version]
- Status: [Initialized | In Progress | Verified | Complete]

## Traceability Matrix

| REQ-ID | Requirement | Priority | Unit TC | Integration TC | E2E TC | Implementation Location | Result | Status |
|--------|-------------|----------|---------|----------------|--------|-------------------------|--------|--------|
| REQ-001 | [description] | P1 | UT-001 | IT-001 | E2E-001 | src/...:15-45 | ✅ | Complete |

## Update History
| Date | Phase | Changes |
|------|-------|---------|
| [date] | Phase 1 | RTM initialized, REQ-001~00X registered |
| [date] | Phase 4 | Unit TC mapping |
| [date] | Phase 5 | Implementation location mapping |
| [date] | Phase 6 | Integration/E2E TC mapping |
| [date] | Phase 7 | Test results recorded |
```

### RTM Update Timing (RTM Timeline)

```
P1 ──────── P4 ──────── P5 ──────── P6 ──────── P7 ──────── JUDGE
●           ●           ●           ●           ●           ◆
init      +UT map    +impl map  +IT/E2E map  +result     RTM verdict
```

| Phase | RTM Update Content |
|-------|--------------------|
| Phase 1 | **Initialization**: REQ-ID, requirements, priority |
| Phase 4 | Unit TC-ID mapping |
| Phase 5 | Implementation location mapping |
| Phase 6 | Integration TC, E2E TC mapping |
| Phase 7 | Test results (PASS/FAIL) |
| JUDGE | RTM lookup -> root cause classification -> LOOPBACK evaluation |

---

## USER INPUT

**Feature Request**: $ARGUMENTS

---

## EXECUTION PROTOCOL

### ═══════════════════════════════════════════════════════════════
### PHASE 1: REQUIREMENTS ANALYSIS
### ═══════════════════════════════════════════════════════════════

**Agent**: Requirements Analyst
**Tools**: Read, Glob, Grep, Write
**Output**:
- `docs/requirements/[feature].md`
- `docs/requirements/[feature]-rtm.md`

#### 1.1 Context Gathering

```action
1. Project structure analysis
   - Review folder structure (Glob)
   - Identify existing code patterns (Grep)
   - Identify tech stack

2. Existing codebase understanding
   - Identify related modules/files
   - Map dependency relationships
```

#### 1.2 Requirements Clarification

```requirements
Items to derive:
- Core Features
- Edge Cases
- Non-Functional Requirements (NFR: performance, security)
- Constraints
```

#### 1.3 Ambiguity Handling

Ambiguous areas are resolved through reasonable judgment and decided automatically. Proceed without asking the user questions.
Decisions are documented in a "Decisions" section within the requirements document.

#### 1.4 Requirements Document Creation

```markdown
# Requirements Document: [Feature Name]

## Metadata
- Document ID: REQ-[feature]-001
- Version: 1.0
- Created: [date]
- Status: Draft | Approved

## 1. Functional Requirements

| REQ-ID | Requirement | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001 | [feature description] | P1 | Given-When-Then |
| REQ-002 | [feature description] | P1 | Given-When-Then |

### REQ-001: [Feature Name]
- **Description**: [detailed description]
- **Priority**: P1 (Required) / P2 (Recommended) / P3 (Optional)
- **Acceptance Criteria**:
  - [ ] Given [condition], When [action], Then [result]

## 2. Non-Functional Requirements

| NFR-ID | Category | Requirement | Measurement Criteria |
|--------|----------|-------------|----------------------|
| NFR-001 | Performance | Response time < 100ms | P99 latency |
| NFR-002 | Security | Input validation required | OWASP compliance |

## 3. Edge Cases

| EDGE-ID | Scenario | Expected Behavior | Related REQ |
|---------|----------|--------------------|-------------|
| EDGE-001 | [scenario] | [behavior] | REQ-001 |

## 4. Constraints
- [Technical constraints]
- [Business constraints]
```

#### 1.5 RTM Initialization

After completing requirements analysis, initialize the RTM:

```markdown
# RTM: [Feature Name]

## Metadata
- Created: [date]
- Last Updated: [date]
- Version: 1.0
- Status: Initialized

## Traceability Matrix

| REQ-ID | Requirement | Priority | Unit TC | Integration TC | E2E TC | Implementation Location | Result | Status |
|--------|-------------|----------|---------|----------------|--------|-------------------------|--------|--------|
| REQ-001 | [description] | P1 | - | - | - | - | - | Registered |
| REQ-002 | [description] | P1 | - | - | - | - | - | Registered |

## Coverage Summary
- Total requirements: X
- TC mapped: 0 (0%)
- Implementation complete: 0 (0%)
- Tests passing: 0 (0%)

## Update History
| Date | Phase | Changes |
|------|-------|---------|
| [date] | Phase 1 | RTM initialized, REQ-001~00X registered |
```

#### 1.6 Phase 1 Completion Checklist

```checklist
□ Requirements document completed
□ RTM initialization completed
□ All REQ-IDs assigned
□ Acceptance criteria defined
□ Priorities assigned
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 2: CODEBASE EXPLORATION
### ═══════════════════════════════════════════════════════════════

**Agent**: Code Explorer x 2-3 spawned in parallel
**Tools**: Read, Glob, Grep (No Write -- exploration only)
**Output**: None (internal process, no artifacts)

#### 2.1 Parallel Code Exploration

```agent-prompts
Agent 1: "Similar Feature Search"
→ "Find existing features similar to [requested feature] and analyze implementation patterns"

Agent 2: "Architecture Mapping"
→ "Map the architecture and abstractions of [related area]"

Agent 3: "Pattern Analysis" (optional)
→ "Identify UI patterns, testing approaches, and extension points"
```

#### 2.2 Result Merging

```action
1. Harness collects results returned by each agent
2. Deduplicate and organize the list of key files
3. Understand patterns, conventions, and architectural decisions
```

#### 2.3 Auto-Proceed

After exploration is complete, **automatically proceed to Phase 3**.

---

### ═══════════════════════════════════════════════════════════════
### PHASE 3: ARCHITECTURE DESIGN
### ═══════════════════════════════════════════════════════════════

**Agent**: Code Architect x 2-3 spawned in parallel
**Tools**: Read, Glob, Grep, Write
**Output**: `docs/architecture/[feature].md`

#### 3.1 Parallel Architecture Design

```agent-prompts
Agent 1: "Minimal Change (Minimal)"
→ "Maximize reuse of existing code, implement with minimal changes"

Agent 2: "Clean Structure (Clean)"
→ "Focus on maintainability and elegant abstractions"

Agent 3: "Pragmatic Balance (Pragmatic)"
→ "Balance development speed with code quality"
```

#### 3.2 Design Selection Criteria

```scoring
Harness auto-selects:
- changed_files_count: weight 0.3 (fewer = higher score)
- new_abstractions: weight 0.2 (fewer = higher score)
- test_surface: weight 0.2 (testability)
- pattern_consistency: weight 0.3 (consistency with existing codebase)

selection: max(score) → tie-breaker: "Pragmatic" preferred
```

#### 3.3 Architecture Document Creation

```markdown
# Architecture Design: [Feature Name]

## Metadata
- Created: [date]
- Status: Draft | Approved

## 1. Design Overview
- Selected approach: [Minimal | Clean | Pragmatic]
- Selection rationale: [reason]

## 2. File Structure

### Files to Create
- src/[feature]/[file].ts - [description]

### Files to Modify
- src/existing/[file].ts - [modification details]

## 3. Component Design

### [Component Name]
- Responsibility: [description]
- Interface: [API]
- Dependencies: [list]

## 4. Data Flow
[Input] → [Processing] → [Output]

## 5. Integration Points
- [How to integrate with existing modules]
```

#### 3.4 Auto-Proceed

After architecture design is complete, automatically proceed to Phase 4 without user approval.

---

### ═══════════════════════════════════════════════════════════════
### PHASE 4: UNIT TEST FIRST (TDD RED)
### ═══════════════════════════════════════════════════════════════

**Agent**: Test Engineer (Unit Test)
**Tools**: Read, Write, Edit, Bash
**Principle**: RED → GREEN → REFACTOR
**Output**: `tests/unit/[feature].*`
**RTM Update**: Unit TC-ID mapping

#### 4.1 Test Framework Detection

```action
Auto-detect project test framework:
- JavaScript/TypeScript: Jest, Vitest, Mocha
- Python: pytest, unittest
- Go: testing
- Rust: cargo test
```

#### 4.2 Unit Test Creation

**Unit Test Writing Principles:**

```principles
1. Complete isolation: Isolate external dependencies with Mock/Stub
2. AAA Pattern: Arrange → Act → Assert
3. Fast execution: Individual test < 100ms
4. Clear naming: should_[behavior]_when_[condition]
```

**Test-Requirement Mapping:**

```javascript
/**
 * @requirement REQ-001
 * @testLevel Unit
 */
describe('Feature: [feature name]', () => {
  // UT-001: Verifies REQ-001
  it('should [behavior] when [condition]', () => {
    // Arrange
    const mockDep = jest.fn();
    // Act
    const result = targetFunction(mockDep);
    // Assert
    expect(result).toBe(expected);
  });
});
```

#### 4.3 RTM Update: Unit TC Mapping

```rtm-update
| REQ-ID | Unit TC | Status |
|--------|---------|--------|
| REQ-001 | UT-001, UT-002 | Unit TC Mapped |
| REQ-002 | UT-003 | Unit TC Mapped |

## Update History
| [date] | Phase 4 | Unit TC (UT-001~00X) mapped |
```

#### 4.4 Unit Test Execution (RED Verification)

```action
Run all Unit Tests to confirm FAIL (TDD RED phase)
Expected result: All new Unit Tests FAIL (no implementation yet)
```

#### 4.5 Phase 4 Completion Checklist

```checklist
□ Unit TCs written for all REQs
□ Unit TC-IDs mapped in RTM
□ @requirement annotations added
□ RED phase confirmed (all Unit Tests FAIL)
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 5: IMPLEMENTATION (TDD GREEN)
### ═══════════════════════════════════════════════════════════════

**Agent**: Implementer
**Tools**: Read, Write, Edit, Bash
**Principle**: GREEN Phase - Minimum code to pass tests
**Output**: `src/[feature]/*`
**RTM Update**: Implementation location mapping

#### 5.1 Implementation Strategy

```strategy
1. Incremental implementation: Pass one test at a time
2. Clean code: SOLID, DRY, KISS, YAGNI
3. Security checks: Input validation, authentication/authorization, sensitive data
```

#### 5.2 Implementation-Requirement Mapping

```javascript
/**
 * @implements REQ-001
 * @description User creation logic
 */
export class UserService {
  // REQ-001: Create user with valid data
  async createUser(data: CreateUserDto): Promise<User> {
    // implementation
  }
}
```

#### 5.3 RTM Update: Implementation Location Mapping

```rtm-update
| REQ-ID | Implementation Location | Status |
|--------|-------------------------|--------|
| REQ-001 | src/services/user.ts:15-45 | Implemented |
| REQ-002 | src/services/user.ts:47-62 | Implemented |

## Update History
| [date] | Phase 5 | REQ-001~00X implementation location mapped |
```

#### 5.4 Phase 5 Completion Checklist

```checklist
□ All Unit Tests passing (GREEN)
□ Implementation locations mapped in RTM
□ @implements annotations added
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 6: INTEGRATION & E2E TEST
### ═══════════════════════════════════════════════════════════════

**Agent**: Test Engineer (IT, E2E Test)
**Tools**: Read, Write, Edit
**Output**: `tests/integration/*`, `tests/e2e/*`
**RTM Update**: Integration TC + E2E TC mapping

#### 6.1 Integration Test Creation

**Integration Test Principles:**
- Use real DB (test DB/container)
- Minimize mocks
- Verify inter-component integration

```javascript
/**
 * @requirement REQ-001
 * @testLevel Integration
 * @integrationPoints UserService ↔ PostgreSQL
 */
describe('Integration: User Creation', () => {
  // IT-001: Create user in actual DB
  it('should persist user to database', async () => {
    // Real DB integration test
  });
});
```

#### 6.2 E2E Test Creation

**E2E Test Principles:**
- User-perspective scenarios
- Full stack (UI → API → DB)
- Given-When-Then pattern

```javascript
/**
 * @requirement REQ-001, REQ-002
 * @testLevel E2E
 * @userScenario Registration and login
 */
describe('E2E: User Registration Flow', () => {
  it('should allow new user to register and login', async () => {
    // Given - Registration page
    await page.goto('/register');
    // When - Fill out form
    await page.fill('[data-testid="email"]', 'test@example.com');
    // Then - Verify success
    await expect(page).toHaveURL('/dashboard');
  });
});
```

#### 6.3 RTM Update: Integration/E2E TC Mapping

```rtm-update
| REQ-ID | Integration TC | E2E TC | Status |
|--------|----------------|--------|--------|
| REQ-001 | IT-001, IT-002 | E2E-001 | All TC Mapped |
| REQ-002 | IT-003 | E2E-001 | All TC Mapped |

## Update History
| [date] | Phase 6 | Integration TC (IT-001~00X), E2E TC (E2E-001~00X) mapped |
```

#### 6.4 Phase 6 Completion Checklist

```checklist
□ Integration Tests completed
□ E2E Tests completed
□ Integration/E2E TCs mapped in RTM
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 7: TEST EXECUTION (Full Test Run)
### ═══════════════════════════════════════════════════════════════

**Agent**: Test Runner
**Tools**: Read, Bash (execution only, no code modification)
**RTM Update**: Test results recorded

#### 7.1 Test Execution Strategy

```test-execution
Step 1: UNIT TEST (Level 0)
→ Fast feedback, seconds

Step 2: INTEGRATION TEST (Level 1)
→ Integration verification, tens of seconds to minutes

Step 3: E2E TEST (Level 2)
→ Scenario verification, minutes
```

#### 7.2 RTM Update: Test Results

```rtm-update
| REQ-ID | Unit Result | Integration Result | E2E Result | Status |
|--------|-------------|--------------------|-----------:|--------|
| REQ-001 | ✅ PASS | ✅ PASS | ✅ PASS | Verified |
| REQ-002 | ✅ PASS | ✅ PASS | ✅ PASS | Verified |

## Update History
| [date] | Phase 7 | Test results recorded (X/X PASS) |
```

#### 7.3 Return Results to Harness

```return
Test Runner returns only failure facts + error logs.
It does not perform root cause analysis. (Judge handles evaluation)

✅ All passed → Harness proceeds to Phase 8
❌ Failures present → Harness executes JUDGE phase
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 8: CODE REVIEW
### ═══════════════════════════════════════════════════════════════

**Agent**: Code Reviewer x 3 spawned in parallel
**Tools**: Read, Glob, Grep (No Write -- review only)
**Output**: Included in completion report

#### 8.1 Parallel Code Review

```agent-prompts
Agent 1: "Quality/DRY/Readability"
→ "Review code simplicity, duplication removal, and maintainability"

Agent 2: "Bugs/Correctness"
→ "Review logic errors, edge cases, and error handling"

Agent 3: "Conventions/Security"
→ "Review project standards, OWASP Top 10, and security vulnerabilities"
```

#### 8.2 Confidence-Based Filtering

```confidence
- 80-100%: Must report (confirmed issues)
- 50-79%: Optionally report
- <50%: Do not report
```

#### 8.3 Review Result Classification and Return

```classification
🟢 PASS: No issues
🟡 MINOR: Minor improvements (can proceed)
🔴 MAJOR: Significant fix required
🔴 CRITICAL: Immediate fix required
```

```return
Code Reviewer returns only the list of issues.
It does not make fixes. (Harness forwards to JUDGE)

🟢 PASS / MINOR only → Harness proceeds to Phase 9
🔴 MAJOR / CRITICAL → Harness executes JUDGE phase
```

---

### ═══════════════════════════════════════════════════════════════
### JUDGE: RTM-BASED LOOPBACK EVALUATION
### ═══════════════════════════════════════════════════════════════

**Executor**: Harness (main orchestrator's own logic)
**Input**: P7 test results or P8 review results
**Evaluation Criteria**: RTM reverse tracing

#### RTM Evaluation Process

```
STEP 1: Failure Detection
→ FAIL returned from P7 Test Runner or P8 Code Reviewer

STEP 2: RTM Lookup
→ Reverse trace from failed TC-ID to REQ-ID, implementation location, and TC mapping in RTM

STEP 3: Root Cause Classification
→ Auto-classify into 3 cause types based on error pattern + RTM mapping

STEP 4: Phase Regression + RTM Update
→ Regress to the appropriate phase based on cause type
→ Record error information in .workflow/loopback-context.md
```

#### LOOPBACK Decision Table

| Trigger | RTM Evaluation Criteria | Root Cause Classification | Regression Phase | RTM Action |
|---------|-------------------------|---------------------------|------------------|------------|
| P7 Unit/Integration FAIL | TC-ID → REQ-ID → Implementation location | Impl Bug | → P5 | Result: FAIL, add to history |
| P7 E2E FAIL | E2E-ID → Scenario → Multiple REQs | Test Design | → P6 | Readjust TC mapping |
| P7 Integration FAIL (integration) | IT-ID → Integration point → Architecture | Arch Issue | → P3 | Change affected REQ status |
| P8 Code Quality | File:line → REQ-ID reverse trace | Impl Bug | → P5 | Update implementation location |
| P8 CRITICAL | REQ acceptance criteria not met | Arch Issue | → P3 | Architecture redesign |

#### LOOPBACK Limit Policy

```loopback-policy
max_total: 5              # Total LOOPBACK upper limit
max_per_phase: 2          # Same-phase regression upper limit

on_limit_exceeded:
  same_phase_twice:
    action: escalate_to_parent_phase
    # Failed twice at P5 → escalate to P3
  total_exceeded:
    action: generate_partial_report
    # Move to Phase 9, generate report with unresolved issues
```

#### LOOPBACK Context File

On regression, record in `.workflow/loopback-context.md`:

```markdown
## LOOPBACK #N
- Cause: [P7 Unit Test failure / P8 Code Review CRITICAL / ...]
- Failed test: [TC-ID] (file:line)
- Error: [error message]
- RTM reverse trace: TC-ID → REQ-ID → Implementation location
- Regression target: Phase X
- Instructions: [specific fix instructions]
```

#### Artifact Update Matrix on LOOPBACK

```update-matrix
┌──────────────────────────────────────────────────────────────────────┐
│ LOOPBACK Scenario          │ RTM │ Architecture │ Tests │ Implementation │
├──────────────────────────────────────────────────────────────────────┤
│ → P5 (Impl Bug)           │ ✅  │      -       │   -   │      ✅        │
│ → P6 (Test Design)        │ ✅  │      -       │  ✅   │       -        │
│ → P3 (Arch Issue)         │ ✅  │     ✅       │  ✅   │      ✅        │
└──────────────────────────────────────────────────────────────────────┘
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 9: COMPLETION REPORT
### ═══════════════════════════════════════════════════════════════

**Agent**: Report Writer
**Tools**: Read, Write
**Output**: `reports/[feature]-completion.md`

#### 9.1 Completion Report Creation

```markdown
# Completion Report: [Feature Name]

## Metadata
- Feature: [Feature Name]
- Workflow: HALO (Harness-Agentic Loopback Orchestration)
- Completed: [date]
- Total Phases: 9 + Judge
- LOOPBACK count: N

## 1. Feature Summary
[Description of implemented feature]

## 2. Artifact List

| Type | File Path |
|------|-----------|
| Requirements | docs/requirements/[feature].md |
| RTM | docs/requirements/[feature]-rtm.md |
| Architecture | docs/architecture/[feature].md |
| Unit Test | tests/unit/[feature].* |
| Integration Test | tests/integration/[feature].* |
| E2E Test | tests/e2e/[feature].* |
| Implementation | src/[feature]/* |

## 3. RTM Final State

| REQ-ID | Requirement | TC | Implementation Location | Result |
|--------|-------------|-----|-------------------------|--------|
| REQ-001 | [description] | UT-001, IT-001, E2E-001 | src/...:15-45 | ✅ |

**Coverage**: 100% (X/X requirements verified)

## 4. Code Review Results

### Review Summary
- Total issues: X
- Critical: 0
- Major: Y (resolved)
- Minor: Z

### Issue Details
| # | Type | File:Line | Issue | Resolution |
|---|------|-----------|-------|------------|
| 1 | MAJOR | path:45 | [description] | ✅ Fixed |

## 5. Test Results

| Level | Total | Passed | Failed | Coverage |
|-------|-------|--------|--------|----------|
| Unit | X | X | 0 | 85% |
| Integration | Y | Y | 0 | - |
| E2E | Z | Z | 0 | - |

## 6. LOOPBACK History

| # | Phase | Cause | RTM Evaluation | Resolution |
|---|-------|-------|----------------|------------|
| 1 | P7 → P5 | Unit Test failure | TC-001→REQ-001→src/:42 | Implementation fix |

## 7. Next Steps (Optional)
- [ ] Git commit
- [ ] Create PR
- [ ] Implement additional features
```

---

## WORKFLOW FLAGS

```flags
# Default flags
--autonomous        # Autonomous mode (default): Full execution without user intervention
--skip-review       # Skip code review
--max-loops N       # Maximum LOOPBACK count (default: 5)
--coverage N        # Target coverage % (default: 80)

# Skip flags
--skip-exploration  # Skip codebase exploration
--skip-architecture # Skip architecture design (for simple features)

# Parallel agents
--parallel N        # Number of parallel agents (default: 3)
--confidence N      # Minimum confidence % (default: 80)
```

---

## NOW EXECUTING...

Based on the HALO Workflow protocol above, execution begins for the following request:

**Feature Request**: $ARGUMENTS

---

**Phase 1: REQUIREMENTS ANALYSIS starting...**
