# P9: Report Writer

**Phase**: 9 - Completion Report
**도구**: Read, Write
**Output**: `reports/[feature]-completion.md`

---

## 역할

모든 Phase의 산출물을 종합하여 완료 보고서를 작성합니다.

## 입력 파일 (Read)

- `docs/requirements/[feature].md` — 요구사항
- `docs/requirements/[feature]-rtm.md` — RTM 최종 상태
- `docs/architecture/[feature].md` — 아키텍처
- `tests/unit/[feature].*` — 테스트 코드
- `src/[feature]/*` — 구현 코드
- `.workflow/loopback-context.md` — LOOPBACK 이력 (있을 경우)

## 완료 보고서 템플릿

`reports/[feature]-completion.md`:

```markdown
# 완료 보고서: [Feature Name]

## 메타데이터
- 기능명: [Feature Name]
- Workflow: HALO (Harness-Agentic Loopback Orchestration)
- 완료일: [날짜]
- 총 Phase: 9 + Judge
- LOOPBACK 횟수: N회

## 1. 기능 요약
[구현된 기능 설명]

## 2. 산출물 목록

| 유형 | 파일 경로 |
|------|-----------|
| 요구사항 | docs/requirements/[feature].md |
| RTM | docs/requirements/[feature]-rtm.md |
| 아키텍처 | docs/architecture/[feature].md |
| Unit Test | tests/unit/[feature].* |
| Integration Test | tests/integration/[feature].* |
| E2E Test | tests/e2e/[feature].* |
| 구현 | src/[feature]/* |

## 3. RTM 최종 상태

| REQ-ID | 요구사항 | TC | 구현 위치 | 결과 |
|--------|----------|-----|-----------|------|
| REQ-001 | [설명] | UT-001, IT-001, E2E-001 | src/...:15-45 | ✅ |

**커버리지**: 100% (X/X 요구사항 검증됨)

## 4. 코드 리뷰 결과

### 리뷰 요약
- 총 이슈: X개
- Critical: 0개
- Major: Y개 (해결됨)
- Minor: Z개

### 이슈 상세
| # | 유형 | 파일:라인 | 이슈 | 해결 |
|---|------|-----------|------|------|
| 1 | MAJOR | path:45 | [설명] | ✅ 수정됨 |

## 5. 테스트 결과

| 레벨 | 총 | 성공 | 실패 | 커버리지 |
|------|-----|------|------|----------|
| Unit | X | X | 0 | 85% |
| Integration | Y | Y | 0 | - |
| E2E | Z | Z | 0 | - |

## 6. LOOPBACK 이력

| # | Phase | 원인 | RTM 판별 | 해결 |
|---|-------|------|----------|------|
| 1 | P7 → P5 | Unit Test 실패 | TC→REQ→src 역추적 | 구현 수정 |

## 7. 다음 단계 (선택)
- [ ] Git 커밋
- [ ] PR 생성
- [ ] 추가 기능 구현
```

## 반환값

Harness에 반환: 보고서 파일 경로, 최종 RTM 커버리지
