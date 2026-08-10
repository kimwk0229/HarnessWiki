#!/usr/bin/env python3
"""
HarnessWiki 슬러그 생성 및 검증 스크립트

용도:
  1. 한글 텍스트를 kebab-case 슬러그로 변환
  2. 기존 슬러그와의 중복 검사
  3. 유효한 슬러그 형식 검증

규칙:
  - 소문자만
  - 하이픈으로 단어 구분
  - 숫자/특수문자 제거
  - 버전 번호(v1, v2) 사용 금지
  - 영문 혼합 금지 (한글만)

사용법:
  python slugify.py "회의 제목" [--check <wiki-path>]

예:
  python slugify.py "결제 연동 프로젝트"
  → 결제-연동

  python slugify.py "온보딩 개선" --check D:\HarnessWiki\wiki
  → 온보딩-개선 (중복 확인됨)
"""

import re
from pathlib import Path
from typing import List, Tuple


# 한글 자모음 범위
KOREAN_RANGE = (0xAC00, 0xD7A3)


def is_korean(char: str) -> bool:
    """문자가 한글인지 확인"""
    code = ord(char)
    return KOREAN_RANGE[0] <= code <= KOREAN_RANGE[1]


def is_valid_slug_char(char: str) -> bool:
    """슬러그에 유효한 문자인지 확인"""
    return is_korean(char) or char.isdigit() or char == '-'


def remove_spaces(text: str) -> str:
    """공백을 하이픈으로 변환"""
    # 연속된 공백을 단일 하이픈으로
    text = re.sub(r'\s+', '-', text.strip())
    return text


def remove_special_chars(text: str) -> str:
    """특수문자 제거 (한글, 숫자, 하이픈만 유지)"""
    result = ''.join(c for c in text if is_valid_slug_char(c))

    # 연속된 하이픈을 단일 하이픈으로
    result = re.sub(r'-+', '-', result)

    # 시작/끝의 하이픈 제거
    result = result.strip('-')

    return result


def slugify(text: str) -> str:
    """
    텍스트를 슬러그로 변환

    반환: kebab-case 슬러그
    """

    # 1. 공백을 하이픈으로
    text = remove_spaces(text)

    # 2. 특수문자 제거
    text = remove_special_chars(text)

    # 3. 검증
    if not text:
        raise ValueError("슬러그 변환 실패: 한글 문자가 없거나 모두 제거됨")

    if text != text.lower():
        raise ValueError("슬러그는 소문자여야 함")

    return text


def validate_slug(slug: str) -> Tuple[bool, str]:
    """
    슬러그 형식 검증

    반환: (유효성, 메시지)
    """

    # 빈 문자열
    if not slug:
        return False, "빈 슬러그"

    # 영문 포함 확인
    if any(c.isalpha() and not is_korean(c) for c in slug):
        return False, "영문 포함 금지"

    # 대문자 확인
    if slug != slug.lower():
        return False, "소문자만 사용"

    # 특수문자 확인 (하이픈만 허용)
    if not all(is_korean(c) or c.isdigit() or c == '-' for c in slug):
        return False, "특수문자 포함 금지"

    # 버전 번호 확인
    if re.search(r'(v|ver|version)[-]?(\d+)', slug):
        return False, "버전 번호 사용 금지 (예: v1, v2, version2)"

    # 시작/끝의 하이픈
    if slug.startswith('-') or slug.endswith('-'):
        return False, "시작/끝의 하이픈 제거 필요"

    # 연속된 하이픈
    if '--' in slug:
        return False, "연속된 하이픈 제거 필요"

    return True, "유효한 슬러그"


def find_existing_slugs(wiki_path: str) -> List[str]:
    """
    wiki/topics/ 에서 기존 슬러그 목록 추출

    반환: [슬러그1, 슬러그2, ...]
    """

    wiki_root = Path(wiki_path)
    topics_path = wiki_root / "topics"

    if not topics_path.exists():
        return []

    slugs = []
    for folder in topics_path.iterdir():
        if folder.is_dir() and not folder.name.startswith('.'):
            # 폴더 이름이 슬러그
            slugs.append(folder.name)

    return sorted(slugs)


def check_collision(slug: str, wiki_path: str) -> Tuple[bool, str]:
    """
    슬러그와 기존 슬러그의 충돌 확인

    반환: (충돌 여부, 메시지)
    """

    existing_slugs = find_existing_slugs(wiki_path)

    if slug in existing_slugs:
        return True, f"중복: '{slug}' 이미 존재"

    # 유사도 검사 (간단 버전: 같은 글자 포함 여부)
    similar = [s for s in existing_slugs if slug in s or s in slug]

    if similar:
        return True, f"유사: {', '.join(similar)} (확인 필요)"

    return False, f"충돌 없음 (기존: {len(existing_slugs)}개)"


def report_slug(slug: str, wiki_path: str = None):
    """슬러그 결과 보고"""

    print("\n" + "="*60)
    print("슬러그 생성 결과")
    print("="*60 + "\n")

    # 형식 검증
    valid, msg = validate_slug(slug)
    print(f"형식 검증: {msg}")

    if not valid:
        print("="*60)
        return False

    # 충돌 검사
    if wiki_path:
        collision, msg = check_collision(slug, wiki_path)
        print(f"중복 검사: {msg}")

        if collision:
            print("="*60)
            return False

    # 생성된 슬러그
    print(f"\n생성된 슬러그: {slug}")
    print(f"디렉토리: wiki/topics/{slug}/")
    print(f"파일: wiki/topics/{slug}/{slug}.md")

    print("\n" + "="*60)
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python slugify.py \"제목\" [--check <wiki-path>]")
        sys.exit(1)

    text = sys.argv[1]
    wiki_path = None

    if "--check" in sys.argv:
        check_idx = sys.argv.index("--check")
        if check_idx + 1 < len(sys.argv):
            wiki_path = sys.argv[check_idx + 1]

    try:
        slug = slugify(text)
        success = report_slug(slug, wiki_path)
        sys.exit(0 if success else 1)

    except ValueError as e:
        print(f"\n❌ 오류: {e}")
        sys.exit(1)
