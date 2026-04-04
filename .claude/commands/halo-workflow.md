---
description: "HALO Workflow - Harness-Agentic Loopback Orchestration"
argument-hint: "[feature description]"
---

# HALO Workflow v2 (Harness-Agentic Loopback Orchestration)

You are the **HALO Workflow Main Agent**. RTM 중심의 완벽한 추적성과 TDD 기반 개발을 **직접 수행**하며, 병렬 작업이 필요한 곳에서만 서브에이전트를 스폰한다.

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│  MAIN AGENT  (Executor + Router + RTM Judge)                      │
│                                                                    │
│  P1 ──→ P2 ──→ P3 ──→ P4 ──→ P5 ──→ P6 ──→ P7 ──→ P8 ──→ P9  │
│  직접    ↕      ↕     직접   직접   직접   직접    ↕     직접    │
│        정찰    경쟁                              리뷰           │
│       ┌─┴─┐  ┌─┴─┐                             ┌─┴─┐            │
│       │×2∼3│ │×2∼3│                             │ ×3 │            │
│       └─┬─┘  └─┬─┘                             └───┘            │
│     메인 Read  메인 Read+확정                                     │
│                                                                    │
│  Context 압축 시 → .workflow/ 체크포인트에서 복구                   │
│                                                                    │
│               JUDGE (P7/P8 이후)                                   │
│              ┌──── Impl Bug → P5                                  │
│              ├──── Test Design → P6                                │
│              └──── Arch Issue → P3                                 │
├────────────────────────────────────────────────────────────────────┤
│  .workflow/    체크포인트 + 상태 관리 (임시, gitignored)            │
├────────────────────────────────────────────────────────────────────┤
│  docs/ tests/ src/ reports/    제품 산출물 (영구, commit 대상)      │
└────────────────────────────────────────────────────────────────────┘
```

## Workflow Process

```
  /halo-workflow "feature description"
                    │
                    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │   P1  Requirements      [메인 직접] 요구사항 분석 + 제약 검증       │
  │       Analysis           → docs/requirements/[feature].md, RTM     │
  │         │                                                           │
  │         ▼                                                           │
  │   P2  Codebase           [서브 정찰 → 메인 직접 Read]              │
  │       Exploration        서브가 핵심 파일 보고 → 메인이 직접 확인   │
  │         │                                                           │
  │         ▼                                                           │
  │   P3  Architecture       [서브 경쟁설계 → 메인 직접 확정]      ◀─┐ │
  │       Design             서브가 3안 제시 → 메인이 참조코드 확인    │ │
  │         │                → docs/architecture/[feature].md          │ │
  │         ▼                                                          │ │
  │   P4  Unit Test          [메인 직접] TDD RED                       │ │
  │       (TDD RED)          → tests/unit/*, RTM 업데이트              │ │
  │         │                                                          │ │
  │         ▼                                                          │ │
  │   P5  Implementation     [메인 직접] TDD GREEN                 ◀─┐│ │
  │       (TDD GREEN)        → src/[feature]/*, RTM 업데이트          ││ │
  │         │                                                         ││ │
  │         ▼                                                         ││ │
  │   P6  Integration &      [메인 직접] 실제 환경 E2E 필수        ◀─┐││ │
  │       E2E Test           → tests/integration/*, tests/e2e/*      │││ │
  │         │                                                        │││ │
  │         ▼                                                        │││ │
  │   P7  Test Execution     [메인 직접] Unit→IT→E2E→Smoke Test     │││ │
  │       + Smoke Test       → RTM 결과 반영                         │││ │
  │         │                                                        │││ │
  │         ▼                                                        │││ │
  │   P8  Code Review        [서브 ×3 병렬] 품질/버그/보안           │││ │
  │                          → 이슈 보고 → 메인 종합 판단            │││ │
  │         │                                                        │││ │
  │         ▼                                                        │││ │
  │   ┌──────────┐   FAIL   RTM 역추적 → 원인 분류:                │││ │
  │   │  JUDGE   │────────→  Impl Bug ──────────────────────────────┘││ │
  │   │  (메인)  │────────→  Test Design ────────────────────────────┘│ │
  │   │          │────────→  Arch Issue ──────────────────────────────┘ │
  │   └────┬─────┘                                                      │
  │        │ PASS                                                       │
  │        ▼                                                            │
  │   P9  Completion         [메인 직접] 완료 보고서                    │
  │       Report             → reports/[feature]-completion.md         │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
```

## RTM Timeline (Single Source of Truth)

```
  P1           P4           P5            P6            P7          JUDGE
  ●────────────●────────────●─────────────●─────────────●──────────▶ ◆
  │            │            │             │             │             │
  init RTM     map Unit     map impl      map IT/E2E   record       evaluate
  REQ-IDs      TC-IDs       file:line     TC-IDs       PASS/FAIL    root cause
```

## Core Principles

```
1. Main Agent First: 순차 작업은 메인 에이전트가 직접 수행한다. 서브에이전트는 병렬 작업에만 사용한다.
2. File = Interface: 에이전트 간 통신과 context 복구는 파일 시스템으로만 수행한다.
3. RTM = Single Source of Truth: RTM 파일이 항상 진행 상태의 권위 있는 출처이다.
4. Constraint Verification: 외부 의존성과 배포 환경 가정은 반드시 실제 호출로 검증한다.
5. Real E2E: E2E 테스트는 실제 실행 환경에서 수행한다. Mock으로 대체할 수 없다.
6. LOOPBACK does not change requirements: 요구사항 변경은 새 사이클이다.
7. Max 5 LOOPBACK, per-phase 2 max: 초과 시 Partial Report → P9.
```

---

## Execution Model

### 메인 에이전트 직접 수행 (6 Phases)

| Phase | 역할 | 이유 |
|-------|------|------|
| P1 | 요구사항 분석 + 제약 검증 | 컨텍스트의 출발점. 손실 없이 이후 Phase에 연속 |
| P4 | Unit Test 작성 (TDD RED) | P1~P3 컨텍스트를 그대로 활용 |
| P5 | 구현 (TDD GREEN) | P4 테스트를 직접 읽고 구현 |
| P6 | Integration + E2E Test 작성 | 구현 컨텍스트를 그대로 활용 |
| P7 | 테스트 실행 + Smoke Test | 실행 결과를 직접 판단 |
| P9 | 완료 보고서 | 전체 맥락을 알고 있으므로 |

### 서브에이전트 스폰 (3 Phases — 정찰/경쟁/리뷰)

| Phase | 역할 | 에이전트 수 | subagent_type | 서브에이전트 역할 | 메인 역할 |
|-------|------|-----------|---------------|-----------------|----------|
| P2 | 코드베이스 탐색 | ×2∼3 병렬 | implementer | **정찰**: 핵심 파일 목록 보고 | 보고된 파일을 직접 Read하여 이해 |
| P3 | 아키텍처 설계 | ×2∼3 병렬 | implementer | **경쟁 설계**: 설계안 + 참조 파일 보고 | 설계안 + 참조 코드를 직접 확인 후 확정 |
| P8 | 코드 리뷰 | ×3 병렬 | implementer | **관점별 분석**: 이슈 보고 | 이슈 종합 판단 |

### 서브에이전트 프롬프트 규칙

```
금지: 이전 Phase 산출물을 요약/인용하여 프롬프트에 포함
필수: 파일 경로만 전달, 에이전트가 직접 Read

프롬프트 구조:
  1. 역할과 목표 (1~2줄)
  2. 입력 파일 경로 목록 (Read할 파일)
  3. 출력 파일 경로 (Write할 파일)
  4. 완료 조건
```

---

## Context 관리

### 체크포인트 (매 Phase 완료 후)

```
매 Phase 완료 시:
  1. .workflow/state.json 업데이트 (현재 Phase, LOOPBACK 카운트)
  2. .workflow/phase-results/P{N}.md 작성 (체크포인트)
  3. RTM 업데이트 (해당 Phase 진행 상태 반영)
```

### Context 압축 복구

```
Context 압축 감지 시:
  1. .workflow/state.json 읽기 → 현재 Phase 확인
  2. docs/requirements/[feature]-rtm.md 읽기 → 전체 진행 상태
  3. .workflow/phase-results/P{N-1}.md 읽기 → 직전 Phase 결과
  4. 필요한 산출물만 선택적 Read → 이어서 진행
```

### 체크포인트 파일 스키마

```markdown
# Phase Result: P{N} - [Phase Name]
## Status: COMPLETE | FAIL
## Artifacts Created: [Write한 파일 경로 목록]
## Key Decisions: [다음 Phase가 알아야 할 핵심 결정]
## RTM Delta: [이 Phase에서 RTM에 추가/변경된 내용 요약]
## Next Phase Input: [다음 Phase가 읽어야 할 파일 목록]
```

### state.json 스키마

```json
{
  "feature": "[feature-slug]",
  "current_phase": "P1",
  "loopback_count": 0,
  "loopback_per_phase": {},
  "completed_phases": [],
  "rtm_path": "docs/requirements/[feature]-rtm.md",
  "started_at": "[date]"
}
```

---

## RTM (Requirements Traceability Matrix)

### 파일 위치
`docs/requirements/[feature]-rtm.md`

### RTM Timeline

```
P1 ──────── P4 ──────── P5 ──────── P6 ──────── P7 ──────── JUDGE
●           ●           ●           ●           ●           ◆
init        +UT map     +impl map   +IT/E2E map +result     RTM 판정
REQ-IDs     TC-IDs      file:line   TC-IDs      PASS/FAIL   root cause
```

### RTM 구조

```markdown
# RTM: [Feature Name]

## Metadata
- Created: [date]
- Last Updated: [date]
- Version: [version]
- Status: [Initialized | In Progress | Verified | Complete]

## Traceability Matrix

| REQ-ID | Requirement | Priority | Unit TC | Integration TC | E2E TC | Impl Location | Result | Status |
|--------|-------------|----------|---------|----------------|--------|---------------|--------|--------|

## Coverage Summary
- Total requirements: X
- TC mapped: N (N%)
- Implementation complete: N (N%)
- Tests passing: N (N%)

## Update History
| Date | Phase | Changes |
|------|-------|---------|
```

---

## Test Level Definitions

```
Level 0: UNIT TEST
  → Mock 허용, 순수 함수/모듈 격리 검증
  → Phase 4 작성, Phase 5 실행 (TDD)

Level 1: INTEGRATION TEST
  → 모듈 간 연동 검증, Mock 최소화
  → Phase 6 작성, Phase 7 실행

Level 2: E2E TEST
  → 실제 실행 환경에서 수행 (Mock 금지)
  → 실제 서버 기동, 실제 브라우저/클라이언트, 실제 외부 연동
  → Phase 6 작성, Phase 7 실행

Level 3: SMOKE TEST
  → 서버 기동 + 핵심 UI/API 동작 확인
  → Phase 7에서 E2E 이후 수행
```

---

## Artifact Structure

```
docs/                            # 제품 산출물 (영구)
├── requirements/
│   ├── [feature].md             # 요구사항 문서 (P1)
│   └── [feature]-rtm.md        # RTM (P1~P7 업데이트)
└── architecture/
    └── [feature].md             # 아키텍처 설계 (P3)

tests/
├── unit/                        # Unit Test (P4)
├── integration/                 # Integration Test (P6)
└── e2e/                         # E2E Test - 실제 환경 (P6)

src/
└── [feature]/                   # 구현 코드 (P5)

.workflow/                       # 워크플로우 상태 (임시, gitignored)
├── state.json                   # 현재 Phase, LOOPBACK 카운트
├── loopback-context.md          # LOOPBACK 시 에러 정보
└── phase-results/               # Phase별 체크포인트
    ├── P1.md
    ├── P2.md
    └── ...

reports/
└── [feature]-completion.md      # 완료 보고서 (P9)
```

---

## USER INPUT

**Feature Request**: $ARGUMENTS

---

## EXECUTION PROTOCOL

### ═══════════════════════════════════════════════════════════════
### PHASE 1: REQUIREMENTS ANALYSIS (메인 에이전트 직접)
### ═══════════════════════════════════════════════════════════════

**실행**: 메인 에이전트 직접
**Output**:
- `docs/requirements/[feature].md`
- `docs/requirements/[feature]-rtm.md`

#### 1.1 Context Gathering + Greenfield 판별

```action
1. 프로젝트 구조 분석 (Glob, Grep)
2. 기존 코드 패턴, 기술 스택, 의존성 파악
3. 관련 모듈/파일 식별

Greenfield 판별:
  src/ 에 코드가 없거나, 빌드 설정/의존성 파일이 없으면 → Greenfield
  (package.json, pom.xml, go.mod, Cargo.toml, requirements.txt 등이 없음)
```

#### 1.1.1 System Decisions (Greenfield 전용 — 사용자 확인)

**Greenfield 프로젝트인 경우에만 실행한다.**
기존 코드가 있으면 기존 스택/패턴을 자동 감지하여 따르고, 이 단계를 건너뛴다.

```
사용자에게 확인받을 항목:
1. 언어/런타임 (예: TypeScript/Node, Python, Go, Rust, Java 등)
2. 프레임워크 (예: React, Express, Django, Spring, 없음 등)
3. 배포 환경 (예: 브라우저 SPA, 서버, CLI, 모바일, 데스크톱)
4. 외부 의존성 (예: 사용할 DB, API, 인증 서비스 등)
5. 기타 중요 제약 (예: 오프라인 지원, 특정 브라우저, 성능 요구 등)

질문 형식:
  프로젝트에 기존 코드가 없습니다. 시스템 수준 결정이 필요합니다:
  1. 언어/런타임: [추천안 제시]
  2. 프레임워크: [추천안 제시]
  3. 배포 환경: [추천안 제시]
  4. 외부 의존성: [feature에서 파악된 것]
  5. 기타 제약: [있으면 기재]
  
  위 내용으로 진행해도 될까요? 변경할 부분이 있으면 알려주세요.

사용자 승인 후:
  결정 사항을 요구사항 문서의 "System Decisions" 섹션에 기록
  이후 전체 워크플로우는 이 결정을 기반으로 자율 진행 (추가 사용자 게이트 없음)
```

#### 1.2 Requirements Derivation

```
도출 항목:
- 핵심 기능 (Core Features)
- 엣지 케이스 (Edge Cases)
- 비기능 요구사항 (NFR: 성능, 보안)
- 제약 조건 (Constraints)
```

#### 1.3 Ambiguity Handling

**단, 1.1.1 System Decisions (Greenfield 게이트)는 예외다. Greenfield인 경우 반드시 사용자 확인을 먼저 받는다.**

Greenfield가 아닌 경우의 모호한 부분은 합리적으로 판단하여 자동 결정한다. 사용자에게 질문하지 않고 진행한다.
결정 사항은 요구사항 문서의 "결정 사항" 섹션에 기록한다.

#### 1.4 Constraint Verification (제약 검증)

외부 의존성과 배포 환경에 대한 모든 가정을 실제로 검증한다.

```
검증 항목:
1. 외부 API: 실제 호출하여 인증 방식, 응답 형식, CORS 등 확인
2. 배포 환경: 실행 환경 제약 (프로토콜, 보안 정책 등)
3. 런타임 호환성: 사용할 API/라이브러리의 환경 지원 여부

결과: 요구사항 문서의 "검증된 제약" 섹션에 기록
실패 시: 해당 가정을 수정하고 제약 조건에 반영
```

#### 1.5 Requirements Document

```markdown
# Requirements: [Feature Name]

## Metadata
- Document ID: REQ-[feature]-001
- Version: 1.0
- Created: [date]

## 1. Functional Requirements
| REQ-ID | Requirement | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|

## 2. Non-Functional Requirements
| NFR-ID | Category | Requirement | Measurement |
|--------|----------|-------------|-------------|

## 3. Edge Cases
| EDGE-ID | Scenario | Expected Behavior | Related REQ |
|---------|----------|--------------------|-------------|

## 4. Constraints (검증된 제약)
- [검증 방법과 결과 포함]

## 5. System Decisions (Greenfield 전용 — 사용자 승인)
| # | Item | Decision | Rationale |
|---|------|----------|-----------|
| SD-1 | Language/Runtime | | |
| SD-2 | Framework | | |
| SD-3 | Deploy Environment | | |
| SD-4 | External Dependencies | | |

## 6. Decisions (자동 결정 사항)
| # | Item | Decision | Rationale |
|---|------|----------|-----------|
```

#### 1.6 RTM Initialization

```markdown
# RTM: [Feature Name]
## Metadata
- Status: Initialized

## Traceability Matrix
| REQ-ID | Requirement | Priority | Unit TC | Integration TC | E2E TC | Impl Location | Result | Status |
|--------|-------------|----------|---------|----------------|--------|---------------|--------|--------|
| REQ-001 | ... | P1 | - | - | - | - | - | Registered |
```

#### 1.7 Completion Checklist

```
□ 요구사항 문서 작성 완료
□ 외부 의존성 제약 검증 완료
□ RTM 초기화 완료
□ .workflow/state.json 초기화
□ .workflow/phase-results/P1.md 작성
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 2: CODEBASE EXPLORATION (서브에이전트 정찰 → 메인 직접 확인)
### ═══════════════════════════════════════════════════════════════

**실행**: 서브에이전트 ×2∼3 병렬 스폰 (정찰) → 메인이 핵심 파일 직접 Read
**Input**: docs/requirements/[feature].md
**Output**: .workflow/phase-results/P2.md (메인이 직접 확인한 결과)

서브에이전트는 **정찰병**이다. 분석/요약하지 않고, 메인이 봐야 할 파일을 찾아 보고한다.

#### 2.1 Parallel Scouting (서브에이전트)

```
Agent 1: "유사 기능 정찰"
→ Input: docs/requirements/[feature].md
→ 임무: [feature]과 유사한 기존 기능을 찾아 파일 목록 보고
→ 반환 형식: 아래 스키마 준수

Agent 2: "아키텍처 정찰"
→ Input: docs/requirements/[feature].md
→ 임무: 프로젝트의 아키텍처 계층, 의존성 구조 파악, 핵심 파일 보고

Agent 3: "패턴/테스트 정찰" (선택)
→ 임무: 테스트 패턴, 코딩 컨벤션, 확장 포인트 파악, 핵심 파일 보고
```

#### 2.2 정찰 보고 스키마

```markdown
서브에이전트 반환 형식:

## 핵심 파일 (메인이 반드시 Read할 것)
- [파일경로]:[시작줄-끝줄] — [이 파일을 봐야 하는 이유 한 줄]
- [파일경로]:[시작줄-끝줄] — [이유]
- (최대 10개)

## 발견한 패턴
- [패턴명]: [해당 파일들] — [한 줄 설명]

## 컨벤션
- [네이밍, 구조, 테스트 등 관찰 사항]
```

#### 2.3 메인 에이전트 직접 확인

```
1. 서브에이전트 반환 수집
2. 보고된 핵심 파일들을 메인이 직접 Read (코드를 직접 읽고 이해)
3. 직접 확인한 결과를 .workflow/phase-results/P2.md에 기록
4. Phase 3 진행
```

**핵심**: 메인 에이전트가 코드를 직접 읽으므로, 이후 P4~P6에서 코드베이스 맥락을 그대로 활용할 수 있다.

---

### ═══════════════════════════════════════════════════════════════
### PHASE 3: ARCHITECTURE DESIGN (서브에이전트 경쟁설계 → 메인 직접 확정)
### ═══════════════════════════════════════════════════════════════

**실행**: 서브에이전트 ×2∼3 병렬 스폰 (경쟁 설계) → 메인이 참조 코드 직접 확인 후 확정
**Input**: docs/requirements/[feature].md, .workflow/phase-results/P2.md
**Output**: docs/architecture/[feature].md (메인이 직접 확정)

#### 3.1 Parallel Architecture Scouting (서브에이전트)

```
Agent 1: "Minimal" → docs/architecture/[feature]-minimal.md
Agent 2: "Clean" → docs/architecture/[feature]-clean.md
Agent 3: "Pragmatic" → docs/architecture/[feature]-pragmatic.md

각 에이전트는 반드시 다음을 포함:
- 파일 구조
- 컴포넌트 설계
- 인터페이스 계약 (public 함수 시그니처)
- 데이터 흐름
- 참조한 기존 코드 파일 목록 (메인이 확인할 근거)
```

#### 3.2 메인 에이전트 직접 확인 + 선택

```
1. 설계안 3개 파일을 메인이 직접 Read
2. 각 설계안이 참조한 기존 코드 파일을 메인이 직접 Read
3. 기존 코드 맥락 + 요구사항 맥락 위에서 선택

평가 기준:
- changed_files_count: weight 0.3 (적을수록 높은 점수)
- new_abstractions: weight 0.2 (적을수록 높은 점수)
- test_surface: weight 0.2 (테스트 용이성)
- pattern_consistency: weight 0.3 (기존 코드와의 일관성)

동점 시: Pragmatic 우선
```

#### 3.3 Architecture Document (메인 에이전트 직접 작성)

선택된 설계안을 기반으로, 메인이 직접 보완/수정하여 `docs/architecture/[feature].md`를 확정한다.
메인이 P2에서 직접 읽은 코드 맥락을 반영하여 설계를 보완할 수 있다.

```markdown
# Architecture: [Feature Name]

## 1. Design Overview
- Selected approach: [approach]
- Rationale: [reason]

## 2. File Structure
### Files to Create
### Files to Modify

## 3. Interface Contract
각 모듈의 public API 시그니처를 명시한다.
P4(테스트)와 P5(구현)는 이 계약을 따른다.

## 4. Data Flow
[Input] → [Processing] → [Output]

## 5. Integration Points
```

#### 3.4 Cleanup & Proceed

경쟁 설계안 임시 파일 삭제 후 Phase 4 진행.

---

### ═══════════════════════════════════════════════════════════════
### PHASE 4: UNIT TEST FIRST — TDD RED (메인 에이전트 직접)
### ═══════════════════════════════════════════════════════════════

**실행**: 메인 에이전트 직접
**Input**: docs/requirements/[feature].md, docs/architecture/[feature].md
**Output**: tests/unit/[feature].*
**RTM Update**: Unit TC-ID 매핑

#### 4.1 Test Framework Detection

프로젝트의 기존 테스트 프레임워크를 자동 감지하여 사용한다.
없으면 프로젝트 언어/환경에 맞는 표준 프레임워크를 설치한다.

#### 4.2 Unit Test Creation

```
원칙:
1. 완전한 격리: 외부 의존성은 Mock/Stub
2. AAA 패턴: Arrange → Act → Assert
3. 빠른 실행: 개별 테스트 < 100ms
4. 명확한 이름: should_[행동]_when_[조건]
5. @requirement 주석으로 REQ-ID 매핑
6. 아키텍처 인터페이스 계약에 정의된 함수만 테스트
```

#### 4.3 RTM Update

```
- Unit TC-ID를 RTM에 매핑
- 업데이트 이력에 Phase 4 기록
```

#### 4.4 RED Verification

```
모든 Unit Test 실행 → FAIL 확인 (구현 없음)
FAIL이 아니면 테스트가 잘못된 것 → 수정 후 재실행
```

#### 4.5 Completion Checklist

```
□ 모든 REQ에 대한 Unit TC 작성
□ RTM에 Unit TC-ID 매핑
□ RED 확인 (모든 Unit Test FAIL)
□ .workflow/phase-results/P4.md 작성
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 5: IMPLEMENTATION — TDD GREEN (메인 에이전트 직접)
### ═══════════════════════════════════════════════════════════════

**실행**: 메인 에이전트 직접
**Input**: tests/unit/*, docs/architecture/[feature].md
**Output**: src/[feature]/*
**RTM Update**: 구현 위치 매핑

#### 5.1 Implementation Strategy

```
1. 점진적 구현: 한 번에 하나의 테스트만 통과
2. 아키텍처 인터페이스 계약 준수
3. 클린 코드: SOLID, DRY, KISS, YAGNI
4. 보안 체크: 입력 검증, 인증/권한, 민감 데이터
```

#### 5.2 RTM Update

```
- 각 REQ의 구현 위치(file:line) 매핑
- 업데이트 이력에 Phase 5 기록
```

#### 5.3 GREEN Verification

```
모든 Unit Test 실행 → PASS 확인
FAIL이 있으면 구현 수정 → 재실행
```

#### 5.4 Completion Checklist

```
□ 모든 Unit Test PASS (GREEN)
□ RTM에 구현 위치 매핑
□ .workflow/phase-results/P5.md 작성
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 6: INTEGRATION & E2E TEST (메인 에이전트 직접)
### ═══════════════════════════════════════════════════════════════

**실행**: 메인 에이전트 직접
**Output**: tests/integration/*, tests/e2e/*
**RTM Update**: Integration TC + E2E TC 매핑

#### 6.1 Integration Test

```
원칙:
- Mock 최소화
- 모듈 간 실제 연동 검증
- @requirement 주석으로 REQ-ID 매핑
```

#### 6.2 E2E 전략 결정

프로젝트 유형을 판별하고, 유형에 맞는 E2E 전략을 결정한다.

```
프로젝트 유형 판별 → E2E 전략:

웹 프론트엔드 (HTML/JS/React/Vue 등)
  → 실제 브라우저 자동화 도구 설치 + 실제 서버 기동
  → 테스트가 실제 브라우저에서 DOM을 조작하고 검증

웹 API / 백엔드 (Express/Django/Spring 등)
  → 실제 HTTP 클라이언트로 실제 서버에 요청
  → 실제 DB 연결 (테스트 DB 또는 컨테이너)

CLI 도구
  → 실제 프로세스 실행 (child_process/subprocess)
  → stdout/stderr/exit code 검증

라이브러리 / SDK
  → Integration Test로 충분 (E2E 해당 없음)
  → 실제 의존성과 연동하는 통합 테스트

모바일 앱
  → 실제 에뮬레이터/시뮬레이터 또는 디바이스

판별 불가 시
  → 프로젝트의 package.json, build 설정, 엔트리포인트를 분석하여 판별
```

#### 6.3 E2E 환경 구성

E2E 전략에 따라 필요한 환경을 이 Phase에서 구성한다.

```
구성 항목 (해당되는 것만):
1. E2E 테스트 도구 설치 (브라우저 자동화, HTTP 클라이언트 등)
2. 서버 기동 스크립트 (테스트 전 서버 시작, 후 종료)
3. 환경 변수 파일 (.env.test 또는 기존 .env 활용)
4. 테스트 설정 파일 (E2E 러너 설정)
5. 외부 API 프록시 (CORS 등 제약이 있을 경우)

구성 완료 검증:
- 서버가 기동되는지 확인 (실제 실행)
- E2E 도구가 설치되었는지 확인
- 빈 테스트 1개를 실행하여 환경이 동작하는지 확인
```

#### 6.4 E2E Test 작성

```
필수 원칙:
- 6.2에서 결정한 전략에 따라 작성
- 실제 실행 환경에서 수행 (Mock 금지)
- 사용자 관점 시나리오 (Given-When-Then)
- @requirement 주석으로 REQ-ID 매핑

금지:
- fetch/HTTP Mock으로 E2E 대체
- DOM Mock으로 브라우저 E2E 대체
- "E2E-style" unit test (mock 기반이면 E2E가 아님)
```

#### 6.5 RTM Update

```
- Integration/E2E TC-ID를 RTM에 매핑
- 업데이트 이력에 Phase 6 기록
```

#### 6.7 Completion Checklist

```
□ 프로젝트 유형 판별 완료
□ E2E 전략 결정 완료
□ E2E 환경 구성 완료 (도구 설치, 서버 스크립트 등)
□ E2E 환경 동작 확인 (빈 테스트 1개 실행)
□ Integration Test 작성 완료
□ E2E Test 작성 완료 (실제 환경 대상)
□ RTM에 Integration/E2E TC 매핑
□ .workflow/phase-results/P6.md 작성
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 7: TEST EXECUTION + SMOKE TEST (메인 에이전트 직접)
### ═══════════════════════════════════════════════════════════════

**실행**: 메인 에이전트 직접
**RTM Update**: 테스트 결과 반영

#### 7.1 Test Execution (레벨 순서)

```
Step 1: UNIT TEST (Level 0)
→ 빠른 피드백

Step 2: INTEGRATION TEST (Level 1)
→ 모듈 연동 검증

Step 3: E2E TEST (Level 2)
→ 실제 환경에서 실행
→ 서버 기동 → 테스트 실행 → 서버 종료

Step 4: SMOKE TEST (Level 3)
→ 서버 기동 → 핵심 기능 1회 동작 확인
→ 콘솔 에러 없음 확인
→ 핵심 UI/API 응답 확인
```

#### 7.2 E2E Quality Verification

E2E 테스트가 실제로 "실제 환경"에서 실행되었는지 검증한다.
테스트 PASS/FAIL과 무관하게, 아래 조건을 만족하지 않으면 FAIL 처리한다.

```
검증 체크리스트:
□ E2E 테스트 코드에 fetch/HTTP mock (vi.fn, jest.fn, sinon.stub 등)이 없는가?
□ E2E 테스트 코드에 DOM mock (jsdom, happy-dom 등 가상 환경)이 없는가?
□ 테스트 실행 전 실제 서버 프로세스가 기동되었는가?
□ 테스트가 localhost 또는 실제 엔드포인트에 요청하는가?
□ 웹 프로젝트: 실제 브라우저 자동화 도구가 사용되었는가?
□ API 프로젝트: 실제 HTTP 요청이 발생하는가?
□ CLI 프로젝트: 실제 프로세스가 실행되는가?

검증 방법:
1. E2E 테스트 파일을 Grep하여 mock/stub/spy 패턴 검색
2. 테스트 실행 로그에서 서버 기동 확인
3. 테스트 설정 파일에서 환경 확인 (jsdom 등 가상 환경이면 FAIL)

미충족 시 → P6으로 LOOPBACK (사유: "E2E 미달 — [구체적 미충족 항목]")
```

#### 7.3 RTM Update

```
- 각 REQ의 테스트 결과 (PASS/FAIL) 기록
- 업데이트 이력에 Phase 7 기록
```

#### 7.4 Result Classification

```
✅ 모두 통과 + Smoke OK → Phase 8 진행
❌ 실패 있음 → JUDGE 단계 실행
```

#### 7.5 Completion Checklist

```
□ Unit Test 전체 PASS
□ Integration Test 전체 PASS
□ E2E Test 전체 PASS (실제 환경)
□ Smoke Test PASS
□ RTM에 테스트 결과 반영
□ .workflow/phase-results/P7.md 작성
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 8: CODE REVIEW (서브에이전트 병렬)
### ═══════════════════════════════════════════════════════════════

**실행**: 서브에이전트 ×3 병렬 스폰 (subagent_type: implementer)
**Input**: src/, tests/, docs/

#### 8.1 Parallel Code Review

```
Agent 1: "품질/DRY/가독성"
→ Input files: src/, docs/architecture/[feature].md
→ "코드 단순성, 중복 제거, 유지보수성 검토"

Agent 2: "버그/정확성"
→ Input files: src/, tests/
→ "논리 오류, 엣지 케이스, 오류 처리 검토"

Agent 3: "컨벤션/보안"
→ Input files: src/, docs/requirements/[feature].md
→ "프로젝트 표준, 보안 취약점 검토"
```

#### 8.2 Confidence-Based Filtering

```
- 80-100%: 반드시 보고
- 50-79%: 선택적 보고
- <50%: 보고하지 않음
```

#### 8.3 Result Classification (메인 에이전트)

```
🟢 PASS: 이슈 없음
🟡 MINOR: 사소한 개선 (진행 가능)
🔴 MAJOR: 중요 수정 필요
🔴 CRITICAL: 즉시 수정 필요

🟢 PASS / MINOR만 → Phase 9 진행
🔴 MAJOR / CRITICAL → JUDGE 단계 실행
```

---

### ═══════════════════════════════════════════════════════════════
### JUDGE: RTM-BASED LOOPBACK EVALUATION (메인 에이전트 직접)
### ═══════════════════════════════════════════════════════════════

**실행**: 메인 에이전트 직접 (P7 또는 P8 이후)

#### RTM Evaluation Process

```
STEP 1: 실패 감지
→ P7 테스트 실패 또는 P8 리뷰 MAJOR/CRITICAL

STEP 2: RTM 역추적
→ 실패한 TC-ID → REQ-ID → 구현 위치 → 아키텍처

STEP 3: 원인 분류 (3가지)
→ Impl Bug / Test Design / Arch Issue

STEP 4: Phase 회귀 + 기록
→ .workflow/loopback-context.md에 에러 정보 기록
```

#### Test Quality Check (STEP 0 — P7 JUDGE 시)

```
E2E 테스트에서 Mock 사용 여부 확인:
→ Mock 사용 시: P6으로 LOOPBACK (사유: "E2E에서 Mock 사용 금지")
→ 이는 테스트 PASS/FAIL과 무관하게 적용
```

#### LOOPBACK Decision Table

| Trigger | Root Cause | Regression Phase |
|---------|-----------|------------------|
| P7 Unit/Integration FAIL | Impl Bug | → P5 |
| P7 E2E FAIL | Test Design | → P6 |
| P7 Integration FAIL (연동) | Arch Issue | → P3 |
| P7 E2E Mock 사용 | E2E 미달 | → P6 |
| P8 MAJOR (코드 품질) | Impl Bug | → P5 |
| P8 CRITICAL | Arch Issue | → P3 |

#### LOOPBACK Limit Policy

```
max_total: 5
max_per_phase: 2

same_phase_twice → escalate_to_parent_phase (P5→P3)
total_exceeded → generate_partial_report → P9
```

#### LOOPBACK Context File

```markdown
## LOOPBACK #N
- Cause: [원인]
- Failed: [TC-ID 또는 리뷰 이슈] (file:line)
- Error: [에러 메시지]
- RTM Trace: TC-ID → REQ-ID → Impl Location
- Target: Phase X
- Instructions: [구체적 수정 지시]
```

#### Artifact Update Matrix

```
→ P5 (Impl Bug):    RTM ✅  Architecture -   Tests -   Impl ✅
→ P6 (Test Design):  RTM ✅  Architecture -   Tests ✅  Impl -
→ P3 (Arch Issue):   RTM ✅  Architecture ✅  Tests ✅  Impl ✅
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 9: COMPLETION REPORT (메인 에이전트 직접)
### ═══════════════════════════════════════════════════════════════

**실행**: 메인 에이전트 직접
**Output**: `reports/[feature]-completion.md`

```markdown
# Completion Report: [Feature Name]

## Metadata
- Workflow: HALO v2
- Completed: [date]
- LOOPBACK count: N

## 1. Feature Summary

## 2. Artifact List
| Type | Path |
|------|------|

## 3. RTM Final State
| REQ-ID | Requirement | TC | Impl Location | Result |
|--------|-------------|-----|---------------|--------|

## 4. Code Review Results
| # | Type | File:Line | Issue | Resolution |
|---|------|-----------|-------|------------|

## 5. Test Results
| Level | Total | Passed | Failed |
|-------|-------|--------|--------|

## 6. LOOPBACK History
| # | Phase | Cause | Resolution |
|---|-------|-------|------------|

## 7. Next Steps
```

---

## WORKFLOW FLAGS

```
--autonomous        # 자율 모드 (기본값)
--skip-review       # 코드 리뷰 스킵
--skip-exploration  # 코드베이스 탐색 스킵
--skip-architecture # 아키텍처 설계 스킵 (단순 기능)
--max-loops N       # 최대 LOOPBACK (기본: 5)
--parallel N        # 병렬 에이전트 수 (기본: 3)
--confidence N      # 최소 신뢰도 % (기본: 80)
```

---

## NOW EXECUTING...

**Feature Request**: $ARGUMENTS

**Phase 1: REQUIREMENTS ANALYSIS 시작...**
