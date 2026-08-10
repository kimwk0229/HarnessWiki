# 변경 로그

HarnessWiki의 시간순 활동 이력. 최신이 위에 오는 역순(newest first).
`[INGEST]`, `[QUERY]`, `[LINT]` 태그로 각 작업 유형을 표시.

## 2026-08-10

- [REFACTOR] `raw/` → `raw/` 폴더명 변경. 모든 상대링크 업데이트 (CLAUDE.md, index.md, log.md, wiki 페이지 6개, handover 문서 2개).
- [REFACTOR] `wiki/` 디렉토리 구조 전환: 평면 구조 → 폴더 노트 구조. `wiki/topics/슬러그.md` → `wiki/topics/슬러그/슬러그.md`, `wiki/decisions.md` → `wiki/decisions/decisions.md`, `wiki/action-items.md` → `wiki/action-items/action-items.md`. 관련 모든 상대링크 갱신 (index.md, 6개 토픽 페이지, 2개 롤업 페이지, CLAUDE.md, _templates/topic-page.template.md). Obsidian 폴더 노트 기능 지원 개선.
- [INGEST] 2026-05-14, 06-11, 06-25, 07-09, 07-23 회의 적재 완료 (5개 회의). 신규 페이지: 백엔드-채용. 기존 페이지 갱신: 결제-연동, 온보딩-개선, 정산-주기, 로드맵. meta.md 작성 완료. 결정사항·액션아이템 롤업 갱신.
- [INGEST] 2026-04-16 제품 주간회의 적재 완료. 생성 페이지: 결제-연동, 정산-주기, 로드맵, 대시보드-개편, 온보딩-개선 (5개 주제), meta.md 작성, 결정사항·액션아이템 롤업 완료.
- [INIT] 1차 설계 핸드오버 문서 작성. `handover/01_1차-설계-핸드오버.md` 생성.
- [INIT] HarnessWiki 부트스트랩 완료. 초기 디렉토리 구조, CLAUDE.md 스키마, 템플릿 준비.
