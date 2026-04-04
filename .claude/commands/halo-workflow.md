---
description: "HALO Workflow - Harness-Agentic Loopback Orchestration"
argument-hint: "[feature description]"
---

# HALO Workflow v3 (Harness-Agentic Loopback Orchestration)

You are the **HALO Workflow Main Agent**. RTM 중심의 완벽한 추적성과 TDD 기반 개발을 **직접 수행**하며, P8(리뷰)과 JUDGE(판별)에서만 서브에이전트를 사용한다.

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│  MAIN AGENT  (Executor + Router)                                   │
│                                                                    │
│  P1 ──→ P2 ──→ P3 ──→ P4 ──→ P5 ──→ P6 ──→ P7 ──→ P8 ──→ P9  │
│  직접   직접   직접   직접   직접   직접   직접    ↕     직접    │
│  ─────────── 메인 연속 실행 (컨텍스트 단절 0) ──    │              │
│                                                   리뷰  JUDGE    │
│                                                  ┌─┴─┐  ┌───┐    │
│                                                  │ ×3 │  │ ×1│    │
│                                                  └───┘  └─┬─┘    │
│                                                           │       │
│               JUDGE 판별 결과에 따라:                       │       │
│              ┌──── Test Bug → P4 ─────────────────────────┘       │
│              ├──── Impl Bug → P5                                  │
│              ├──── Test Design → P6                                │
│              └──── Arch Issue → P3                                 │
│                                                                    │
│  Context 압축 시 → .workflow/phase-results/ 체크포인트에서 복구     │
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
  ┌───────────────────────────────────────────────────────────────────┐
  │                                                                   │
  │   P1  Requirements      [메인 직접] 요구사항 + 제약 검증          │
  │       Analysis           → RTM 초기화 (REQ-ID 등록)              │
  │         │                  Greenfield → 사용자에게 기술 스택 확인 │
  │         ▼                                                         │
  │   P2  Codebase           [메인 직접] Glob/Grep/Read              │
  │       Exploration        Greenfield → 자동 스킵                  │
  │         │                                                         │
  │         ▼                                                         │
  │   P3  Architecture       [메인 직접] 설계                    ◀──┐│
  │       Design             → docs/architecture/[feature].md       ││
  │         │                                                       ││
  │         ▼                                                       ││
  │   P4  Unit Test          [메인 직접] TDD RED                ◀─┐││
  │       (TDD RED)          → RTM에 Unit TC-ID 매핑              │││
  │         │                                                     │││
  │         ▼                                                     │││
  │   P5  Implementation     [메인 직접] TDD GREEN             ◀┐│││
  │       (TDD GREEN)        → RTM에 구현 위치 매핑             ││││
  │         │                                                   ││││
  │         ▼                                                   ││││
  │   P6  Integration &      [메인 직접] 실제 환경 E2E        ◀┐││││
  │       E2E Test           → RTM에 IT/E2E TC-ID 매핑        │││││
  │         │                                                  │││││
  │         ▼                                                  │││││
  │   P7  Test Execution     [메인 직접] Unit→IT→E2E→Smoke    │││││
  │                          → RTM에 결과(PASS/FAIL) 기록     │││││
  │         │                                                  │││││
  │         │  ANY FAIL → 즉시 JUDGE (P8 스킵)                │││││
  │         │  ALL PASS ↓                                      │││││
  │         ▼                                                  │││││
  │   P8  Code Review        [서브 ×3] 품질/버그/보안          │││││
  │                          → 메인이 이슈를 RTM에 반영        │││││
  │         │                                                  │││││
  │         ▼                                                  │││││
  │   ┌──────────┐  FAIL    JUDGE [서브 ×1] RTM만 Read:       │││││
  │   │  JUDGE   │───────→   Test Design ─────────────────────┘││││
  │   │  (서브)  │───────→   Test Bug ─────────────────────────┘│││
  │   │          │───────→   Impl Bug ──────────────────────────┘││
  │   │          │───────→   Arch Issue ─────────────────────────┘│
  │   └────┬─────┘                                                │
  │        │ PASS                                                 │
  │        ▼                                                      │
  │   P9  Completion         [메인 직접] 완료 보고서              │
  │       Report             → reports/[feature]-completion.md    │
  │                                                                │
  │   ※ 매 Phase 완료 시 체크포인트 + RTM 업데이트 반드시 수행    │
  └────────────────────────────────────────────────────────────────┘
