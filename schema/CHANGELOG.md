# HarnessWiki 변경 로그 (Changelog)

모든 주요 변경사항을 기록합니다. 형식은 [Keep a Changelog](https://keepachangelog.com/) 기반.

---

## [Unreleased]

### Planned
- 자동 lint 도구 개발 (매월 자동 검증)
- 회의 원문 자동 분류 (키워드 기반)
- 결정사항 타임라인 시각화

---

## [1.2.0] - 2026-08-10

### Added
- **schema/SCHEMA.md**: 기술 명세서 추가
  - 메타데이터 스키마 정의 (frontmatter)
  - 링크 규칙 명확화 (경로 깊이)
  - 파일 생명주기 정의
  - 데이터 무결성 규칙
  - Lint 검증 기준
  - 11개 섹션으로 구조화

- **handover/04_규칙-강화-DO-DON-T-체크리스트.md**: 규칙 강화 문서
  - Ingest 체크리스트 (9항)
  - DO/DON'T 규칙 (28항)
  - 변경 이유 및 통계

- **CLAUDE.md 규칙 강화**:
  - "링크 규칙 (경로 깊이)" 섹션 추가
  - Ingest 체크리스트 (9항) 추가
  - "규칙 (DO/DON'T)" 섹션 신규 (28항)
  - Ingest 단계별 **rule:** 마크 추가
  - 스타일 가이드 강화 (frontmatter, raw.md 포맷)

### Fixed
- 로드맵 페이지 역링크 누락 해결
  - 로드맵 → 정산-주기 링크 추가
  - 설명문: "결제 연동 완료 후 필수 진행 항목 (Q2/Q3)"

### Changed
- 스타일 가이드 업데이트
  - Obsidian `[[위키링크]]` 사용 "절대 금지" 명시
  - frontmatter 권장 필드 명확화 (updated, topics, status)
  - raw.md 권장 섹션 구조 제시

### Verified
- ✅ Lint 재점검 완료 (규칙 강화 후)
  - 고아 페이지: 0건
  - 끊어진 링크: 0건
  - 모순: 0건
  - 역링크 누락: 0건 (해결됨)
  - 오래진 액션아이템: 4건 (플래그, 담당자 연락 필요)
  - index.md 누락: 0건

---

## [1.1.0] - 2026-08-10

### Added
- **handover/03_린트-점검-및-수정-이력.md**: 린트 점검 기록

### Fixed
- Lint 결과 링크 깨짐 5건 수정
- 역링크 누락 3건 추가
- 강태우 계약조건 항목 근거 명확화

### Changed
- decisions.md, action-items.md, 각 토픽 페이지 링크 경로 갱신

---

## [1.0.0] - 2026-08-10

### Added
- **handover/02_wiki-구조-전환-폴더노트화.md**: 폴더 노트 구조 전환 기록
  - 평면 구조 → 폴더 노트 구조 전환
  - 8개 파일 이동
  - 9개 파일의 상대 경로 재계산
  - CLAUDE.md, _templates/ 갱신

### Changed
- wiki/topics 구조 표준화
  - 이전: `wiki/topics/슬러그.md` (평면)
  - 현재: `wiki/topics/슬러그/슬러그.md` (폴더 노트)

- 링크 경로 표준화
  - raw 참조: `../../../raw/...` (3단계)
  - 형제 토픽: `../슬러그/슬러그.md`
  - 결정/액션: `../topics/...` 또는 `../../raw/...`

### Affected Files
- wiki/decisions/decisions.md (이동)
- wiki/action-items/action-items.md (이동)
- wiki/topics/{결제-연동, 대시보드-개편, 로드맵, 온보딩-개선, 정산-주기}/ (전환)
- index.md (링크 갱신)
- CLAUDE.md (구조 문서화)
- _templates/topic-page.template.md (경로 갱신)

---

## [0.1.0] - 2026-08-10

### Added
- **handover/01_1차-설계-핸드오버.md**: 초기 설계 기록
- **CLAUDE.md**: 스키마 및 규칙 정의 (초기)
  - 3계층 구조 (raw/, wiki/, schema)
  - 3가지 오퍼레이션 (Ingest, Query, Lint)
  - 스타일 가이드
  - 핵심 철학

- **index.md**: 위키 카탈로그
- **log.md**: 시간순 변경 이력

### Initial Content
- raw/: 4개 회의 기록 (2026-04-16 ~ 2026-07-23)
  - 2026-04-16 제품 주간회의
  - 2026-05-14 제품 주간회의
  - 2026-06-11 제품 주간회의
  - 2026-06-25 온보딩 개선 회의
  - 2026-07-09 제품 주간회의
  - 2026-07-23 제품 주간회의

- wiki/topics/: 5개 주제 페이지
  - 결제-연동 (Q2 핵심)
  - 온보딩-개선 (CS 피드백 → 프로젝트 완료)
  - 대시보드-개편 (Q3 계획)
  - 로드맵 (Q2/Q3 계획)
  - 정산-주기 (정책 미정)

- wiki/decisions/decisions.md: 결정사항 롤업 (23개)
- wiki/action-items/action-items.md: 액션아이템 롤업 (완료 5건, 미완료 12건)

---

## 스키마 버전 관리

### 버전 번호 규칙

`MAJOR.MINOR.PATCH`

- **MAJOR** (x.0.0): 파일 구조 변경, 메타데이터 스키마 변경, breaking change
- **MINOR** (1.x.0): 신규 섹션/필드 추가, 새로운 규칙 추가 (backward compatible)
- **PATCH** (1.0.x): 문서 개선, 예제 추가, 스타일 가이드 강화

### 마이그레이션 가이드

#### 0.1.0 → 1.0.0 (폴더 노트 전환)
- **영향**: wiki/topics 디렉토리 구조 변경
- **마이그레이션**:
  1. 각 주제별 폴더 생성 (`wiki/topics/슬러그/`)
  2. 기존 .md 파일을 폴더 내로 이동
  3. 모든 상대경로 링크 재계산
  4. index.md 링크 갱신

#### 1.0.0 → 1.1.0 (Lint 개선)
- **영향**: 없음 (backward compatible)
- **신규**: Lint 기준 강화

#### 1.1.0 → 1.2.0 (스키마 정의)
- **영향**: 없음 (backward compatible)
- **신규**: schema/SCHEMA.md 추가, frontmatter 권장사항

---

## 버전별 스키마 특성

### v0.1.0
- ❌ 폴더 노트 미지원 (평면 구조)
- ❌ Lint 기준 미정
- ❌ 메타데이터 스키마 비정식
- ✅ 기본 3계층 구조 정의

### v1.0.0
- ✅ 폴더 노트 구조 적용
- ✅ 링크 경로 표준화
- ✅ CLAUDE.md 정식 정의
- ❌ Lint 도구 미제공

### v1.1.0
- ✅ Lint 기준 확립
- ✅ 링크 검증 완료
- ✅ 역링크 검증 추가
- ❌ 메타데이터 스키마 비정식

### v1.2.0 (현재)
- ✅ schema/SCHEMA.md 추가 (메타데이터 정식 정의)
- ✅ Ingest 체크리스트 (9항)
- ✅ DO/DON'T 규칙 (28항)
- ✅ Lint 검증 완료
- ✅ 모든 문서화 완료

---

## 주요 이정표

| 날짜 | 마일스톤 | 버전 | 상태 |
|---|---|---|---|
| 2026-04-16 | 초기 설계 (1차) | 0.1.0-draft | ✅ |
| 2026-05-14 | 첫 회의 ingest | 0.1.0 | ✅ |
| 2026-06-11 | Lint 점검 시작 | 0.1.0 | ✅ |
| 2026-08-10 | 폴더 노트 전환 | 1.0.0 | ✅ |
| 2026-08-10 | Lint 재점검 | 1.1.0 | ✅ |
| 2026-08-10 | 규칙 강화 + 스키마 정의 | 1.2.0 | ✅ |

---

## 다음 계획 (v2.0.0+)

### 계획 중
- [ ] 자동 lint 도구 (Python script)
- [ ] 메타데이터 검증 스크립트
- [ ] 회의 원문 키워드 자동 분류
- [ ] 결정사항 타임라인 시각화
- [ ] 주간/월간 동향 리포트 자동 생성

### 고려사항
- Obsidian 공식 연동 (아직 미정)
- 다른 팀의 사례 조사
- 인프라 자동화 (CI/CD 파이프라인)

---

## 문서 관리

- **CHANGELOG.md** (이 파일): 스키마/규칙 변경 이력
- **log.md**: 시간순 ingest/query/lint 활동 기록
- **CLAUDE.md**: 현재 규칙 정의 (정식)
- **schema/SCHEMA.md**: 기술 명세 (정식)
- **handover/**: 작업 배경 및 상세 기록

---

**최종 갱신**: 2026-08-10  
**현재 버전**: 1.2.0  
**상태**: Active, Ready for Production
