# 핸드오버: wiki/ 디렉토리 구조 전환 (폴더 노트화)

**작업 일시**: 2026-08-10  
**담당**: Claude Code (AI Assistant)  
**상태**: ✅ 완료

---

## 작업 개요

HarnessWiki의 `wiki/` 디렉토리를 **평면 구조 → 폴더 노트(folder note) 구조**로 전환했습니다.

### 변경 전/후

| 항목 | 이전 | 새로운 |
|---|---|---|
| 토픽 페이지 | `wiki/topics/슬러그.md` | `wiki/topics/슬러그/슬러그.md` |
| 결정사항 롤업 | `wiki/decisions.md` | `wiki/decisions/decisions.md` |
| 액션아이템 롤업 | `wiki/액션아이템.md` | `wiki/액션아이템/액션아이템.md` |
| Obsidian 네비게이션 | 파일만 가능 | 폴더+파일 동시 표현 가능 (폴더 클릭 → 해당 페이지 열림) |

---

## 상세 작업 내용

### 1단계: 파일 이동 (8건)

새 폴더를 생성하고 파일을 이동:

```
wiki/액션아이템/액션아이템.md
wiki/decisions/decisions.md
wiki/topics/결제-연동/결제-연동.md
wiki/topics/대시보드-개편/대시보드-개편.md
wiki/topics/로드맵/로드맵.md
wiki/topics/백엔드-채용/백엔드-채용.md
wiki/topics/온보딩-개선/온보딩-개선.md
wiki/topics/정산-주기/정산-주기.md
```

### 2단계: 상대링크 재계산 (9개 파일)

각 파일의 상대경로가 변경되었으므로 내부 링크를 모두 갱신:

#### index.md (8개 링크)
- `wiki/topics/로드맵.md` → `wiki/topics/로드맵/로드맵.md`
- `wiki/topics/온보딩-개선.md` → `wiki/topics/온보딩-개선/온보딩-개선.md`
- (기타 6개 토픽 페이지)
- `wiki/decisions.md` → `wiki/decisions/decisions.md`
- `wiki/액션아이템.md` → `wiki/액션아이템/액션아이템.md`

#### wiki/decisions/decisions.md (17개 링크)
- 예: `./topics/결제-연동.md` → `../topics/결제-연동/결제-연동.md`
- 토픽 페이지로의 모든 링크 깊이 조정

#### wiki/액션아이템/액션아이템.md (11개 링크)
- 예: `../raw/2026-07-23-제품주간회의/meta.md` → `../../raw/2026-07-23-제품주간회의/meta.md`
- raw/ 링크가 한 단계 더 깊어짐

#### wiki/topics/X/X.md (각 토픽, 총 ~20개 링크)
- raw 링크: `../../raw/...` → `../../../raw/...`
- 형제 토픽 링크: `./로드맵.md` → `../로드맵/로드맵.md`

### 3단계: 스키마 문서 갱신

#### CLAUDE.md
- **라인 41**: `wiki/topics/슬러그.md` → `wiki/topics/슬러그/슬러그.md` (폴더 노트 구조 명시)
- **라인 47-48**: `wiki/decisions.md` → `wiki/decisions/decisions.md`, `wiki/액션아이템.md` → `wiki/액션아이템/액션아이템.md`
- **라인 88**: 액션아이템 롤업 링크 경로 갱신 (`../../raw/...` → `../../../raw/...`)

#### _templates/topic-page.template.md
- **라인 15, 18**: raw 링크 예시 깊이 조정 (`../../raw/` → `../../../raw/`)
- **라인 27**: raw 링크 예시 깊이 조정
- **라인 40-42**: 토픽 간 링크 및 롤업 링크 예시 갱신
  - `../topics/다른-주제.md` → `../다른-주제/다른-주제.md`
  - `../decisions.md` → `../../decisions/decisions.md`
  - `../액션아이템.md` → `../../액션아이템/액션아이템.md`

#### log.md
- 구조 전환 작업을 `[REFACTOR]` 태그로 기록

---

## 영향 범위

