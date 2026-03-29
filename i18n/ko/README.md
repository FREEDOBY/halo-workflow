# HALO Workflow

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
| P1 | Requirements Analyst | 요구사항 분석 + RTM 초기화 |
| P2 | Code Explorer x3 | 코드베이스 탐색 (병렬) |
| P3 | Code Architect x3 | 아키텍처 설계 (병렬) |
| P4 | Test Engineer (Unit) | TDD RED - 단위 테스트 작성 |
| P5 | Implementer | TDD GREEN - 구현 |
| P6 | Test Engineer (IT/E2E) | 통합/E2E 테스트 작성 |
| P7 | Test Runner | 전체 테스트 실행 |
| P8 | Code Reviewer x3 | 코드 리뷰 (병렬) |
| JUDGE | Harness (RTM) | RTM 기반 LOOPBACK 판별 |
| P9 | Report Writer | 완료 보고서 |

## Key Concepts

- **RTM Timeline** — P1/P4/P5/P6/P7에서 누적 업데이트, Judge가 판정에 활용
- **LOOPBACK** — 요구사항은 불변, 3가지 회귀 경로 (P3/P5/P6)
- **Context Isolation** — 서브에이전트는 독립 컨텍스트, 파일로만 통신
- **Tool Restriction** — Phase별 허용 도구가 다름 (탐색 에이전트는 Write 불가)

## License

MIT
