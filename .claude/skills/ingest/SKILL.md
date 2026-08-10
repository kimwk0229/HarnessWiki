---
name: ingest-harnesswiki
description: >
  HarnessWiki의 회의록 수집(ingest) 전체 프로세스를 자동화합니다. 새 회의 메모/전사본을 받으면:
  (1) raw/에 원본 저장 (write-once), (2) 주제 페이지 매칭 및 생성, (3) 주제 페이지에 정보 누적,
  (4) 모순 처리 (변경이력 추적), (5) decisions.md 갱신, (6) action-items.md 갱신,
  (7) 모든 링크 검증, (8) log.md 기록, (9) 결과 보고.
  사용자가 회의 메모나 STT 전사본을 제공할 때마다 이 스킬을 사용하세요.
  CLAUDE.md의 "오퍼레이션 1: 수집" 9단계를 완전 자동화합니다.
compatibility:
  requires_tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# HarnessWiki Ingest 스킬

이 스킬은 HarnessWiki에 새 회의 정보를 수집(ingest)하는 전체 프로세스를 자동화합니다.
CLAUDE.md의 "오퍼레이션 1: 수집"에 정의된 9단계를 모두 실행합니다.

## 개요

### 입력
- **회의 메모 또는 STT 전사본**: 사용자가 제공하는 원본 텍스트
- **메타정보** (사용자 확인):
  - 날짜 (YYYY-MM-DD)
  - 제목
  - 참석자 (선택사항)
  - 자료유형 (manual / stt / hybrid)
  - 한 줄 요약

### 출력
- **생성/갱신된 파일 목록**:
  - raw/YYYY-MM-DD_슬러그/raw.md (원본)
  - raw/YYYY-MM-DD_슬러그/meta.md (메타카드)
  - wiki/topics/슬러그/슬러그.md (신규 토픽 또는 기존 갱신)
  - wiki/decisions/decisions.md (갱신)
  - wiki/action-items/action-items.md (갱신)
  - wiki/index.md (신규 토픽 시)
  - log.md (기록)

## 9단계 프로세스

### 1단계: 메타정보 확인
날짜, 제목, 자료유형을 명확히 하기 위해 사용자에게 확인합니다.
- **날짜**: YYYY-MM-DD 형식 (필수)
- **제목**: 회의 제목 (필수)
- **참석자**: 쉼표 구분 이름 (선택)
- **자료유형**: "manual" (수동 메모), "stt" (STT 전사), "hybrid" (혼합)
  - 불명확하면: 체계적인 bullet points → manual, 비유창함/마커 → stt, 혼합 → hybrid

### 2단계: 원본 저장
- `raw/YYYY-MM-DD_슬러그/raw.md`에 원문을 **손대지 않고 그대로** 저장합니다.
- YAML frontmatter 포함:
  ```yaml
  ---
  title: 회의 제목
  date: 2026-08-10
  type: [회의 분류]  # e.g. 주간회의, 주제별회의
  participants:
    - 이름1
    - 이름2
  ---
  ```
- **rule**: 저장 후 절대 수정 금지 (write-once 정책)

- `meta.md` 동시 작성 (같은 폴더):
  ```yaml
  ---
  title: 회의 제목
  date: 2026-08-10
  type: [회의 분류]
  participants:
    - 이름1
    - 이름2
  자료유형: manual
  ---
  
  ## 메타정보
  - **일시**: 2026-08-10
  - **참석자**: 이름1, 이름2
  - **자료유형**: 수동 메모
  - **출처**: [raw.md](raw.md)
  
  ## 한줄 요약
  핵심 내용을 한 문장으로.
  ```

### 3단계: 주제 페이지 매칭
원문에서 핵심 키워드 3-5개를 추출하고, wiki/topics/ 전체를 grep으로 검색합니다.
- 관련된 기존 주제 페이지를 찾음
- 없으면 신규 토픽 생성 (폴더 노트 형식)

**판단 기준**:
- "회의에서 직접 다룬 주제" = 관련 (예: "결제 연동 진행상황" → 결제-연동 토픽)
- "회의에서 언급만 된 주제" = 검토 후 판단 (예: "대시보드는 Q3로" → 대시보드-개편 관련)
- "배경 설명 수준" = 관련 안 함 (예: "작년에 했던 온보딩 개선" 언급만 → 관련 안 함)

### 4단계: 주제 페이지에 정보 누적
각 관련 주제 페이지에 이번 회의의 정보를 추가합니다.

**처리 원칙**:
- **현황/개요 섹션** (overwriteable): 최신 상태로 갱신 가능
- **결정사항 섹션** (append-only): 신규 날짜 블록 추가, 기존 블록 수정 금지
  ```markdown
  ## 결정사항
  
  ### 2026-08-10 (최신)
  - 결정 내용 1
  - 결정 내용 2
  출처: [2026-08-10 제품 주간회의](../../../raw/2026-08-10_제품주간회의/meta.md)
  
  ### 2026-07-23
  - 이전 결정
  ```

- **모순 처리**: 지우지 말고 변경이력 추적
  ```markdown
  ### 2026-08-10 (최신)
  - X 담당: 기존 Y → 현재 Z 변경 ([2026-08-10 회의](../../../raw/2026-08-10_회의슬러그/meta.md))
  ```

- **근거 링크 필수**: 모든 정보에 출처 회의 meta.md 링크 포함
  ```markdown
  출처: [2026-08-10 제품 주간회의](../../../raw/2026-08-10_제품주간회의/meta.md)
  ```

### 5단계: 결정사항 롤업
새 결정사항을 `wiki/decisions/decisions.md`에 반영합니다.

**형식**:
```markdown
## 2026-08-10 제품 주간회의

- [결정1](../topics/주제/주제.md) — 출처: [회의 메타](../../raw/2026-08-10_슬러그/meta.md)
- [결정2](../topics/다른주제/다른주제.md)
```

