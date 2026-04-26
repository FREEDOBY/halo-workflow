# HALO Workflow v3

**H**arness · **A**gentic · **L**oopback · **O**rchestration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**요구사항이 유일한 진실(single source of truth)** — HALO 는 이 전제를 워크플로우 전체에 강제한다. 요구사항은 **RTM(Requirements Traceability Matrix)** 이라는 단일 문서로 박제되고, 테스트 · 구현 · 리뷰는 모두 그 진실에 귀속된다. TDD 는 P4/P5 에서 쓰는 전술, LOOPBACK 은 산출물이 요구사항에서 벗어났을 때 복귀시키는 메커니즘 — 둘 다 "요구사항에 충실하기" 위한 수단일 뿐이다.

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) 에서 작동한다. **메인 에이전트**가 8 개의 순차 phase (P1~P7, P9) 를 **컨텍스트 단절 0** 으로 직접 실행하며, 서브 에이전트는 **P8 코드 리뷰** 와 **JUDGE RTM 평가** 에만 투입된다.

> **[인터랙티브 아키텍처 다이어그램](https://FREEDOBY.github.io/halo-workflow/)**

## 목차

- [설계 철학](#설계-철학)
- [Quick Start](#quick-start)
- [입력 단위 가이드](#입력-단위-가이드)
- [Architecture](#architecture)
- [RTM = Single Source of Truth](#rtm--single-source-of-truth)
- [핵심 원칙](#핵심-원칙)
- [Phases](#phases)
  - [메인 에이전트 직접 실행 (8 Phases)](#메인-에이전트-직접-실행-8-phases)
  - [서브 에이전트 (2 지점)](#서브-에이전트-2-지점)
  - [LOOPBACK 정책](#loopback-정책)
- [테스트 레벨](#테스트-레벨)
- [License](#license)

## 설계 철학

LLM 에이전트 워크플로우는 **조용히 실패한다**. 컨텍스트가 drift 되고, 에이전트가 자기 산출물에 후한 도장을 찍고, 문서가 반복 편집으로 침식되고, 가정이 검증 없이 넘어간다 — 어느 것도 에러를 내지 않는다. HALO 는 이 실패 모드들을 희망이 아닌 **구조**로 방어하도록 설계되었다.

- **병렬보다 연속성.** 메인 에이전트가 P1–P9 를 직접 이어서 수행하므로, P3 에서 내린 결정이 P7 의 선택까지 압축 손실 없이 전달된다. 서브 에이전트는 독립성이나 다른 관점이 실제로 필요한 지점 — P8 다관점 리뷰, JUDGE 편향 제거 — 에만 쓴다. 병렬 그 자체는 목적이 아니다.
- **평가자는 다른 reader 다.** 코드를 작성한 에이전트는 그 코드가 좋은지 판단할 자격이 없다. JUDGE 는 RTM 만 읽고 저자의 수사에 귀 기울이지 않으며, LOOPBACK 여부를 객관적으로 결정한다.
- **메모리보다 파일.** 모든 phase 간 신호는 `.workflow/`, RTM, 리뷰 문서에 남는다. 채팅 기억, 에이전트 prompt, 암묵적 상태는 금지. 컨텍스트 압축이 대화를 잘라도 파일은 살아남는다.
- **완전한 산출보다 작은 산출.** RTM 은 편집할 때 전체가 한 시야에 들어와 정확한 셀을 타겟팅할 수 있도록 작게 유지한다. 세부 추적은 인접 파일로 분산. drift 하는 큰 문서보다 신뢰할 수 있는 작은 문서가 낫다.
- **수정은 재정의가 아니다.** LOOPBACK 은 요구사항이 이미 요구하던 것을 고친다. 요구사항 자체가 바뀌면 새 사이클이 시작된다. 이 경계가 수정 작업 중의 몰래 scope 확장을 막는다.
- **분해는 사용자 몫.** 깨끗한 컨텍스트는 입력 크기에서 결정된다. 1 회 호출 = 1 개의 작은 RTM 사이클이라는 전제를 지키기 위해 HALO 는 자동 분할하지 않는다. 사용자가 자연스러운 경계로 쪼개 다회 호출하면, 시스템은 그 사이클들을 자동으로 잇는다 — 다음 호출의 P2 가 이전 사이클의 RTM 과 completion report 를 읽어 P3 설계 입력으로 전달한다. 시스템 추측보다 사용자 의도가 항상 더 정확하다.

각 원칙은 개발 중 실제로 목격된 실패 모드에 대응한다 — 스타일 선호가 아니다.

## Quick Start

1. 프로젝트에 `.claude/` 폴더 복사
2. `/halo-workflow [기능 설명]` 실행

## 입력 단위 가이드

깨끗한 컨텍스트는 입력 크기에서 결정된다. HALO 1 회 호출이 안정적으로 처리할 수 있는 범위는 유한하다 — 다음 신호 중 하나라도 보이면 **분할 후 다회 호출**을 권한다:

- 요구사항이 명확히 다른 레이어에 걸쳐 있다 (예: 인증 + UI + 알림)
- 독립적으로 배포 / 테스트 가능한 단위가 둘 이상 보인다
- 큰 기존 코드베이스(Brownfield) 위에 작업한다

**분할 예시**

❌ 한 번에:

```
/halo-workflow "사용자 인증 + 프로필 API + 푸시 알림 시스템"
```

✅ 쪼개서:

```
/halo-workflow "사용자 인증 (JWT 기반)"
/halo-workflow "프로필 API (인증된 사용자 대상)"
/halo-workflow "푸시 알림 시스템"
```

청크 간 연속성은 **P2 (코드베이스 탐색) 가 자동으로 보장**한다. 다음 호출의 P2 가 이전 사이클의 `reports/*-completion.md` 와 `docs/requirements/*-rtm.md` 를 발견해 P3 설계 입력으로 전달한다. 사용자는 분할 경계만 결정하고, 시스템은 그 결정을 잇는다 — 같은 파일을 동시 수정해야 하는 잘못된 분할은 사용자가 직접 막는다.

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│  MAIN AGENT  (Executor + Router)                                   │
│                                                                    │
│  P1 ──→ P2 ──→ P3 ──→ P4 ──→ P5 ──→ P6 ──→ P7 ──→ P8 ──→ P9  │
│  direct direct direct direct direct direct direct  ↕    direct   │
│  ──────── Main continuous (zero context breaks) ─  │              │
│                                                  Review  JUDGE    │
│                                                  ┌─┴─┐  ┌───┐    │
│                                                  │ ×3 │  │ ×1│    │
│                                                  └───┘  └─┬─┘    │
│              JUDGE reads RTM only → classifies:          │       │
│              ┌──── Test Bug → P4 ────────────────────────┘       │
│              ├──── Impl Bug → P5                                  │
│              ├──── Test Design → P6                                │
│              └──── Arch Issue → P3                                 │
├────────────────────────────────────────────────────────────────────┤
│  .workflow/    Checkpoint + State (temporary, gitignored)          │
├────────────────────────────────────────────────────────────────────┤
│  docs/ tests/ src/ reports/    Product Artifacts (permanent)       │
└────────────────────────────────────────────────────────────────────┘
```

## RTM = Single Source of Truth

**요구사항이 진실이고, RTM 은 그 진실을 phase 사이로 나르는 문서다.** 모든 phase 가 RTM 을 갱신하고, JUDGE 는 오직 RTM 만 읽어 산출물이 요구사항에 충실했는지를 판단한다. 따라서 RTM 이 틀어지면 판단이 틀어지고, 판단이 틀어지면 LOOPBACK 이 엉뚱한 phase 로 돌아간다 — RTM 을 작게 유지하는 이유.

```
  P1           P4           P5            P6            P7       P8       JUDGE
  ●────────────●────────────●─────────────●─────────────●────────●────────▶ ◆
  │            │            │             │             │        │          │
  init RTM     +Unit TC     +impl loc     +IT/E2E TC   +result  +review   RTM only
  REQ-IDs      mapping      file:line     mapping      PASS/    issues    → evaluate
                                                        FAIL    reflect   → loopback
```

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **RTM = Single Source of Truth** | 모든 phase 가 RTM 갱신. JUDGE 는 RTM 만 읽는다. |
| **Main Agent First** | P1~P7 메인 직접 실행. 서브 에이전트는 P8 (리뷰) 와 JUDGE 에만. |
| **Constraint Verification** | 외부 API / 배포 환경 가정은 P1 에서 실제 호출로 검증. |
| **Real E2E** | E2E 테스트는 실제 환경에서 실행. Mock 금지. |
| **File = Interface** | 에이전트 간 통신과 컨텍스트 복구는 파일시스템으로만. |
| **LOOPBACK ≠ 요구사항 변경** | 요구사항 불변. 회귀 경로 4 개 (P3/P4/P5/P6). |

## Phases

### 메인 에이전트 직접 실행 (8 Phases)

| Phase | 역할 | RTM 갱신 |
|-------|------|----------|
| P1 | 요구사항 + 제약 검증 | RTM 초기화 (REQ-ID 등록) |
| P2 | 코드베이스 탐색 (Greenfield 시 자동 스킵) | - |
| P3 | 아키텍처 설계 | - |
| P4 | 단위 테스트 (TDD RED) | + Unit TC 매핑 |
| P5 | 구현 (TDD GREEN) | + 구현 위치 (file:line) |
| P6 | Integration & E2E 테스트 (실제 환경) | + IT/E2E TC 매핑 |
| P7 | 테스트 실행 + Smoke | + 결과 (PASS/FAIL) |
| P9 | 완료 보고서 | Status → Complete |

### 서브 에이전트 (2 지점)

| Phase | 역할 | 에이전트 | 목적 |
|-------|------|----------|------|
| P8 | 코드 리뷰 | ×3 병렬 | 품질 / 버그 / 보안 → 이슈를 RTM 에 반영 |
| JUDGE | RTM 평가 | ×1 | RTM 만 읽음 → 근본 원인 분류 → LOOPBACK |

### LOOPBACK 정책

| 근본 원인 | 회귀 대상 |
|----------|-----------|
| Test Bug (assertion 오류, 잘못된 기대값) | **→ P4** |
| Impl Bug (로직 오류, 미처리 예외) | **→ P5** |
| Test Design (E2E 시나리오, 환경 이슈, mock 오용) | **→ P6** |
| Arch Issue (인터페이스 불일치, 설계 결함) | **→ P3** |

> **한도**: 총 5 회, phase 당 2 회. 동일 phase 2 회 초과 → 상위 phase 로 escalate (예: P5→P3). 전체 한도 초과 → Partial Report → P9.

> **재실행 범위**: 회귀 phase 부터 끝까지 (예: P5 회귀 시 P5 → P6 → P7 → P8 → JUDGE).

## 테스트 레벨

```
Level 0: UNIT TEST        — Mock 허용, 격리 (P4/P5 TDD)
Level 1: INTEGRATION TEST — 최소 mock, 모듈 간 상호작용 (P6/P7)
Level 2: E2E TEST         — Mock 금지, 실제 서버/브라우저/API (P6/P7)
Level 3: SMOKE TEST       — 서버 기동 + 핵심 기능 확인 (P7)
```

## License

MIT
