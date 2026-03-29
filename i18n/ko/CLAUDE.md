# HALO Workflow Project

## Usage
```
/halo-workflow [feature description]
```

## Core Principles
- **RTM is Single Source of Truth** — `docs/requirements/*-rtm.md`
- **File = Agent Interface** — 에이전트 간 통신은 파일 시스템으로만
- **LOOPBACK은 요구사항을 바꾸지 않음** — P1 회귀 없음 (요구사항 변경 = 새 사이클)
- **Max 5 LOOPBACK, per-phase 2회** — 초과 시 Partial Report 생성

## 3-Layer Architecture
1. **Harness** — 메인 오케스트레이터, 상태 머신, RTM Judge
2. **AI Agents** — Phase별 격리 서브에이전트, 도구 제한
3. **Artifacts** — 파일 시스템 (docs/, tests/, src/, reports/)

## Agent Definitions
`.claude/commands/agents/` 폴더에 Phase별 에이전트가 정의되어 있습니다.
메인 오케스트레이터가 Phase 진입 시 해당 에이전트 프롬프트를 로드합니다.
