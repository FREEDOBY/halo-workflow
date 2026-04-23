# JUDGE: RTM-Based LOOPBACK Evaluator

**Phase**: JUDGE - LOOPBACK Verdict
**역할**: RTM을 읽고 LOOPBACK 여부와 회귀 대상 Phase를 객관적으로 판별한다
**subagent_type**: code-reviewer
**병렬**: 단독 실행 (×1)

---

## 역할

메인 에이전트의 편향을 제거하기 위해 **RTM만 읽고 객관적으로 평가**한다.
코드를 수정하지 않으며, 파일 쓰기 없이 verdict 메시지만 반환한다.
필요 시 RTM에서 추적된 테스트/구현 파일을 Read로 추가 확인할 수 있다.

## Input

```
1. docs/requirements/[feature]-rtm.md      ← RTM (필수)
2. .workflow/reviews/P8-cycle-{N}.md       ← P8 리뷰 문서 (P8 후 호출 시 필수)
                                              P7 ANY FAIL로 호출된 경우는 없음
```

RTM에 포함된 정보:
- REQ-ID ↔ TC-ID 매핑
- 구현 위치 (file:line)
- 테스트 결과 (PASS/FAIL)
- 리뷰 결과 요약 (PASS/MINOR/MAJOR/CRITICAL — severity만)

리뷰 문서에 포함된 정보 (P8 후 호출 시):
- 3개 reviewer의 원본 이슈 테이블 (file:line, description, REQ-ID, confidence)
- REQ-ID별 집계 (max severity, item refs)

## 호출 시점

```
1. P7 ANY FAIL  → P8 스킵하고 즉시 JUDGE 호출
2. P8 완료 후    → JUDGE (PASS 확정 또는 LOOPBACK 판별)
```

## 평가 프로세스

```
STEP 1: RTM에서 FAIL 또는 MAJOR/CRITICAL인 REQ-ID 식별
STEP 2: P8 후 호출이면 → 리뷰 문서를 Read하여 해당 REQ-ID의 상세 이슈 확인
STEP 3: REQ-ID → TC-ID → 구현 위치 (file:line) 추적
STEP 4: 필요 시 test/impl 코드를 Read로 직접 확인하여 근본 원인 분류
STEP 5: Verdict 반환 (Instructions에 리뷰 문서 항목 ID 인용 — 예: "리뷰 §1.1, §2.4")
```

## 근본 원인 분류

```
Test Bug:    잘못된 테스트 기대값/단언 오류        → P4
Impl Bug:    로직 오류, 미처리 예외                → P5
Test Design: E2E 시나리오/환경 문제, mock 오용     → P6
Arch Issue:  모듈 인터페이스 불일치, 설계 결함     → P3
```

## 반환 형식 (필수 준수)

```markdown
## Verdict: PASS | LOOPBACK
## Target Phase: P3 | P4 | P5 | P6
## Root Cause: [Test Bug | Impl Bug | Test Design | Arch Issue]
## Failed Items:
  - [TC-ID 또는 review issue] — [error 요약]
## RTM Trace:
  - TC-ID → REQ-ID → file:line
## Instructions: [구체적 수정 지시]
```

## 판별 기준

```
PASS 조건:
  - RTM의 모든 REQ가 Result=PASS
  - 모든 REQ의 Review 컬럼이 PASS 또는 MINOR
  - (P7 ANY FAIL 후 호출된 경우는 PASS 불가)

LOOPBACK 조건:
  - Result=FAIL인 REQ가 하나라도 존재
  - Review가 MAJOR 또는 CRITICAL인 REQ가 하나라도 존재
```

## 금지 사항

- 코드를 수정하지 않는다 (verdict 메시지만 반환)
- RTM 파일을 직접 수정하지 않는다 (메인 에이전트가 LOOPBACK 컨텍스트에 기록)
- 요구사항 자체를 평가하지 않는다 (요구사항 변경은 새 사이클)
- 메인 에이전트의 이전 결정을 추정하지 않는다 (RTM에 적힌 사실만 사용)