**rule**: ingest 후 decisions.md 갱신 누락 시 SSOT 깨짐. 필수.

### 6단계: 액션아이템 롤업
새 액션아이템을 `wiki/action-items/action-items.md`에 체크박스 형태로 추가합니다.

**형식**:
```markdown
## 2026-08-10 제품 주간회의

- [ ] 액션 내용 (담당자, 기한 if 있으면 자유 형식) — 출처: [회의 메타](../../raw/2026-08-10_슬러그/meta.md)
```

**rule**: ingest 후 action-items.md 갱신 누락 시 SSOT 깨짐. 필수.

### 7단계: 링크 유효성 검증
신규 추가한 모든 링크가 실제 파일을 가리키는지 확인합니다.

**검증 항목**:
- **raw 참조**: 항상 `../../../raw/YYYY-MM-DD_슬러그/meta.md` (3단계 깊이)
- **형제 토픽**: 항상 `../슬러그/슬러그.md` (상대경로)
- **결정 롤업**: `../topics/슬러그/슬러그.md`
- **액션 롤업**: `../../raw/YYYY-MM-DD_슬러그/meta.md`

**rule**: 깨진 링크로 ingest 완료 금지.

### 8단계: 로그 업데이트
`log.md`에 `[INGEST]` 항목을 추가합니다.

**형식**:
```markdown
- [INGEST] 2026-08-10 제품 주간회의 적재 완료. 갱신 페이지: 결제-연동, 정산-주기. decisions.md/action-items.md 갱신.
```

### 9단계: 사용자에게 보고
처리 완료 후 다음을 보고합니다:
- 생성된 파일: raw/YYYY-MM-DD_슬러그/, meta.md
- 갱신된 토픽 페이지 목록
- 신규 생성된 토픽 페이지 (있으면)
- decisions.md, action-items.md 갱신 여부
- 식별된 이슈 (깨진 링크 등)

## 참고 자료

신규 토픽 생성 시 폴더 노트 구조 확인: `references/file-formats.md`

엣지 케이스 판단 기준: `references/edge-cases.md`

## 스크립트

**check_links.py**: 경로 깊이 검증 및 깨진 링크 탐지
```bash
python scripts/check_links.py <wiki-path>
```

**slugify.py**: 한글 kebab-case 슬러그 생성 및 중복 감지
```bash
python scripts/slugify.py <제목-텍스트>
```

## 템플릿

`assets/` 디렉토리의 템플릿을 참고하여 파일을 작성합니다:
- `raw-frontmatter.template.md` — raw.md의 frontmatter 형식
- `meta.template.md` — meta.md 전체 구조
- `topic-page.template.md` — 신규 토픽 페이지 기본 구조

## 체크리스트

ingest 완료 전 다음을 반드시 확인하세요:

- [ ] raw.md 저장 완료 (수정 금지, write-once 정책 준수)
- [ ] meta.md 작성 완료 (제목/날짜/자료유형/한 줄 요약 포함)
- [ ] 주제 페이지 신규 생성 시 폴더 노트 구조 준수 (wiki/topics/슬러그/슬러그.md)
- [ ] 모든 링크 경로 검증 (raw: `../../../raw/`, 형제 토픽: `../슬러그/슬러그.md`)
- [ ] 신규 토픽이면 index.md에 등록
- [ ] `wiki/decisions/decisions.md` 동시 갱신
- [ ] `wiki/action-items/action-items.md` 동시 갱신
- [ ] `log.md`에 `[INGEST]` 항목 추가
- [ ] 생성/갱신된 파일 목록을 사용자에게 보고

## 규칙 요약 (DO/DON'T)

### ✅ 꼭 해야 할 규칙

**구조**
- raw.md는 저장 후 절대 수정 금지 (write-once). 오타도 건드리지 말 것.
- 신규 토픽 페이지는 반드시 폴더 노트 형식: `wiki/topics/슬러그/슬러그.md`
- 신규 토픽 생성 후 즉시 `index.md`에 등록

**링크**
- raw 참조: 항상 `../../../raw/YYYY-MM-DD_슬러그/meta.md` (3단계, 일관성)
- 형제 토픽: 항상 `../슬러그/슬러그.md` (상대경로, 일관성)
- ingest 완료 전 모든 신규 링크 검증 (깨진 링크 허용 안 함)

**업데이트**
- ingest 후 반드시 `wiki/decisions/decisions.md` 갱신
- ingest 후 반드시 `wiki/action-items/action-items.md` 갱신
- 기존 내용과 모순되면, 지우지 말고 변경이력 남기기
- `log.md`에 `[INGEST]` 항목 추가

**투명성**
- 주제 페이지에 근거 링크 필수 (어느 회의에서 나온 정보인지)
- meta.md는 회의 원문의 가벼운 카드 역할 (요약, 참석자, 일시 등)

### ❌ 절대 하지 말 규칙

**구조**
- `wiki/topics/슬러그.md` 형식 사용 금지 (평면 구조, 구 형식)
- 같은 주제에 여러 슬러그 페이지 생성 금지

**링크**
- raw 링크를 `../../raw/`, `../../../../raw/` 등으로 섞어 쓰기 금지
- Obsidian `[[위키링크]]` 사용 금지

**raw.md**
- raw.md 저장 후 수정 금지 (오타 포함)

**업데이트**
- ingest 후 decisions.md, action-items.md 갱신 누락 금지
- 신규 토픽 생성했는데 index.md에 등록 안 함 금지

**동시성**
- 같은 토픽 페이지를 사용자와 LLM이 동시 편집 금지
- ingest 진행 중 그 주제 페이지 사용자 편집 금지
