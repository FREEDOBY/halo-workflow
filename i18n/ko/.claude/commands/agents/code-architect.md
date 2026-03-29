# P3: Code Architect

**Phase**: 3 - Architecture Design
**도구**: Read, Glob, Grep, Write
**병렬**: 2-3개 동시 스폰
**Output**: `docs/architecture/[feature].md`

---

## 역할

복수의 설계안을 병렬 생성하고, Harness가 최적안을 선택합니다.

## 병렬 에이전트 프롬프트

### 에이전트 1: 최소 변경 (Minimal)
```
"기존 코드 최대 재사용, 최소 변경으로 구현.
변경 파일 수를 최소화하고 기존 패턴을 그대로 따름."
```

### 에이전트 2: 깔끔한 구조 (Clean)
```
"유지보수성과 우아한 추상화 중점.
SOLID 원칙 준수, 명확한 책임 분리."
```

### 에이전트 3: 실용적 균형 (Pragmatic)
```
"개발 속도와 코드 품질 균형.
적절한 추상화 수준, 테스트 용이성 고려."
```

## 설계안 선택 기준 (Harness가 자동 적용)

```scoring
- changed_files_count: weight 0.3 (적을수록 높은 점수)
- new_abstractions: weight 0.2 (적을수록 높은 점수)
- test_surface: weight 0.2 (테스트 용이성)
- pattern_consistency: weight 0.3 (기존 코드베이스와의 일관성)

selection: max(score) → 동점 시 "Pragmatic" 우선
```

## 아키텍처 문서 템플릿

`docs/architecture/[feature].md`:

```markdown
# 아키텍처 설계: [Feature Name]

## 메타데이터
- 작성일: [날짜]
- 선택 접근법: [Minimal | Clean | Pragmatic]

## 1. 설계 개요
- 선택 근거: [scoring 결과]

## 2. 파일 구조

### 생성할 파일
- src/[feature]/[file].ts - [설명]

### 수정할 파일
- src/existing/[file].ts - [수정 내용]

## 3. 컴포넌트 설계

### [Component Name]
- 책임: [설명]
- 인터페이스: [API]
- 의존성: [목록]

## 4. 데이터 흐름
[입력] → [처리] → [출력]

## 5. 통합 포인트
- [기존 모듈과의 연동 방법]
```

## 반환값

Harness에 반환: 아키텍처 파일 경로, 생성/수정 파일 목록, 선택 근거
