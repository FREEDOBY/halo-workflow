# Requirements: config-loader

## 1. Functional Requirements

| REQ-ID | Requirement | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001 | JSON 파일을 dict 로 로드 | P0 | 유효한 JSON 파일 → dict 반환 |
| REQ-002 | 존재하지 않는 파일 처리 | P0 | FileNotFoundError raise |
| REQ-003 | 잘못된 JSON 처리 | P0 | ValueError raise (원인 메시지 포함) |

## 2. Non-Functional Requirements
- 표준 라이브러리만 사용 (json, pathlib)
- Python 3.11+

## 3. Edge Cases
| EDGE-ID | Scenario | Expected | REQ |
|---------|----------|----------|-----|
| EDGE-01 | 빈 JSON `{}` | 빈 dict 반환 | REQ-001 |
| EDGE-02 | 디렉토리 경로 입력 | FileNotFoundError 또는 ValueError | REQ-002 |

## 4. Constraints (Verified)
- Python 3.11.x 환경에서 표준 라이브러리만 사용 — 검증됨

## 5. System Decisions (Greenfield — User Approved)
- Language/Runtime: Python 3.11+
- 의존성: 없음 (표준 라이브러리만)
- 배포: pip 패키지가 아닌 소스 직접 실행 (`python -m configloader`)
