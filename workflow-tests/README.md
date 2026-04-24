# Workflow Tests

HALO 워크플로우 **자체**를 테스트하는 메타-테스트 디렉토리.
워크플로우 프롬프트를 개선할 때 **같은 입력에 대한 품질 변화를 숫자로** 확인하는 게 목표다.

> 여기서 말하는 "테스트"는 워크플로우가 만들어낸 산출물의 테스트가 아니라,
> 워크플로우 그 자체가 같은 품질을 재현하는지 검증하는 회귀 벤치마크다.

---

## 구조

```
workflow-tests/
├── fixtures/                         # 워크플로우에 넣을 고정 입력
│   └── smoke-cli-word-counter/
│       ├── request.txt               # /halo-workflow 에 넣을 한 줄
│       └── oracle.json               # 기대 결과 (허용 범위)
├── scripts/
│   ├── evaluate.py                   # .workflow/ + RTM + 산출물 파싱 → metrics + 오라클 비교
│   └── compare.py                    # baseline과 최신 실행 결과 diff
├── baselines/                        # 현재 기준 (git 커밋 대상)
│   └── <fixture>.json
└── runs/                             # 매 실행 아카이브 (gitignored)
    └── <fixture>/
        ├── <timestamp>/metrics.json
        └── latest.json
```

---

## 사용 흐름 (권장 — `/halo-eval` 슬래시 명령)

평범한 사용은 슬래시 명령 하나로 끝난다. 내부적으로 워크플로우 실행 + 평가 + 산출물 아카이브까지 전부 처리한다.

```
/halo-eval list                             # 사용 가능한 fixture 목록
/halo-eval smoke-cli-word-counter           # 전체 사이클 실행 (워크플로우 + 평가)
/halo-eval smoke-cli-word-counter --baseline   # 실행 + baseline 저장
/halo-eval compare smoke-cli-word-counter   # baseline 과 최신 실행 비교
/halo-eval clean                            # 잔여 산출물 수동 정리
```

명령 정의: `.claude/commands/halo-eval.md`

## 내부 스크립트 직접 호출 (고급)

슬래시 명령을 거치지 않고 직접 스크립트를 쓰고 싶을 때:

### 평가

```
python workflow-tests/scripts/evaluate.py <fixture>
```

한 번의 실행으로:
1. **지표 수집** — `.workflow/`, RTM, 리뷰 문서, 산출물 glob을 읽어 metrics 계산 후 오라클과 비교
2. **산출물 아카이브 (move)** — Greenfield fixture 인 경우 `docs/`, `src/`, `tests/`, `reports/`, `.workflow/` 를 `workflow-tests/runs/<fixture>/<timestamp>/artifacts/` 로 **이동**. 프로젝트 루트가 자동으로 클린해진다.
3. **결과 파일 기록** — `runs/<fixture>/<timestamp>/metrics.json` + `runs/<fixture>/latest.json`

플래그:
- `--save-baseline` : 평가 결과를 `baselines/<fixture>.json` 에 저장
- `--keep-artifacts` : 산출물을 이동하지 않고 workspace 에 남김 (iterative 디버깅용)
- `--no-archive` : runs/ 아카이브 자체 스킵 (metrics.json 도, 이동도 안 함 — pure read-only 평가)

exit code: 오라클 전부 PASS → 0, 하나라도 FAIL → 1

### 비교

```
python workflow-tests/scripts/compare.py <fixture>
```

`baselines/<fixture>.json` 과 `runs/<fixture>/latest.json` 의 지표 차이를 줄 단위로 출력.

---

## 평가의 4개 레이어

워크플로우의 결과는 **상대 비교(baseline diff)**가 아니라 **절대 기준**으로 평가하는 게 원칙이다. 현재 구현은 L1 + L3 이며, L2·L4 는 선택적 확장.

