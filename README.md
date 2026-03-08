# agent

Pre-commit 코드리뷰 에이전트 개발 레포지토리

## 목표
- 커밋 전 불필요 코드 탐지
- 경로별 작업 태그 수집
- 리뷰 리스크(버그/SQL/null/예외 처리) 확인

## 디렉터리 구조
- `docs/PRECOMMIT_CODE_REVIEW_AGENT.md`: 아키텍처/규칙/실행 방법
- `tools/code-review-agent/`: CLI 점검기
- `sample/backend/`: Spring Boot + MyBatis 샘플
- `sample/frontend/`: React 샘플
- `sample/db/`: DB 안내 문서

## 빠른 시작
1. 전체 샘플 스캔
- `python3 tools/code-review-agent/code_review_agent.py --paths sample`
2. staged 파일 스캔
- `python3 tools/code-review-agent/code_review_agent.py --staged`

## 결과 해석
- `ERROR`: 즉시 수정 권장
- `WARN`: 리뷰 대상
- 종료 코드 `0/1/2`: 정상/오류 발견/인자 오류


## 단계 진행 요약
| 단계 | 상태 | 비고 |
| --- | --- | --- |
| Step 0 샘플 구성 | 완료 | 백엔드/프론트/DB 생성 |
| Step 1 규칙 점검기 | 완료 | CLI 동작 및 오류/경고 분류 |
| Step 2 태그 수집 | 완료 | `backend/frontend/db/other` 그룹 |
| Step 3 번들 생성 | 미진행 | `review_bundle.json` 필요 |
| Step 4 LLM 리뷰 | 미진행 | Finding 생성 파이프라인 필요 |
| Step 5 Gate/CI | 미진행 | pre-commit/CI 연동 필요 |
| Step 6 설정 확장 | 미진행 | config 로더 필요 |

상세 계획은 `docs/PRECOMMIT_CODE_REVIEW_AGENT.md`의 `6~7` 절을 기준으로 진행한다.
