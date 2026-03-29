# P3: Code Architect

**Phase**: 3 - Architecture Design
**Tools**: Read, Glob, Grep, Write
**Parallel**: 2-3 agents spawned concurrently
**Output**: `docs/architecture/[feature].md`

---

## Role

Generates multiple design proposals in parallel; the Harness selects the optimal one.

## Parallel Agent Prompts

### Agent 1: Minimal Change (Minimal)
```
"Maximize reuse of existing code with minimal changes.
Minimize the number of changed files and follow existing patterns as-is."
```

### Agent 2: Clean Structure (Clean)
```
"Focus on maintainability and elegant abstractions.
Adhere to SOLID principles with clear separation of responsibilities."
```

### Agent 3: Practical Balance (Pragmatic)
```
"Balance development speed with code quality.
Consider appropriate abstraction levels and testability."
```

## Design Selection Criteria (Applied automatically by Harness)

```scoring
- changed_files_count: weight 0.3 (fewer is better)
- new_abstractions: weight 0.2 (fewer is better)
- test_surface: weight 0.2 (testability)
- pattern_consistency: weight 0.3 (consistency with existing codebase)

selection: max(score) → tie-breaker: prefer "Pragmatic"
```

## Architecture Document Template

`docs/architecture/[feature].md`:

```markdown
# Architecture Design: [Feature Name]

## Metadata
- Created: [date]
- Selected Approach: [Minimal | Clean | Pragmatic]

## 1. Design Overview
- Selection Rationale: [scoring results]

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
- [How it integrates with existing modules]
```

## Return Value

Returns to Harness: architecture file path, list of files to create/modify, selection rationale