```

## RTM = Single Source of Truth

RTM은 워크플로우 전체의 유일한 진실이다. 각 Phase가 RTM을 업데이트하고, JUDGE는 RTM만 읽고 판별한다.

```
  P1           P4           P5            P6            P7       P8       JUDGE
  ●────────────●────────────●─────────────●─────────────●────────●────────▶ ◆
  │            │            │             │             │        │          │
  init RTM     +Unit TC     +impl loc     +IT/E2E TC   +result  +review   RTM만
  REQ-IDs      매핑          file:line     매핑          PASS/   이슈      Read
                                                        FAIL    반영      → 판별
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

| REQ-ID | Requirement | Priority | Unit TC | Integration TC | E2E TC | Impl Location | Result | Review | Status |
|--------|-------------|----------|---------|----------------|--------|---------------|--------|--------|--------|

## Coverage Summary
- Total requirements: X
- TC mapped: N (N%)
- Implementation complete: N (N%)
- Tests passing: N (N%)

## Update History
| Date | Phase | Changes |
|------|-------|---------|
```

**RTM 컬럼 설명:**
- `Result`: P7에서 기록. PASS / FAIL / - (미실행)
- `Review`: P8에서 기록. PASS / MINOR / MAJOR / CRITICAL / - (미리뷰)
- `Status`: Registered → Unit TC Mapped → Implemented → All TC Mapped → Verified → Complete

---

## Core Principles

```
1. Main Agent First: P1~P7은 메인이 직접 수행. 서브는 P8(리뷰)과 JUDGE(판별)에만.
2. RTM = Single Source of Truth: 모든 Phase가 RTM을 업데이트. JUDGE는 RTM만 읽고 판별.
3. File = Interface: 에이전트 간 통신과 context 복구는 파일 시스템으로만.
4. Constraint Verification: 외부 의존성 가정은 반드시 실제 호출로 검증.
5. Real E2E: E2E 테스트는 실제 실행 환경. Mock 금지.
6. LOOPBACK does not change requirements: 요구사항 변경은 새 사이클.
7. Max 5 LOOPBACK, per-phase 2 max: 초과 시 Partial Report → P9.
```

---

## Execution Model

### 메인 에이전트 직접 수행 (8 Phases)

| Phase | 역할 | RTM 업데이트 |
|-------|------|-------------|
| P1 | 요구사항 분석 + 제약 검증 | RTM 초기화 (REQ-ID 등록) |
| P2 | 코드베이스 탐색 | - (Greenfield 시 스킵) |
| P3 | 아키텍처 설계 | - |
| P4 | Unit Test 작성 (TDD RED) | Unit TC-ID 매핑 |
| P5 | 구현 (TDD GREEN) | 구현 위치(file:line) 매핑 |
| P6 | Integration + E2E Test | IT/E2E TC-ID 매핑 |
| P7 | 테스트 실행 + Smoke Test | 결과(PASS/FAIL) 기록 |
| P9 | 완료 보고서 | Status → Complete |

**P1→P7 메인 연속 실행. 컨텍스트 단절 0.**

### 서브에이전트 (2개)

| Phase | 역할 | Input | Output |
|-------|------|-------|--------|
| P8 | 코드 리뷰 ×3 병렬 | src/, tests/, docs/ | 이슈 메시지 → 메인이 RTM에 반영 |
| JUDGE | RTM 판별 ×1 | RTM 파일 하나 | 판별 메시지 → 메인이 LOOPBACK 실행 |

### 서브에이전트 프롬프트 규칙

```
금지: 이전 Phase 산출물을 요약/인용하여 프롬프트에 포함
필수: 파일 경로만 전달, 에이전트가 직접 Read
```

---

## Context 관리

### 체크포인트 (매 Phase 완료 후 — 반드시 실행)

**이것은 선택이 아니다. 각 Phase의 마지막 행동은 반드시 체크포인트 Write이다.**

```
매 Phase 완료 시:
  1. .workflow/state.json 업데이트 (current_phase, completed_phases)
  2. .workflow/phase-results/P{N}.md 작성 (아래 스키마)
  3. RTM 업데이트 (해당 Phase 진행 상태)
