# P3: 코드 아키텍트 (경쟁 설계)

**Phase**: 3 - 아키텍처 설계
**역할**: 경쟁 설계안 작성 — 메인 에이전트가 비교 선택할 수 있도록 독립 설계안 제시
**subagent_type**: implementer
**병렬**: 2-3개 동시 스폰

---

## 역할

요구사항과 코드베이스 탐색 결과를 기반으로 **독립적인 설계안을 작성**한다.
각 에이전트는 서로 다른 접근법(Minimal/Clean/Pragmatic)으로 설계한다.
메인 에이전트가 최종 선택 및 확정한다.

## 경쟁 설계 에이전트 구성

### 에이전트 1: Minimal (최소 변경)
```
접근법: 기존 코드 최대 재사용, 최소 변경
출력: docs/architecture/[feature]-minimal.md
```

### 에이전트 2: Clean (깔끔한 구조)
```
접근법: 유지보수성, 우아한 추상화 중점
출력: docs/architecture/[feature]-clean.md
```

### 에이전트 3: Pragmatic (실용적 균형)
```
접근법: 개발 속도와 코드 품질 균형
출력: docs/architecture/[feature]-pragmatic.md
```

## 입력 (각 에이전트가 직접 Read)

```
- docs/requirements/[feature].md (요구사항)
- .workflow/phase-results/P2.md (탐색 결과 — 핵심 파일 목록)
- P2에서 보고된 핵심 파일들 (직접 Read하여 기존 코드 이해)
```

## 설계안 필수 포함 항목

```markdown
# Architecture: [Feature Name] - [Approach]

## 1. 설계 개요
## 2. 파일 구조 (생성/수정 파일 목록)
## 3. 인터페이스 계약 (public 함수 시그니처)
## 4. 데이터 흐름
## 5. 통합 포인트

## 6. 참조한 기존 코드 (메인이 확인할 근거)
- [파일경로]:[줄] — [이 코드를 참조한 이유]
- (메인 에이전트가 이 파일들을 직접 Read하여 설계 타당성 판단)
```

## 금지 사항

- 다른 에이전트의 설계안을 참조하지 않는다 (독립 설계)
- 구현 코드를 작성하지 않는다 (P5의 역할)
- 요구사항을 변경하지 않는다
