# P2: Code Explorer

**Phase**: 2 - Codebase Exploration
**Tools**: Read, Glob, Grep (Write not allowed)
**Parallel**: 2-3 agents spawned concurrently
**Output**: None (results returned to Harness as text)

---

## Role

Explores the existing codebase to identify patterns, conventions, and architectural decisions.
Does not modify any code.

## Parallel Agent Prompts

### Agent 1: Similar Feature Discovery
```
"Find existing features similar to [requested feature] and analyze implementation patterns.
Identify file structure, naming conventions, and data flow patterns."
```

### Agent 2: Architecture Mapping
```
"Map the architecture and abstractions of [related area].
Identify layer structure, dependency direction, and entry points."
```

### Agent 3: Pattern Analysis (Optional)
```
"Identify UI patterns, testing approaches, and extension points.
Analyze existing test framework configuration and component patterns."
```

## Result Merging (Performed by Harness)

```
1. Collect key file lists returned by each agent
2. Remove duplicates
3. Summarize patterns/conventions/architectural decisions
```

## Return Value

Returns to Harness: key file list, pattern summary, technology stack information
