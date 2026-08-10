# HarnessWiki 검증 가이드

회의 수집(ingest) 후 두 가지 검증을 수행합니다:

1. **기계 검증** — Lint 스크립트 (Python)
2. **컨텐츠 검증** — LLM 리뷰 스킬 (Claude)

## 사용 흐름

```
회의 메모 제공
    ↓
/ingest 스킬 실행 (회의 수집)
    ↓
✅ /lint 실행 (기계 검증) ← 이 문서
    ↓
✅ /content-review 실행 (컨텐츠 검증) ← 이 문서
    ↓
발견 사항 검토 및 수정
    ↓
git commit
```

---

## 1️⃣ 기계 검증 (Lint Script)

### 개요
자동 검증 (TypeScript 또는 Python):
- Frontmatter YAML 유효성
- 파일 구조 규칙 (경로, 폴더명)
- 파일명 규칙 (kebab-case)
- 링크 유효성 (존재 여부, 깊이)

### 실행 방법

#### TypeScript 버전 (권장)
```bash
# npm 스크립트 사용 (프로젝트 루트에서)
npm run lint

# 또는 직접 실행
npx tsx scripts/lint.ts
```

#### Python 버전 (대체)
```bash
# 프로젝트 루트에서
python scripts/lint.py

# 또는 특정 경로 지정
python scripts/lint.py D:\HarnessWiki
```

#### Claude Code에서 실행
```bash
! npm run lint
! npx tsx scripts/lint.ts
! python scripts/lint.py
```

### 출력 예시

```
🔍 HarnessWiki 기계 검증 시작...

============================================================
검증 완료
============================================================

❌ 오류 (0건):

⚠️  경고 (1건):
  ⚠️  wiki/index.md: 토픽 '모바일-앱'이 index에 없음 (고아 페이지)

ℹ️  정보 (42건):
  ℹ️  raw/2026-06-11_제품주간회의/raw.md: Frontmatter 유효
  ... 외 41건

📊 요약:
  - 오류: 0건
  - 경고: 1건
  - 정보: 42건
```

### 종료 코드
- `0`: 성공 (오류 없음)
- `1`: 오류 발생 (수정 필요)

### 주의사항
- **오류**는 반드시 수정 필요
- **경고**는 검토 후 판단 (대부분 수정 필요)
- **정보**는 참고용 (정상 작동 확인)

---

## 2️⃣ 컨텐츠 검증 (LLM Review Skill)

### 개요
Claude가 수행하는 검증:
1. 일치도 — 회의록 ↔ 위키 일치도
2. 할루시네이션 — 회의에 없는 정보 추가 여부
3. 누락 — 중요 내용 빠짐 여부
4. 액션 추적 — 액션아이템 상태 변화 추적
5. 메타정보/링크 — frontmatter, 링크, 롤업 확인

### 실행 방법

```bash
/content-review 2026-06-11
```

#### 옵션

```bash
# 특정 토픽만 검증
/content-review 2026-06-11 --focus=결제-연동,온보딩-개선

# 엄격 모드 (작은 불일치도 플래그)
/content-review 2026-06-11 --strict

# 상세 출력
/content-review 2026-06-11 --verbose

# 조합
/content-review 2026-06-11 --strict --verbose
```

### 출력 예시

```
====================================================================
                  HarnessWiki 컨텐츠 검증 리포트
====================================================================

회의: 2026-06-11 제품 주간회의
검증 일시: 2026-08-10
검증자: Claude

====================================================================
                           검증 결과
====================================================================

1. 일치도 (Content Alignment)        ✅ PASS
   - 토픽별 일치도: 결제-연동 ✅ / 정산-주기 ✅ / 온보딩-개선 ✅

2. 할루시네이션 (No Hallucination)   ✅ PASS
   - 모든 정보 출처 명확, 회의 내용 범위 내

3. 누락 (Completeness)              ✅ PASS
   - 주요 결정/액션/보류 모두 반영

4. 액션 추적 (Action Lifecycle)     ✅ PASS
   - 상태 변화 명확, 기한 업데이트 정확

5. 메타정보/링크 (Meta & Links)     ✅ PASS
   - 메타정보 완전, 링크 유효, 롤업 완료

====================================================================
                             최종 판정
====================================================================

✅ APPROVED — 이 ingest는 기준을 충족합니다.
```

### 판정 결과

- **✅ APPROVED** — 기준 충족, 바로 커밋 가능
- **⚠️ REVIEW NEEDED** — 발견 사항 검토 후 수정 필요
- **❌ FAILED** — 심각한 문제, 재ingest 또는 수정 필요

### 발견 사항별 대응

#### ✅ PASS (통과)
→ 그냥 진행

#### ⚠️ WARNING (경고)
→ 발견 사항 확인 후 수정 여부 판단
- 예: 부분 일치, 의역, 누락된 세부사항