### 변경된 파일 (9개)
- `index.md`
- `wiki/decisions/decisions.md`
- `wiki/액션아이템/액션아이템.md`
- `wiki/topics/결제-연동/결제-연동.md`
- `wiki/topics/대시보드-개편/대시보드-개편.md`
- `wiki/topics/로드맵/로드맵.md`
- `wiki/topics/백엔드-채용/백엔드-채용.md`
- `wiki/topics/온보딩-개선/온보딩-개선.md`
- `wiki/topics/정산-주기/정산-주기.md`

### 스키마 문서 갱신 (3개)
- `CLAUDE.md`
- `_templates/topic-page.template.md`
- `log.md`

### 변경되지 않은 파일
- `raw/` 내 모든 파일 (raw/에서 wiki/로 가는 링크 없음)
- `handover/` (이 문서 제외)

---

## 검증 완료

✅ **구조 검증**
- 8개 폴더 각각 정확히 1개 md 파일 포함
- 옛 평면 경로 패턴 0개 (완전히 제거됨)

✅ **링크 검증**
- index.md: 8개 링크 (모두 `wiki/topics/X/X.md`, `wiki/decisions/decisions.md`, `wiki/액션아이템/액션아이템.md` 형태)
- decisions.md: 17개 토픽 링크 (모두 `../topics/X/X.md` 형태)
- 액션아이템.md: 11개 raw 링크 (모두 `../../raw/...` 형태)
- 각 토픽 페이지: raw 링크 `../../../raw/...`, 형제 토픽 링크 `../X/X.md` 형태

---

## 다음 단계 (신규 회의 수집 시 주의)

### ingest 절차에서 할 일
신규 회의를 추가할 때, LLM(Claude)은 이제 **자동으로** 다음 구조로 페이지를 생성합니다:
- 새 토픽 페이지: `wiki/topics/새-슬러그/새-슬러그.md`
- 기존 토픽 갱신: 같은 폴더 내 파일 편집
- 링크: `../../../raw/...` (raw 참조), `../다른-토픽/다른-토픽.md` (형제 토픽 참조)

### 주의사항
1. **새 토픽 페이지 생성 시** index.md에 `wiki/topics/새-슬러그/새-슬러그.md` 형태로 링크 추가
   - 이전처럼 `wiki/topics/새-슬러그.md` 형태로 하지 말 것
2. **토픽 간 내부 링크**: `../슬러그/슬러그.md` 형태 (같은 topics/ 폴더 내 형제)
3. **raw 참조 시**: `../../../raw/YYYY-MM-DD-슬러그/meta.md` 형태 (3단계 상향)

### CLAUDE.md는 최신 스키마 반영
- `CLAUDE.md`는 이미 새 구조를 문서화했으므로, LLM이 다음 회의 수집 시 참고하면 됨
- 템플릿 `_templates/topic-page.template.md`도 새 링크 패턴으로 업데이트됨

---

## 기술 상세

### Obsidian 폴더 노트 설정
- `.obsidian/core-plugins.json` 에 `note-composer` 플러그인 활성화됨 (이미 설정됨)
- 폴더와 같은 이름의 md 파일 생성 시 자동으로 폴더 노트로 인식
- 파일 탐색기에서 폴더를 클릭 → 해당 슬러그.md 파일이 자동으로 열림

### 왜 이 구조인가?
1. **네비게이션 개선**: 폴더를 열면 자동으로 개요 페이지가 로드됨
2. **미래 확장성**: 폴더 내에 추후 하위 문서 추가 가능 (예: 토픽별 첨부파일, 관련 링크 모음 등)
3. **SSOT 원칙**: 같은 슬러그로 폴더와 파일명을 통일하여 혼동 방지

---

## 작업 로그

| 시간 | 단계 | 상태 |
|---|---|---|
| 계획 | 탐색 + 설계 | ✅ 완료 |
| 실행 | 8개 파일 이동 + 링크 재계산 | ✅ 완료 |
| 검증 | 구조 및 링크 검증 | ✅ 완료 |
| 문서화 | 스키마 문서 + log.md 갱신 | ✅ 완료 |

---

## 연락처 & 질문

이 작업에 대해 의문이나 추가 조정 필요 시:
1. `index.md`를 참고해 전체 위키 카탈로그 확인
2. `CLAUDE.md`의 "오퍼레이션 1: 수집" 섹션을 참고해 신규 회의 적재 방식 확인
3. `_templates/topic-page.template.md`를 참고해 새 주제 페이지 작성 방식 학습
