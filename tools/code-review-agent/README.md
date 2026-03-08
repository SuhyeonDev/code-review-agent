# code-review-agent (v0)

정규식 기반 pre-commit 코드리뷰 에이전트.

## Run

작업 트리(폴더) 스캔:

```bash
python3 tools/code-review-agent/code_review_agent.py --paths sample
```

staged 파일만 스캔:

```bash
python3 tools/code-review-agent/code_review_agent.py --staged
```

## Checks (v0)

- `console.log`, `debugger`
- `System.out.println`, `printStackTrace`
- `TODO`, `FIXME` (주석 라인 전용 탐지)
- 주석 처리된 코드(휴리스틱)

종료 코드:
- `0`: `ERROR` 없음
- `1`: `ERROR` 있음
- `2`: 인자 오류