수정 방법:
1. 해당 파일 열기 (토픽 페이지 또는 롤업 파일)
2. 내용 추가/수정
3. 커밋 (커밋 메시지에 "[REVIEW FIX]" 태그)
4. `/content-review 2026-06-11 --verbose` 재실행

#### ❌ ERROR (오류)
→ 심각한 불일치, 반드시 수정

수정 방법:
1. 원본 회의록(raw.md) 재검토
2. 잘못된 정보 제거 또는 수정
3. 누락된 정보 추가
4. 커밋 (커밋 메시지에 "[REVIEW FIX]" 태그)
5. `/content-review 재실행

---

## 검증 실패 시 대응

### Lint 오류 해결

#### 파일명 규칙 오류
```
❌ raw/2026-06-11-제품주간회의: 폴더명 형식 오류: YYYY-MM-DD_슬러그 형식 필요
```

해결: 폴더명을 `2026-06-11_제품주간회의`로 변경

#### 슬러그 kebab-case 오류
```
❌ raw/2026-06-11_제품_주간회의: 슬러그 '제품_주간회의'가 kebab-case 아님
```

해결: 슬러그를 `제품-주간-회의`로 변경 (하이픈 사용, 언더스코어 제거)

#### Frontmatter YAML 문법 오류
```
❌ wiki/topics/결제-연동/결제-연동.md: Frontmatter YAML 문법 오류
```

해결: YAML 문법 확인
```yaml
---
updated: 2026-06-11  # 올바른 형식
topics:              # 올바른 형식
  - 주제1
  - 주제2
---
```

#### 깨진 링크
```
❌ wiki/topics/결제-연동/결제-연동.md: 링크가 가리키는 파일 없음: ../../../raw/2026-06-11_제품주간회의/meta.md
```

해결: 링크 경로 확인 및 수정

### Content Review 오류 해결

#### 일치도 불일치
```
⚠️ 토픽: 정산-주기 ⚠️
- 회의 내용: "주 1회 정산 vs 월 1회 정산"
- 위키 반영: "월 1회 정책" — 부분 일치
```

해결: 토픽 페이지의 결정사항 섹션에 내용 추가

#### 할루시네이션 발견
```
❌ 위키: "사용자 조사 실시 필요"
- 출처: raw.md에서 확인 불가
```

해결: 해당 내용 제거 또는 해석이 맞다면 각주 추가

#### 액션아이템 누락
```
❌ 액션: "박준서 — A사 테스트 계정 발급"
- 회의 내용에는 있으나 action-items.md에 없음
```

해결: action-items.md에 액션 추가

---

## 검증 통과 후

### 커밋 메시지 예시

```
[INGEST] 2026-06-11 제품 주간회의 적재

- 결제 연동 목표 재연기 (6월 중순 → 7월 초)
- 정산 주기 결론 보류
- 온보딩 3단계 42% 이탈률 발견 → A/B 테스트 진행

✅ 검증 완료: lint 통과, content-review APPROVED

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 발견 사항 수정 후 커밋

```
[REVIEW FIX] 2026-06-11 제품 주간회의 — 검증 지적사항 수정

- 정산-주기: 고객사별 차등 정책 섹션 추가
- action-items.md: 누락된 액션 2건 추가
- index.md: 새 토픽 링크 추가

✅ 재검증 완료: content-review APPROVED

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 주기 및 팁

### 추천 검증 주기
- **매 ingest 직후**: 필수 (lint + content-review)
- **주 1회**: 전체 위키 lint 스캔 (누적 오류 방지)

### 성능 팁
- TypeScript lint: ~1-2초 (npm 시작 오버헤드 포함)
- Python lint: ~0.5초 (가장 빠름)
- content-review: ~2-5분 (회의 복잡도에 따라)
- 병렬 실행 불가 (순차 실행 권장)

### TypeScript vs Python 선택
| 항목 | TypeScript | Python |
|------|-----------|--------|
| 설정 | npm install 필요 | pyyaml만 설치 |
| 속도 | ~1-2초 | ~0.5초 |
| 장점 | Node.js 생태계, 타입 안전 | 가볍고 빠름 |
| 선택 | CI/CD 통합할 때 | 로컬에서만 실행할 때 |

### 자동화 옵션

#### Claude Code 스크립트 자동화 (권장)
`.claude/hooks/` 또는 settings.json에 설정:
```json
{
  "hooks": {
    "after-ingest": "npm run lint"
  }
}
```

#### npm watch 모드
파일 변경 감지 시 자동 검증:
```bash
npm run lint:watch
```

#### 컴파일 및 배포
```bash
# TypeScript를 JavaScript로 컴파일
npm run lint:build

# 생성된 dist/ 폴더에서 실행
node dist/scripts/lint.js
```

---

## 참고

- 스크립트 위치: `scripts/lint.py`
- 스킬 위치: `.claude/skills/content-review/`
- 스키마 문서: `AGENTS.md`
- 발견된 이슈 기록: `log.md`에 `[LINT]` 또는 `[REVIEW]` 태그로 기록