| 레이어 | 질문 | 구현 상태 |
|---|---|---|
| **L1 프로세스** | 워크플로우가 자기 규칙을 지켰나? | ✅ state/RTM/review 파싱 |
| **L2 정적 품질** | syntax/lint/type-check 통과? | ❌ (필요시 verify.py 안에서) |
| **L3 기능 검증** | 산출 코드가 실제 요청대로 동작하나? | ✅ `verify.py` 실행 |
| **L4 시맨틱 품질** | 별도 LLM rubric 채점 | ❌ 향후 확장 |

## 수집하는 지표

| 카테고리 | 출처 | 내용 |
|---|---|---|
| state | `.workflow/state.json` | loopback_count, loopback_per_phase, completed_phases |
| rtm | `docs/requirements/*-rtm.md` | total_reqs, result_pass, Unit/IT/E2E TC 매핑 수, impl_location 매핑 수 |
| review | `.workflow/reviews/P8-cycle-*.md` | 마지막 cycle 의 CRITICAL/MAJOR/MINOR 카운트 |
| artifacts | 지정된 glob | 산출물 파일 존재 여부 |
| **functional** | `fixtures/<name>/verify.py` 실행 | 산출 코드를 실제로 돌린 exit code + 로그 (`verify.log`) |

### `verify.py` 규약

각 fixture 는 `verify.py` 를 자유 작성한다. 평가 흐름:

```
python fixtures/<name>/verify.py <artifacts_dir>
  ↓
  exit 0       → functional PASS
  exit non-0   → functional FAIL (log 로 원인 추적)
```

`<artifacts_dir>` 는 `runs/<fixture>/<ts>/artifacts/` (Greenfield) 또는 workspace (그 외). stdout + stderr 는 `runs/<fixture>/<ts>/verify.log` 로 저장.

oracle 에서 `"functional_ok": true` 를 선언하면 evaluate.py 가 이 체크를 자동으로 포함한다. 선언하지 않으면 verify.py 는 실행되지만 오라클 판정에는 영향 없음 (정보용).

---

## Fixture 추가

1. `fixtures/<name>/request.txt` — 워크플로우에 줄 입력 (한 줄 권장)
2. `fixtures/<name>/oracle.json` — 기대 결과 (허용 범위로 표현)

`oracle.json` 키 레퍼런스:

```json
{
  "fixture": "이름",
  "description": "이 fixture가 검증하는 워크플로우 기능",
  "project_type": "cli-python | rest-api | library | ...",
  "greenfield": true,
  "expected": {
    "loopback_count_max": 1,
    "total_reqs_min": 3,
    "all_reqs_result_pass": true,
    "all_reqs_have_unit_tc": true,
    "all_reqs_have_impl_location": true,
    "review_critical_max": 0,
    "review_major_max": 1,
    "functional_ok": true,
    "artifacts_must_exist": ["docs/requirements/*.md", "src/**/*.py"]
  }
}
```

`verify.py` (선택): `expected.functional_ok = true` 를 쓸 경우 fixture 디렉토리에 `verify.py` 를 만든다. `sys.argv[1]` 로 artifacts 디렉토리 경로를 받고, 기능적으로 올바르면 `exit 0`, 그렇지 않으면 non-zero 로 종료하는 스크립트면 된다.

---

## 주의사항

- **실행 비결정성**: 같은 fixture를 돌려도 매번 결과가 완전히 같지는 않다. 중요한 변경 전후엔 최소 2~3회 돌려 평균을 봐야 한다.
- **산출물 격리**: `evaluate.py`가 Greenfield fixture의 산출물을 자동으로 runs/로 **이동**시킨다. 따라서 평가를 거친 후에는 바로 다음 fixture를 실행해도 된다. 단, **평가 전에 다른 fixture를 연속으로 돌리면 산출물이 섞이니 금지**.
- **Brownfield fixture**: 아직 산출물 이동이 지원되지 않는다 (pre-existing 코드를 망가뜨릴 수 있어서). 별도 git worktree나 수동 정리가 필요하다.
- **Oracle은 허용 범위**: 정확한 일치가 아니라 "이 정도면 합리적"의 상한/하한으로 작성한다.
