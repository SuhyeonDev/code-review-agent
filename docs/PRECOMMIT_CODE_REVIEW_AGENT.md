# Pre-commit 코드리뷰 Agent

## 0. 기술 스택
- Agent 실행: Python 3 CLI (`tools/code-review-agent/code_review_agent.py`)
- 개발 도구: Codex app, Git(`git diff --cached`)
- 백엔드 샘플: Spring Boot, MyBatis, MariaDB
- 프론트엔드 샘플: React 18(TypeScript 미사용)

## 1. 목적
- 커밋 전에 불필요 코드와 잠재 리스크를 빠르게 식별한다.
- 코드리뷰 결과에 `TODO/FIXME` 경로별 리스트를 포함해, 개발자가 남은 할일 또는 문의사항을 빠르게 정리하도록 돕는다.
- 즉시 수정 가능한 항목(Rule Engine)과 문맥 기반 리스크(Review Engine)를 분리해 리뷰 품질을 높인다.

## 2. 범위
- 입력 범위: `--paths <경로>` 또는 `--staged`
- 분석 범위: 금지 패턴, 작업 태그(`TODO/FIXME`), 주석 코드 휴리스틱
- 현재 상태: Step 0~2 완료(정적 점검 + 경로별 태그 그룹화)

### 산출물(실제 예시)
| 산출물 | 설명 | 예시 |
| --- | --- | --- |
| 코드리뷰 리포트 | `ERROR`/`WARN` 요약과 상세 라인 출력 | ``sample/frontend/pages/ReviewPlaygroundPage.jsx:11 [ERROR] console.log`` |
| 경로별 작업 태그 리스트 | `backend/frontend/db/other` 그룹으로 `TODO/FIXME` 정리 | ``### backend``, ``UserService.java:49 FIXME`` |
| 종료 코드 | 훅/CI 연동용 상태 코드 | `0`(정상), `1`(오류 존재), `2`(인자 오류) |

### 0번 추가 후 문서 구성 판단
- `기술 스택` 추가만으로 기존 섹션을 제거하면 안 된다.
- 유지 필요: `목적`, `아키텍처`, `실행`, `단계 진행 현황` (운영/협업에 직접 필요)
- 축약 가능: 기존의 장문형 "남은 단계 상세 계획" (중복 설명이 많음)

## 3. 아키텍처
1. Collect
- 입력: `git diff --cached` 또는 지정 경로
- 출력: 검사 대상 파일 목록
- 설명: 리뷰 대상을 최소화해 점검 속도와 정확도를 유지한다.

2. Rule Engine
- 금지 패턴 탐지
- 작업 태그(`TODO`, `FIXME`) 수집
- 주석 처리된 코드 휴리스틱 탐지
- 설명: 빠른 정적 점검으로 즉시 수정 가능한 문제를 먼저 걸러낸다.

3. Review Engine
- LLM으로 버그/SQL/null/비동기 예외 처리 리스크 분석
- Finding 스키마: `severity`, `file`, `line`, `reason`, `fix`
- 설명: Rule Engine이 놓치기 쉬운 논리/컨텍스트 기반 리스크를 보완한다.

4. Gate
- 정책 기반 판정: `block` / `warn`
- 설명: 결과를 커밋/PR 품질 기준으로 연결한다.

## 4. 규칙 요약
| 항목 | 기존 | 현재 |
| --- | --- | --- |
| `TODO`/`FIXME` 수집 | 모든 라인 | 주석 라인(`//`, `#`, `--`, `/*`, `*`, `<!--`)만 수집 |
| `debugger` | `ERROR` | `ERROR` |
| `console.log` | `ERROR` | `ERROR` |
| `System.out.println` | `WARN` | `WARN` |
| `printStackTrace` | `WARN` | `WARN` |
| 주석 코드 휴리스틱 | `WARN` | `WARN` |

## 5. 실행
1. 경로 스캔
- `python3 tools/code-review-agent/code_review_agent.py --paths <경로>`

2. staged 스캔
- `python3 tools/code-review-agent/code_review_agent.py --staged`

3. 종료 코드
- `0`: 오류 없음
- `1`: 오류 존재
- `2`: 실행 인자 오류

## 6. 단계별 진행 현황
| 단계 | 목표 | 현재 상태 | 근거 파일 | 남은 작업 |
| --- | --- | --- | --- | --- |
| Step 0 | 샘플 프로젝트 구성 | 완료 | `sample/backend`, `sample/frontend`, `sample/db` | 없음 |
| Step 1 | 정적 규칙 점검기 | 완료 | `tools/code-review-agent/code_review_agent.py` | 규칙별 ignore 옵션 추가 |
| Step 2 | TODO/FIXME 경로별 수집 | 완료 | `tools/code-review-agent/code_review_agent.py` (`_group_todos`) | 출력 형식(JSON/Markdown 선택) |
| Step 3 | 리뷰 번들 생성 | 미진행 | 없음 | `review_bundle.json` 생성기 구현 |
| Step 4 | LLM 리뷰 Finding 생성 | 미진행 | 없음 | Finding 생성 프롬프트/출력 파서 구현 |
| Step 5 | Gate + Hook/CI 연동 | 미진행 | 없음 | pre-commit hook, CI workflow 추가 |
| Step 6 | 프로젝트별 규칙 설정 | 미진행 | 없음 | `code-review-agent.config.json` 로더 구현 |

## 7. 추가 적용 예정 사항
| 항목 | 확인 기준 | 상태 |
| --- | --- | --- |
| Rule 결과 신뢰도 | 문서/비코드 파일 오탐 비율이 허용 범위 이내 | 진행 중 |
| TODO/FIXME 활용성 | 경로별 리스트만 보고 남은 할일 및 문의 항목 정리 가능 | 진행 중 |
| LLM 리뷰 파이프라인 | Finding 스키마 고정(`severity/file/line/reason/fix`) | 미진행 |
| CI 연동 | PR 체크에서 자동 실행 및 결과 게시 | 미진행 |
