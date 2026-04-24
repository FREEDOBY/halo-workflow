---
description: "HALO 워크플로우 회귀 테스트 - fixture 기반 평가 사이클 오케스트레이터"
argument-hint: "[list | <fixture> [--baseline] | compare <fixture> | clean]"
---

# /halo-eval — HALO Workflow Evaluator

워크플로우 자체를 **회귀 테스트**하는 오케스트레이터. fixture 하나를 골라 워크플로우를 실행하고, 산출물을 자동 평가·아카이브한다.

**용도**: 워크플로우 프롬프트를 개선할 때 "같은 입력에 대한 품질 변화"를 숫자로 비교.

---

## 인자 파싱

**Input**: `$ARGUMENTS`

다음 패턴 순서로 매칭해 해당 섹션으로 이동:

| 패턴 | 섹션 |
|---|---|
| 빈 값 또는 `list` | **[LIST]** |
| `clean` | **[CLEAN]** |
| `compare <fixture>` | **[COMPARE]** |
| `<fixture>` (선택: 끝에 `--baseline`) | **[RUN]** ← 핵심 경로 |

인자가 위 패턴 중 어느 것도 아니면 사용법 안내 후 종료.

---

## [LIST] 사용 가능한 Fixture 나열

**동작**:

1. `workflow-tests/fixtures/` 아래 디렉토리 목록 확인 (Glob `workflow-tests/fixtures/*/oracle.json`)
2. 각 fixture의 `oracle.json`을 Read하여 `description` 필드 추출
3. 표로 출력:

```
| Fixture | Description |
|---------|-------------|
| smoke-cli-word-counter | 기본 happy path smoke test... |
```

4. baseline 저장 여부도 함께 표시 (`workflow-tests/baselines/<fixture>.json` 존재 여부)

---

## [CLEAN] 워크스페이스 수동 정리

**조건**: 이전 실행이 비정상 종료되어 산출물이 남아있을 때.
정상 평가 후에는 `evaluate.py`가 자동 이동하므로 보통은 불필요.

**동작**:

1. 5개 아티팩트 디렉토리에서 `.gitkeep` 외 파일을 찾아 나열:
   ```bash
   for d in docs src tests reports .workflow; do
     [ -d "$d" ] && find "$d" -type f ! -name '.gitkeep'
   done
   ```
2. 결과가 비어 있으면 "이미 클린 상태" 보고 후 종료.
3. 결과가 있으면 사용자에게 리스트 보여주고 `git status -s` 로 tracked 여부 추가 경고.
4. 사용자 확인 받은 후 **non-.gitkeep 콘텐츠만** 삭제 (스캐폴딩 디렉토리와 `.gitkeep` 은 보존):
   ```bash
   for d in docs src tests reports .workflow; do
     [ -d "$d" ] && find "$d" -mindepth 1 ! -name '.gitkeep' -delete
   done
   ```
5. 결과 보고

---

## [COMPARE] Baseline vs Latest 비교

**동작**:

```bash
python workflow-tests/scripts/compare.py <fixture>
```

출력을 그대로 사용자에게 전달. baseline이 없으면 "먼저 `/halo-eval <fixture> --baseline` 을 실행하세요" 안내.

---

## [RUN] 전체 테스트 사이클 (핵심)

`/halo-eval <fixture>` 또는 `/halo-eval <fixture> --baseline` 호출 시 수행.

### Step 1 — 사전 점검

1. **Fixture 존재 검증**:
   - `workflow-tests/fixtures/<fixture>/request.txt` 존재?
   - `workflow-tests/fixtures/<fixture>/oracle.json` 존재?
   - 없으면 오류 보고 + 사용법 안내 + 종료.

2. **워크스페이스 클린 검증**:
   - "클린" 의 정의: 5개 아티팩트 디렉토리(`docs/`, `src/`, `tests/`, `reports/`, `.workflow/`) 가 존재해도 **각 디렉토리에 `.gitkeep` 외의 실제 파일이 없으면** 클린으로 간주 (스캐폴딩만 있는 초기 상태).
   - 다음 명령으로 실제 산출물 유무 확인:
     ```bash
     for d in docs src tests reports .workflow; do
       [ -d "$d" ] && find "$d" -type f ! -name '.gitkeep' 2>/dev/null | head -1
     done
     ```
   - 파일이 하나라도 출력되면 → 중단 + 사용자에게 안내: "이전 실행 산출물이 남아 있습니다. `/halo-eval clean` 으로 정리한 뒤 다시 시도하세요."

3. **Fixture 요청 읽기**:
   - `workflow-tests/fixtures/<fixture>/request.txt` 전체 내용을 Read.
   - 이 내용이 Step 2에서 워크플로우의 Feature Request가 된다.

4. `oracle.json`의 `greenfield` 필드 확인:
   - `true` 면 워크플로우의 Greenfield 경로로 진행될 예정임을 인지.

