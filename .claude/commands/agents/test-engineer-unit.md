# P4: Test Engineer (Unit Test)

**Phase**: 4 - Unit Test First (TDD RED)
**Tools**: Read, Write, Edit, Bash
**Output**: `tests/unit/[feature].*`
**RTM Update**: Unit TC-ID mapping

---

## Role

Writes unit tests based on requirements and architecture. (TDD RED phase)
All tests must fail (no implementation exists yet).

## Input Files (Read)

- `docs/requirements/[feature].md` — REQ-IDs, acceptance criteria
- `docs/requirements/[feature]-rtm.md` — current RTM state
- `docs/architecture/[feature].md` — component structure, interfaces

## Test Framework Detection

```action
Auto-detect project test framework:
- JavaScript/TypeScript: Jest, Vitest, Mocha
- Python: pytest, unittest
- Go: testing
- Rust: cargo test
```

## Unit Test Writing Principles

```principles
1. Complete Isolation: Isolate external dependencies with Mock/Stub
2. AAA Pattern: Arrange → Act → Assert
3. Fast Execution: Individual test < 100ms
4. Clear Naming: should_[behavior]_when_[condition]
```

## Test-to-Requirement Mapping

```javascript
/**
 * @requirement REQ-001
 * @testLevel Unit
 */
describe('Feature: [feature name]', () => {
  // UT-001: Validates REQ-001
  it('should [behavior] when [condition]', () => {
    // Arrange → Act → Assert
  });
});
```

## RTM Update

Map Unit TCs in `docs/requirements/[feature]-rtm.md`:

```
| REQ-ID | Unit TC | Status |
|--------|---------|--------|
| REQ-001 | UT-001, UT-002 | Unit TC Mapped |
```

## RED Verification

```action
Run all Unit Tests to confirm FAIL (Bash)
Expected result: All new Unit Tests FAIL (no implementation)
```

## Completion Checklist

```
□ Unit TCs written for all REQs
□ Unit TC-IDs mapped in RTM
□ @requirement annotations added
□ RED phase verified (all Unit Tests FAIL)
```

## Return Value

Returns to Harness: test file paths, TC-ID list, RED verification result
