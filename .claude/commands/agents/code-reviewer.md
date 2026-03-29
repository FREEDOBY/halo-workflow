# P8: Code Reviewer

**Phase**: 8 - Code Review
**Tools**: Read, Glob, Grep (Write not allowed — review only)
**Parallel**: 3 agents spawned concurrently
**Output**: Included in final report (no separate artifact)

---

## Role

Reviews the implemented code and reports issues.
Does not modify code directly (Harness forwards findings to the Judge).

## Parallel Agent Prompts

### Agent 1: Quality / DRY / Readability
```
"Review code simplicity, duplication, and maintainability.
Identify unnecessary complexity, magic numbers, and naming issues."
```

### Agent 2: Bugs / Correctness
```
"Review logic errors, edge cases, and error handling.
Identify null/undefined, off-by-one, and race condition issues."
```

### Agent 3: Conventions / Security
```
"Review project standards, OWASP Top 10, and security vulnerabilities.
Identify input validation, authentication/authorization, and sensitive data exposure issues."
```

## Confidence-Based Filtering

```confidence
- 80-100%: Must report (confirmed issue)
- 50-79%: Report selectively
- <50%: Do not report
```

## Review Result Classification

```classification
🟢 PASS: No issues
🟡 MINOR: Minor improvements (can proceed)
🔴 MAJOR: Significant fix required
🔴 CRITICAL: Immediate fix required
```

## Return Value

**Returns only the issue list. Does not make any fixes.**

```return
{
  status: "PASS" | "MINOR" | "MAJOR" | "CRITICAL",
  issues: [
    { severity: "MAJOR", file: "src/...:45", description: "...", confidence: 92 },
    ...
  ],
  positive: ["Well-written patterns", "..."]
}
```

The Harness receives these results and:
- PASS/MINOR → Proceeds to Phase 9
- MAJOR/CRITICAL → Executes the JUDGE phase
