#!/usr/bin/env python3
"""
HarnessWiki 링크 검증 스크립트

용도:
  1. 깨진 링크 탐지 (존재하지 않는 파일)
  2. 깊이 불일치 감지 (raw는 3단계 깊이, 형제 토픽은 상대경로)
  3. 형식 오류 감지 (절대경로, Obsidian 위키링크 등)

사용법:
  python check_links.py <wiki-path> [--strict] [--verbose]

예:
  python check_links.py D:\HarnessWiki\wiki --strict
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict


def parse_links(content: str) -> List[str]:
    """마크다운에서 모든 상대경로 링크 추출"""
    # 마크다운 링크: [text](path)
    markdown_links = re.findall(r'\[.*?\]\((.*?)\)', content)

    # Obsidian 위키링크 감지: [[text]] (금지)
    obsidian_links = re.findall(r'\[\[(.*?)\]\]', content)

    return markdown_links, obsidian_links


def validate_link_depth(link: str, source_path: Path) -> Tuple[bool, str]:
    """
    링크의 깊이가 규칙을 따르는지 검증

    규칙:
    - raw 참조: ../../../raw/ (3단계)
    - 형제 토픽: ../<slug>/ (상대경로)

    반환: (유효성, 메시지)
    """

    # 절대경로 감지
    if link.startswith('/') or ':' in link:
        return False, f"절대경로 사용 금지: {link}"

    # Obsidian 위키링크 감지 (여기서는 하지 않음, 별도 검사)
    if '[[' in link:
        return False, f"Obsidian 위키링크 금지: {link}"

    # raw 참조 검증
    if 'raw/' in link:
        # raw는 3단계 깊이여야 함
        parts = link.split('/')
        raw_index = parts.index('raw')

        # ../../../raw/ 형태 확인 (앞에 3개의 ../)
        dots_count = len([p for p in parts[:raw_index] if p == '..'])

        if dots_count != 3:
            return False, f"raw 참조는 3단계 깊이여야 함: {link} (현재 {dots_count}단계)"

        return True, "유효 (raw 3단계)"

    # 형제 토픽 참조 검증
    if 'topics/' in link and '.md' in link:
        # ../slug/slug.md 형태 확인
        if link.count('..') < 1:
            return False, f"형제 토픽은 상대경로여야 함: {link}"

        return True, "유효 (형제 토픽 상대경로)"

    # 기타 상대경로는 경고만
    return True, "상대경로 (기타)"


def check_link_target(link: str, source_path: Path) -> Tuple[bool, str]:
    """
    링크가 실제로 존재하는 파일을 가리키는지 확인

    반환: (존재 여부, 메시지)
    """

    # 앵커(#) 제거
    if '#' in link:
        link = link.split('#')[0]

    # 상대경로를 절대경로로 변환
    target_path = (source_path.parent / link).resolve()

    if target_path.exists():
        return True, f"유효 → {target_path}"
    else:
        return False, f"파일 없음: {target_path}"


def scan_wiki(wiki_path: str) -> Dict[str, List[Dict]]:
    """
    wiki 디렉토리 스캔하여 모든 링크 검증

    반환:
    {
        "broken_links": [...],
        "depth_mismatches": [...],
        "obsidian_links": [...],
        "valid_links": [...]
    }
    """

    wiki_root = Path(wiki_path)

    results = {
        "broken_links": [],
        "depth_mismatches": [],
        "obsidian_links": [],
        "valid_links": []
    }

    # 모든 .md 파일 탐색
    for md_file in wiki_root.rglob("*.md"):

        # _templates 제외
        if "_templates" in str(md_file):
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️  {md_file} 읽기 실패: {e}")
            continue

        # 링크 추출
        markdown_links, obsidian_links = parse_links(content)

        # Obsidian 위키링크 기록
        for link in obsidian_links:
            results["obsidian_links"].append({
                "file": str(md_file),
                "link": link
            })

        # 마크다운 링크 검증
        for link in markdown_links:

            # 절대경로나 외부 링크는 스킵
            if link.startswith('http') or link.startswith('/'):
                continue

            # 깊이 검증
            depth_valid, depth_msg = validate_link_depth(link, md_file)

            if not depth_valid:
                results["depth_mismatches"].append({
                    "file": str(md_file),
                    "link": link,
                    "issue": depth_msg
                })
                continue

            # 파일 존재 검증
            target_valid, target_msg = check_link_target(link, md_file)

            if not target_valid:
                results["broken_links"].append({
                    "file": str(md_file),
                    "link": link,
                    "issue": target_msg
                })
            else:
                results["valid_links"].append({
                    "file": str(md_file),
                    "link": link
                })

    return results


def report(results: Dict, verbose: bool = False) -> int:
    """
    결과 보고 및 종료 코드 반환

    반환: 0 (완료), 1 (이슈 있음)
    """

    print("\n" + "="*60)
    print("HarnessWiki 링크 검증 결과")
    print("="*60 + "\n")

    # 깨진 링크
    if results["broken_links"]:
        print(f"❌ 깨진 링크 ({len(results['broken_links'])}건):\n")
        for item in results["broken_links"]:
            print(f"   파일: {item['file']}")
            print(f"   링크: {item['link']}")
            print(f"   문제: {item['issue']}\n")
    else:
        print("✅ 깨진 링크: 0건\n")

    # 깊이 불일치
    if results["depth_mismatches"]:
        print(f"⚠️  깊이 불일치 ({len(results['depth_mismatches'])}건):\n")
        for item in results["depth_mismatches"]:
            print(f"   파일: {item['file']}")
            print(f"   링크: {item['link']}")
            print(f"   문제: {item['issue']}\n")
    else:
        print("✅ 깊이 불일치: 0건\n")

    # Obsidian 위키링크
    if results["obsidian_links"]:
        print(f"❌ Obsidian 위키링크 금지 ({len(results['obsidian_links'])}건):\n")
        for item in results["obsidian_links"]:
            print(f"   파일: {item['file']}")
            print(f"   링크: [[{item['link']}]]\n")
    else:
        print("✅ Obsidian 위키링크: 0건\n")

    # 유효한 링크 (verbose)
    if verbose and results["valid_links"]:
        print(f"✅ 유효한 링크 ({len(results['valid_links'])}건): 생략\n")

    # 종료 코드
    has_issues = bool(
        results["broken_links"] or
        results["depth_mismatches"] or
        results["obsidian_links"]
    )

    print("="*60)
    if has_issues:
        print("⚠️  이슈 발견. 위를 참고하여 수정하세요.")
        print("="*60)
        return 1
    else:
        print("✅ 모든 링크 유효!")
        print("="*60)
        return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python check_links.py <wiki-path> [--verbose]")
        sys.exit(1)

    wiki_path = sys.argv[1]
    verbose = "--verbose" in sys.argv

    if not os.path.isdir(wiki_path):
        print(f"❌ 경로 없음: {wiki_path}")
        sys.exit(1)

    results = scan_wiki(wiki_path)
    exit_code = report(results, verbose)

    sys.exit(exit_code)
