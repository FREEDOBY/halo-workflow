# HALO Workflow Project

## Usage
```
/halo-workflow [feature description]
```

## Core Principles
- **RTM = Single Source of Truth** — 매 Phase가 RTM 업데이트. JUDGE는 RTM만 읽고 판별.
- **Main Agent First** — P1~P7 메인 연속 실행. 서브는 P8(리뷰)과 JUDGE(판별)에만.
- **File = Interface** — 에이전트 간 통신과 context 복구는 파일로만.
- **Constraint Verification** — 외부 의존성은 실제 호출로 검증.
- **Real E2E** — E2E는 실제 환경. Mock 금지.
- **LOOPBACK never changes requirements** — 요구사항 변경 = 새 사이클.
- **Max 5 LOOPBACK, per-phase 2 max** — 초과 시 Partial Report → P9.

## Execution Model
- **Main direct** (8 Phases): P1→P2→P3→P4→P5→P6→P7→P9 — 컨텍스트 단절 0
- **Sub-agents** (2 points): P8 review (×3), JUDGE (×1 — RTM만 읽고 판별)

## RTM Flow
P1(REQ등록) → P4(Unit TC매핑) → P5(구현위치매핑) → P6(IT/E2E TC매핑) → P7(결과기록) → P8(리뷰반영) → JUDGE(RTM읽고 판별)

## Agent Definitions
Sub-agent definition (P8 reviewer) is in `.claude/commands/agents/`.