### Step 2 — 워크플로우 실행

`.claude/commands/halo-workflow.md` 의 **EXECUTION PROTOCOL 전체** (PHASE 1 ~ PHASE 9) 를 그대로 따라 실행한다.

- `$ARGUMENTS` (Feature Request) = Step 1에서 읽은 `request.txt` 내용
- 모든 규칙 엄격 준수:
  - 각 Phase 후 checkpoint (`.workflow/phase-results/P{N}.md`) 작성
  - RTM 단계별 업데이트
  - P8 리뷰 문서 (`.workflow/reviews/P8-cycle-{N}.md`) 작성
  - JUDGE 호출 (P7 FAIL 시 즉시, 또는 P8 후)
  - LOOPBACK 한도 (총 5회, Phase당 2회)
- Greenfield tech 스택 확인 질문이 발생하면 **반드시 사용자에게 전달**하여 응답을 받는다.
- 워크플로우 정의를 임의로 생략하거나 단순화하지 말 것.

### Step 3 — 평가 실행

워크플로우 완주 (P9.md 생성, state.json current_phase=P9 등) 확인 후:

**기본**:
```bash
python workflow-tests/scripts/evaluate.py <fixture>
```

**인자 끝에 `--baseline` 이 있었다면**:
```bash
python workflow-tests/scripts/evaluate.py <fixture> --save-baseline
```

이 스크립트가 순서대로 수행하는 것:
1. 지표 수집 (state, RTM, P8 리뷰, 산출물 glob)
2. 산출물 이동 → `workflow-tests/runs/<fixture>/<timestamp>/artifacts/` (Greenfield fixture만)
3. **기능 검증** → fixture 디렉토리의 `verify.py` 가 존재하면 산출 코드를 실제로 실행. exit 0 = functional PASS. 로그는 `runs/.../verify.log` 로 저장.
4. 오라클 비교 + metrics.json 기록

출력 전체를 보관해 Step 4 에서 활용.

### Step 4 — 결과 요약

사용자에게 다음 섹션을 출력:

```markdown
## 평가 결과: <fixture>

- **Oracle**: <passed>/<total> 체크 통과
- **LOOPBACK**: <loopback_count> 회 (phase별: <loopback_per_phase>)
- **RTM**: 총 <total_reqs>개 REQ 중 <result_pass>개 PASS, Unit TC <u>/<n>, Impl <i>/<n>
- **P8 Review**: CRITICAL <c>, MAJOR <m>, MINOR <mn>
- **Functional**: OK / FAIL (exit=<n>)   ← 산출 코드 실제 실행 결과
- **Archive**: workflow-tests/runs/<fixture>/<timestamp>/
```

FAIL 체크가 있으면 별도 "실패 항목" 블록으로 나열:

```markdown
### 실패한 Oracle 체크
- [FAIL] total_reqs >= 3  (actual=2)
- [FAIL] artifact exists: reports/*-completion.md  (matches=0)
```

### Step 5 — 다음 단계 제안

| 상황 | 제안 |
|---|---|
| 전체 PASS + baseline 없음 + `--baseline` 미사용 | "결과가 합리적이면 `/halo-eval <fixture> --baseline` 으로 기준점 저장" |
| 전체 PASS + baseline 이미 있음 | "`/halo-eval compare <fixture>` 로 baseline과 차이 확인" |
| FAIL 존재 | "실패 체크를 확인하고 워크플로우 프롬프트 (`.claude/commands/halo-workflow.md`) 를 조정하세요" |

---

## 출력 규칙

- **[RUN]의 Step 2 워크플로우 실행 중**에는 일반 `/halo-workflow` 와 동일한 상세 로그를 보여줄 것 (Phase 시작/완료, RTM 업데이트 등).
- **Step 4 ~ 5**는 간결하게. 장황한 서술 금지.
- 스크립트 (`evaluate.py`, `compare.py`) 의 원본 출력은 그대로 보여준 뒤, 그 아래 요약을 덧붙이는 방식.

---

## 주의사항

- **[RUN] 은 긴 작업**: P1 ~ P9 전체 수행으로 수십 분 걸릴 수 있음. 사용자에게 시작 전에 이 사실을 알릴 것.
- **비결정성**: 1회 실행만으로 baseline을 확정하지 말 것. 최소 2~3회 돌려 일관성을 본 뒤 저장 권장.
- **Brownfield fixture**: 현재는 Greenfield 만 완전 지원 (산출물 자동 이동이 Greenfield 한정). Brownfield fixture 는 평가는 되지만 워크스페이스 정리는 수동.
- **`.workflow/state.json` 이 이미 존재**하면 워크플로우가 이어서 진행하려 할 수 있음. Step 1의 클린 검증이 이를 차단.

---

## NOW EXECUTING...

**Input**: `$ARGUMENTS`

위 인자 파싱 규칙에 따라 해당 섹션을 수행하라.