```

### 체크포인트 스키마

```markdown
# Phase Result: P{N} - [Phase Name]

## Status
COMPLETE | FAIL | SKIPPED

## Artifacts
- [파일 경로 목록]

## Key Decisions
- [판단과 근거]

## Context Snapshot
- [컨텍스트 압축 후 이 섹션만 읽으면 이어갈 수 있어야 함]

## RTM Delta
- [이 Phase에서 RTM에 추가/변경된 내용]

## Next Phase Input
- [다음 Phase가 읽어야 할 파일 경로]
```

### Context 압축 복구

```
1. .workflow/state.json → 현재 Phase
2. RTM → 전체 진행 상태
3. .workflow/phase-results/ → Context Snapshot, Key Decisions
4. 이어서 진행
```

### state.json 스키마

```json
{
  "feature": "[feature-slug]",
  "current_phase": "P1",
  "loopback_count": 0,
  "loopback_per_phase": {},
  "completed_phases": [],
  "greenfield": false,
  "rtm_path": "docs/requirements/[feature]-rtm.md",
  "started_at": "[date]"
}
```

---

## Test Levels

```
Level 0: UNIT TEST      → Mock 허용, 격리 검증.           P4 작성, P5 실행 (TDD)
Level 1: INTEGRATION    → Mock 최소화, 모듈 연동.         P6 작성, P7 실행
Level 2: E2E TEST       → Mock 금지, 실제 환경.           P6 작성, P7 실행
Level 3: SMOKE TEST     → 서버 기동 + 핵심 기능 1회 확인. P7 실행
```

---

## Artifact Structure

```
docs/
├── requirements/
│   ├── [feature].md             # 요구사항 (P1)
│   └── [feature]-rtm.md        # RTM — Single Source of Truth
└── architecture/
    └── [feature].md             # 아키텍처 (P3)

tests/
├── unit/                        # Unit Test (P4)
├── integration/                 # Integration Test (P6)
└── e2e/                         # E2E Test (P6)

src/[feature]/                   # 구현 (P5)

.workflow/                       # 임시, gitignored
├── state.json
├── loopback-context.md
└── phase-results/P{N}.md

reports/[feature]-completion.md  # 완료 보고서 (P9)
```

---

## USER INPUT

**Feature Request**: $ARGUMENTS

---

## EXECUTION PROTOCOL

### ═══════════════════════════════════════════════════════════════
### PHASE 1: REQUIREMENTS ANALYSIS (메인 직접)
### ═══════════════════════════════════════════════════════════════

**Output**: `docs/requirements/[feature].md`, `docs/requirements/[feature]-rtm.md`

#### 1.1 Context Gathering + Greenfield 판별

```
1. 프로젝트 구조 분석 (Glob, Grep)
2. 기존 코드 패턴, 기술 스택, 의존성 파악
3. 관련 모듈/파일 식별

Greenfield 판별:
  src/ 에 코드가 없거나, 빌드 설정/의존성 파일이 없으면 → Greenfield
```

#### 1.1.1 System Decisions (Greenfield 전용 — 사용자 확인)

Greenfield인 경우에만 실행. 기존 코드가 있으면 자동 감지하여 스킵.

```
사용자에게 확인:
1. 언어/런타임
2. 프레임워크
3. 배포 환경
4. 외부 의존성
5. 기타 제약

승인 후 → 요구사항 문서 "System Decisions" 섹션에 기록
이후 전체 워크플로우 자율 진행 (추가 사용자 게이트 없음)
```

#### 1.2 Requirements Derivation

```
도출: 핵심 기능, 엣지 케이스, NFR(성능/보안), 제약 조건
```

#### 1.3 Ambiguity Handling

Greenfield 기술 결정은 반드시 사용자 확인. 그 외 모호한 부분은 자동 결정하고 문서에 기록.

#### 1.4 Constraint Verification

```
외부 API → 실제 호출로 검증
배포 환경 → 실행 환경 제약 확인
런타임 호환성 → 라이브러리 지원 여부 확인
결과를 요구사항 문서 "검증된 제약" 섹션에 기록
```

#### 1.5 Requirements Document

```markdown
# Requirements: [Feature Name]

