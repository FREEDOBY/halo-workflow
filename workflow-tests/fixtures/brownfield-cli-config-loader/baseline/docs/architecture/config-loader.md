# Architecture: config-loader

## 1. Design Overview
JSON 설정 파일을 메모리 dict 로 로드하는 단일 책임 모듈.

## 2. File Structure

```
src/configloader/
├── __init__.py       # 패키지 마커
├── __main__.py       # CLI 진입점 — `python -m configloader <path>`
└── loader.py         # 핵심 load_config()
```

## 3. Interface Contract

```python
def load_config(path: str | Path) -> dict
```
- Input: 파일 경로
- Output: 파싱된 JSON dict
- Raises:
  - `FileNotFoundError` — 경로 없음
  - `ValueError` — JSON 파싱 실패 (원인 포함)

## 4. Data Flow

```
CLI args → __main__.main() → loader.load_config() → print "k=v" lines → exit code
```

## 5. Integration Points
없음 — 표준 라이브러리만 사용.
