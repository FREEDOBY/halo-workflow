# P9: Report Writer

**Phase**: 9 - Completion Report
**Tools**: Read, Write
**Output**: `reports/[feature]-completion.md`

---

## Role

Consolidates artifacts from all phases into a completion report.

## Input Files (Read)

- `docs/requirements/[feature].md` — requirements
- `docs/requirements/[feature]-rtm.md` — final RTM state
- `docs/architecture/[feature].md` — architecture
- `tests/unit/[feature].*` — test code
- `src/[feature]/*` — implementation code
- `.workflow/loopback-context.md` — LOOPBACK history (if applicable)

## Completion Report Template

`reports/[feature]-completion.md`:

```markdown
# Completion Report: [Feature Name]

## Metadata
- Feature: [Feature Name]
- Workflow: HALO (Harness-Agentic Loopback Orchestration)
- Completed: [date]
- Total Phases: 9 + Judge
- LOOPBACK Count: N

## 1. Feature Summary
[Description of the implemented feature]

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

## 3. Final RTM State

| REQ-ID | Requirement | TC | Implementation Location | Result |
|--------|-------------|-----|-------------------------|--------|
| REQ-001 | [description] | UT-001, IT-001, E2E-001 | src/...:15-45 | ✅ |

**Coverage**: 100% (X/X requirements verified)

## 4. Code Review Results

### Review Summary
- Total Issues: X
- Critical: 0
- Major: Y (resolved)
- Minor: Z

### Issue Details
| # | Severity | File:Line | Issue | Resolution |
|---|----------|-----------|-------|------------|
| 1 | MAJOR | path:45 | [description] | ✅ Fixed |

## 5. Test Results

| Level | Total | Passed | Failed | Coverage |
|-------|-------|--------|--------|----------|
| Unit | X | X | 0 | 85% |
| Integration | Y | Y | 0 | - |
| E2E | Z | Z | 0 | - |

## 6. LOOPBACK History

| # | Phase | Cause | RTM Judgment | Resolution |
|---|-------|-------|--------------|------------|
| 1 | P7 → P5 | Unit Test failure | TC→REQ→src backtrace | Implementation fix |

## 7. Next Steps (Optional)
- [ ] Git commit
- [ ] Create PR
- [ ] Implement additional features
```

## Return Value

Returns to Harness: report file path, final RTM coverage