## 1. Functional Requirements
| REQ-ID | Requirement | Priority | Acceptance Criteria |

## 2. Non-Functional Requirements
| NFR-ID | Category | Requirement | Measurement |

## 3. Edge Cases
| EDGE-ID | Scenario | Expected Behavior | Related REQ |

## 4. Constraints (검증된 제약)
## 5. System Decisions (Greenfield — 사용자 승인)
## 6. Decisions (자동 결정)
```

#### 1.6 RTM 초기화

```markdown
| REQ-ID | Requirement | Priority | Unit TC | Integration TC | E2E TC | Impl Location | Result | Review | Status |
| REQ-001 | ... | P1 | - | - | - | - | - | - | Registered |
```

#### 1.7 Completion

```
□ 요구사항 문서 + RTM 초기화 완료
□ 제약 검증 완료
□ state.json 초기화 (greenfield 플래그)
□ .workflow/phase-results/P1.md Write
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 2: CODEBASE EXPLORATION (메인 직접)
### ═══════════════════════════════════════════════════════════════

#### 2.0 Greenfield Skip Gate

```
greenfield == true → 스킵. P2.md에 SKIPPED 기록. 즉시 P3.
greenfield == false → 아래 실행.
```

#### 2.1 탐색

```
1. 프로젝트 구조 (Glob)
2. 유사 기능 (Grep)
3. 아키텍처 (엔트리포인트, 서비스 레이어 Read)
4. 테스트 패턴 (기존 테스트 구조 파악)
5. 핵심 파일 직접 Read
```

#### 2.2 Completion

```
□ .workflow/phase-results/P2.md Write
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 3: ARCHITECTURE DESIGN (메인 직접)
### ═══════════════════════════════════════════════════════════════

**Output**: `docs/architecture/[feature].md`

#### 3.1 설계

```
P1~P2 컨텍스트를 기반으로 직접 설계.

포함 항목:
- 파일 구조 (생성/수정)
- 인터페이스 계약 (public 함수 시그니처) — P4, P5가 따름
- 데이터 흐름
- 통합 포인트
```

#### 3.2 Architecture Document

```markdown
# Architecture: [Feature Name]
## 1. Design Overview
## 2. File Structure
## 3. Interface Contract
## 4. Data Flow
## 5. Integration Points
```

#### 3.3 Completion

```
□ docs/architecture/[feature].md Write
□ .workflow/phase-results/P3.md Write
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 4: UNIT TEST — TDD RED (메인 직접)
### ═══════════════════════════════════════════════════════════════

**Output**: `tests/unit/[feature].*`
**RTM Update**: Unit TC-ID 매핑

#### 4.1 Unit Test 작성

```
1. 격리: 외부 의존성 Mock/Stub
2. AAA: Arrange → Act → Assert
3. @requirement 주석으로 REQ-ID 매핑
4. 아키텍처 인터페이스 계약에 정의된 함수만 테스트
```

#### 4.2 RTM Update: Unit TC 매핑

```
RTM에 각 REQ의 Unit TC-ID 기록. 업데이트 이력 추가.
```

#### 4.3 RED 확인

```
모든 Unit Test 실행 → FAIL 확인 (구현 없음)
```

#### 4.4 Completion

