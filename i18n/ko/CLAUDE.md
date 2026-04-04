# HALO Workflow Project

## 사용법
```
/halo-workflow [feature description]
```

## 핵심 원칙
- **Main Agent First** — 순차 작업은 메인 에이전트가 직접 수행. 서브에이전트는 병렬만.
- **RTM = Single Source of Truth** — `docs/requirements/*-rtm.md`
- **File = Interface** — 에이전트 간 통신과 context 복구는 파일 시스템으로만
- **Constraint Verification** — 외부 의존성/배포 환경 가정은 반드시 실제 호출로 검증
- **Real E2E** — E2E 테스트는 실제 실행 환경에서 수행. Mock 금지.
- **LOOPBACK은 요구사항을 바꾸지 않음** — 요구사항 변경 = 새 사이클
- **Max 5 LOOPBACK, per-phase 2회** — 초과 시 Partial Report 생성

## 실행 모델
- **메인 직접** (6 Phases): P1 요구사항, P4 테스트, P5 구현, P6 IT/E2E, P7 실행, P9 보고
- **서브에이전트** (3 Phases): P2 정찰, P3 경쟁설계, P8 리뷰

## 서브에이전트 역할
- **P2 정찰병**: 핵심 파일 목록 보고 → 메인이 직접 Read
- **P3 경쟁설계**: 설계안 + 참조 코드 보고 → 메인이 직접 확인 후 확정
- **P8 리뷰어**: 관점별 이슈 보고 → 메인이 종합 판단

## 에이전트 정의
`.claude/commands/agents/` 폴더에 서브에이전트(P2, P3, P8)가 정의되어 있습니다.