```
□ RTM에 Unit TC-ID 매핑
□ RED 확인
□ .workflow/phase-results/P4.md Write
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 5: IMPLEMENTATION — TDD GREEN (메인 직접)
### ═══════════════════════════════════════════════════════════════

**Output**: `src/[feature]/*`
**RTM Update**: 구현 위치(file:line) 매핑

#### 5.1 구현

```
1. 점진적: 한 번에 하나의 테스트만 통과
2. 아키텍처 인터페이스 계약 준수
3. 보안 체크: 입력 검증, 민감 데이터
```

#### 5.2 RTM Update: 구현 위치 매핑

```
RTM에 각 REQ의 구현 위치(file:line) 기록. 업데이트 이력 추가.
```

#### 5.3 GREEN 확인

```
모든 Unit Test 실행 → PASS 확인
```

#### 5.4 Completion

```
□ RTM에 구현 위치 매핑
□ GREEN 확인
□ .workflow/phase-results/P5.md Write
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 6: INTEGRATION & E2E TEST (메인 직접)
### ═══════════════════════════════════════════════════════════════

**Output**: `tests/integration/*`, `tests/e2e/*`
**RTM Update**: Integration TC + E2E TC 매핑

#### 6.1 Integration Test

```
Mock 최소화. 모듈 간 실제 연동 검증. @requirement 주석.
```

#### 6.2 E2E 전략 결정

```
프로젝트 유형 판별:
  웹 프론트엔드 → 브라우저 자동화 + 서버 기동
  웹 API       → HTTP 클라이언트 + 실제 서버
  CLI          → subprocess 실행 + stdout 검증
  라이브러리    → Integration으로 충분 (E2E 해당 없음)
```

#### 6.3 E2E 환경 구성 + E2E Test 작성

```
필수: 실제 환경 (Mock 금지). Given-When-Then. @requirement 주석.
금지: fetch/HTTP Mock, DOM Mock, "E2E-style" unit test.
```

#### 6.4 RTM Update: IT/E2E TC 매핑

```
RTM에 Integration/E2E TC-ID 기록. 업데이트 이력 추가.
```

#### 6.5 Completion

```
□ RTM에 IT/E2E TC-ID 매핑
□ .workflow/phase-results/P6.md Write
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 7: TEST EXECUTION (메인 직접)
### ═══════════════════════════════════════════════════════════════

**RTM Update**: 테스트 결과(PASS/FAIL) 기록

#### 7.1 실행 순서

```
Step 1: UNIT TEST → Step 2: INTEGRATION → Step 3: E2E → Step 4: SMOKE
```

#### 7.2 E2E 품질 검증

```
테스트 PASS/FAIL과 무관하게:
  □ E2E 코드에 mock/stub/spy 없는가?
  □ 실제 서버 기동되었는가?
  □ 실제 엔드포인트에 요청하는가?
미충족 → RTM에 FAIL 기록
```

#### 7.3 RTM Update: 테스트 결과 기록

```
RTM의 Result 컬럼에 각 REQ의 테스트 결과(PASS/FAIL) 기록.
업데이트 이력 추가.
```

#### 7.4 분기

```
ALL PASS → P8 진행
ANY FAIL → RTM에 FAIL 기록 후, 즉시 JUDGE 스폰 (P8 스킵)
```

#### 7.5 Completion

```
□ RTM에 결과 기록
□ .workflow/phase-results/P7.md Write
  (FAIL이어도 체크포인트 작성 후 JUDGE 진행)
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 8: CODE REVIEW (서브에이전트 ×3 병렬)
### ═══════════════════════════════════════════════════════════════

**P7 ALL PASS인 경우에만 실행.**

#### 8.1 병렬 리뷰

```
Agent 1: 품질/DRY/가독성 — src/, docs/architecture/
Agent 2: 버그/정확성     — src/, tests/
Agent 3: 컨벤션/보안     — src/, docs/requirements/

신뢰도 80%+ 이슈만 보고.
```

#### 8.2 메인: RTM에 리뷰 결과 반영

```
서브 ×3 이슈 수합 후:
  → RTM의 Review 컬럼에 각 REQ의 리뷰 결과 기록 (PASS/MINOR/MAJOR/CRITICAL)
  → 업데이트 이력에 P8 기록
  → JUDGE 서브에이전트 스폰 (RTM 경로만 전달)
```

---

### ═══════════════════════════════════════════════════════════════
### JUDGE: RTM-BASED LOOPBACK EVALUATION (서브에이전트 ×1)
### ═══════════════════════════════════════════════════════════════

**목적**: 메인 편향 제거. RTM만 읽고 객관적 판별.

**Input**: `docs/requirements/[feature]-rtm.md` — RTM 하나만 Read.
**Output**: 메시지로 판별 결과 반환 (파일 Write 안 함)

RTM에 모든 정보가 있다:
- REQ-ID ↔ TC-ID 매핑
- 구현 위치(file:line)
- 테스트 결과(PASS/FAIL)
- 리뷰 결과(PASS/MINOR/MAJOR/CRITICAL)

필요시 RTM에서 역추적한 테스트/구현 파일을 추가로 Read.

#### 스폰 타이밍

```
1. P7에서 ANY FAIL → P8 스킵, 즉시 JUDGE
2. P8 완료 후 → JUDGE (PASS 확인 또는 LOOPBACK 판별)
```

#### RTM 판별 프로세스

```
STEP 1: RTM에서 FAIL 또는 MAJOR/CRITICAL 있는 REQ-ID 식별
STEP 2: 해당 REQ-ID → TC-ID → 구현 위치(file:line) 역추적
STEP 3: 필요시 테스트 코드/구현 코드를 직접 Read하여 원인 분류
STEP 4: 판별 결과 반환

원인 분류:
  Test Bug:    테스트 기대값 오류, assertion 오류 → P4
  Impl Bug:    구현 로직 오류, 예외 미처리 → P5
  Test Design: E2E 시나리오/환경 오류, Mock 사용 → P6
  Arch Issue:  모듈 인터페이스 불일치, 설계 결함 → P3
```

#### JUDGE 반환 형식

```
## Verdict: PASS | LOOPBACK
## Target Phase: P3 | P4 | P5 | P6
## Root Cause: [Test Bug | Impl Bug | Test Design | Arch Issue]
## Failed Items:
  - [TC-ID 또는 리뷰 이슈] — [에러 요약]
## RTM Trace:
  - TC-ID → REQ-ID → file:line
## Instructions: [구체적 수정 지시]
```

---

### ═══════════════════════════════════════════════════════════════
### LOOPBACK 실행 (메인 에이전트)
### ═══════════════════════════════════════════════════════════════

JUDGE 반환을 받은 메인:

#### PASS → P9 진행

#### LOOPBACK →

```
1. .workflow/loopback-context.md에 기록:
   ## LOOPBACK #N
   - Cause / Failed Items / RTM Trace / Target / Instructions

2. state.json 업데이트 (loopback_count++, loopback_per_phase)

3. 제한 확인:
   same_phase 2회 → 상위 Phase 에스컬레이션 (P5→P3, P6→P3, P4→P3)
   total 5회 초과 → Partial Report → P9

4. 해당 Phase로 회귀하여 수정

5. 수정 후 재실행 범위 (회귀 Phase부터 끝까지):
   P3 회귀: P3 → P4 → P5 → P6 → P7 → [P8] → JUDGE
   P4 회귀: P4 → P5 → P6 → P7 → [P8] → JUDGE
   P5 회귀: P5 → P6 → P7 → [P8] → JUDGE
   P6 회귀: P6 → P7 → [P8] → JUDGE
```

#### Artifact Update Matrix

```
→ P3 (Arch Issue):   RTM ✅  Arch ✅  Tests ✅  Impl ✅
→ P4 (Test Bug):     RTM ✅  Arch -   Tests ✅  Impl -
→ P5 (Impl Bug):     RTM ✅  Arch -   Tests -   Impl ✅
→ P6 (Test Design):  RTM ✅  Arch -   Tests ✅  Impl -
```

---

### ═══════════════════════════════════════════════════════════════
### PHASE 9: COMPLETION REPORT (메인 직접)
### ═══════════════════════════════════════════════════════════════

**Output**: `reports/[feature]-completion.md`

```markdown
# Completion Report: [Feature Name]

## Metadata
- Workflow: HALO v3
- Completed: [date]
- LOOPBACK count: N

## 1. Feature Summary
## 2. Artifact List
## 3. RTM Final State
## 4. Code Review Results
## 5. Test Results
## 6. LOOPBACK History
## 7. Next Steps
```

---

## WORKFLOW FLAGS

```
--autonomous        # 자율 모드 (기본값)
--skip-review       # P8 코드 리뷰 스킵
--skip-exploration  # P2 코드베이스 탐색 스킵
--skip-architecture # P3 아키텍처 설계 스킵
--max-loops N       # 최대 LOOPBACK (기본: 5)
```

---

## NOW EXECUTING...

**Feature Request**: $ARGUMENTS

**Phase 1: REQUIREMENTS ANALYSIS 시작...**
