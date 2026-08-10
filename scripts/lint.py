#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HarnessWiki 기계 검증 스크립트 (Lint)

검증 항목:
1. Frontmatter 유효성 (YAML 포맷)
2. 스키마 구조 검증 (경로, 파일명)
3. 파일명 규칙 (kebab-case)
4. 링크 검증 (존재 여부, 경로 깊이)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import yaml
import io

# Windows 인코딩 처리
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class WikiLinter:
    def __init__(self, wiki_root: str = "."):
        self.wiki_root = Path(wiki_root)
        self.errors = []
        self.warnings = []
        self.info = []

    def log_error(self, file_path: str, message: str):
        self.errors.append(f"[ERROR] {file_path}: {message}")

    def log_warning(self, file_path: str, message: str):
        self.warnings.append(f"[WARN]  {file_path}: {message}")

    def log_info(self, file_path: str, message: str):
        self.info.append(f"[INFO]  {file_path}: {message}")

    def is_kebab_case(self, text: str) -> bool:
        """슬러그가 kebab-case 형식인지 확인"""
        # 허용: 소문자, 숫자, 하이픈, 한글, 기타 유니코드 문자
        # 한글은 kebab-case의 예외 허용
        if not text or text.startswith("-") or text.endswith("-"):
            return False
        # 한글 포함 확인
        if re.search(r'[一-鿿가-힯]', text):
            return True  # 한글은 허용
        # 영문+숫자+하이픈만 허용
        return bool(re.match(r"^[a-z0-9-]+$", text))

    def validate_raw_structure(self):
        """raw/ 폴더 구조 검증"""
        raw_dir = self.wiki_root / "raw"
        if not raw_dir.exists():
            self.log_warning("raw/", "디렉토리가 없음")
            return

        for folder in raw_dir.iterdir():
            if not folder.is_dir():
                continue

            folder_name = folder.name
            # YYYY-MM-DD_슬러그 형식 검증
            match = re.match(r"^(\d{4})-(\d{2})-(\d{2})_(.+)$", folder_name)
            if not match:
                self.log_error(f"raw/{folder_name}", "폴더명 형식 오류: YYYY-MM-DD_슬러그 형식 필요")
                continue

            slug = match.group(4)
            if not self.is_kebab_case(slug):
                self.log_error(f"raw/{folder_name}", f"슬러그 '{slug}'가 kebab-case 아님 (허용: 소문자, 숫자, 하이픈)")

            # raw.md, meta.md 존재 확인
            raw_file = folder / "raw.md"
            meta_file = folder / "meta.md"

            if not raw_file.exists():
                self.log_error(f"raw/{folder_name}", "raw.md 파일 없음")
            else:
                self.validate_frontmatter(str(raw_file))

            if not meta_file.exists():
                self.log_error(f"raw/{folder_name}", "meta.md 파일 없음")
            else:
                self.validate_frontmatter(str(meta_file))
                self.validate_meta_structure(meta_file)

    def validate_topic_structure(self):
        """wiki/topics/ 폴더 구조 검증"""
        topics_dir = self.wiki_root / "wiki" / "topics"
        if not topics_dir.exists():
            self.log_warning("wiki/topics/", "디렉토리가 없음")
            return

        for folder in topics_dir.iterdir():
            if not folder.is_dir():
                continue

            slug = folder.name
            if not self.is_kebab_case(slug):
                self.log_error(f"wiki/topics/{slug}", f"슬러그가 kebab-case 아님")

            # 폴더 노트 구조 검증: wiki/topics/슬러그/슬러그.md
            expected_file = folder / f"{slug}.md"
            if not expected_file.exists():
                self.log_error(f"wiki/topics/{slug}", f"파일 '{slug}.md' 없음 (폴더 노트 구조 필요)")
            else:
                self.validate_frontmatter(str(expected_file))
                self.validate_topic_links(expected_file, slug)

            # 파일이 폴더명과 다르면 경고
            for file in folder.glob("*.md"):
                if file.name != f"{slug}.md" and file.name != "index.md":
                    self.log_warning(f"wiki/topics/{slug}/{file.name}", "폴더명과 일치하지 않는 파일명")

    def validate_frontmatter(self, file_path: str):
        """Frontmatter YAML 유효성 검증"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.startswith("---"):
                    # YAML frontmatter 추출
                    end_index = content.find("---", 3)
                    if end_index != -1:
                        frontmatter_text = content[3:end_index].strip()
                        try:
                            yaml.safe_load(frontmatter_text)
                            self.log_info(file_path, "Frontmatter 유효")
                        except yaml.YAMLError as e:
                            self.log_error(file_path, f"Frontmatter YAML 문법 오류: {str(e)[:100]}")
                    else:
                        self.log_error(file_path, "Frontmatter 닫는 --- 없음")
        except Exception as e:
            self.log_error(file_path, f"파일 읽기 오류: {str(e)}")

    def validate_meta_structure(self, meta_file: Path):
        """meta.md 구조 검증"""
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # 필수 섹션 확인
                required_sections = ["## 메타정보", "## 한줄 요약"]
                for section in required_sections:
                    if section not in content:
                        self.log_warning(str(meta_file), f"필수 섹션 '{section}' 없음")
        except Exception as e:
            self.log_error(str(meta_file), f"검증 오류: {str(e)}")

    def validate_topic_links(self, topic_file: Path, slug: str):
        """주제 페이지의 링크 검증"""
        try:
            with open(topic_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # 링크 추출: [text](path)
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                links = re.findall(link_pattern, content)

                for text, link_path in links:
                    # 상대경로 링크만 검증
                    if not link_path.startswith('http'):
                        # 경로 정규화 (Windows 역슬래시 처리)
                        normalized_path = link_path.replace("\\", "/")

                        # 상대경로 해석
                        parts = normalized_path.split("/")
                        current = topic_file.parent
                        try:
                            for part in parts:
                                if part == "..":
                                    current = current.parent
                                elif part and part != ".":
                                    current = current / part

                            full_path = current

                            # 경로 깊이 검증
                            if normalized_path.startswith("../../../raw/"):
                                # raw 참조는 3단계 깊이 OK
                                pass
                            elif normalized_path.startswith("../"):
                                # 형제 토픽 링크
                                if normalized_path.count("../") != 1:
                                    self.log_error(str(topic_file), f"형제 토픽 링크 깊이 오류: {link_path}")
                            elif normalized_path.startswith("../../"):
                                # 다른 경로 (e.g., 결정.md)
                                pass
                            else:
                                self.log_warning(str(topic_file), f"예상치 못한 링크 경로: {link_path}")

                            # 파일 존재 여부 확인
                            if not full_path.exists() and "raw/" not in normalized_path:
                                self.log_error(str(topic_file), f"링크가 가리키는 파일 없음: {link_path}")
                        except Exception as path_error:
                            self.log_warning(str(topic_file), f"경로 계산 오류: {link_path} ({str(path_error)[:50]})")
        except Exception as e:
            self.log_error(str(topic_file), f"링크 검증 오류: {str(e)}")

    def validate_rollup_files(self):
        """결정.md, 액션아이템.md 검증"""
        files_to_check = [
            self.wiki_root / "wiki" / "결정" / "결정.md",
            self.wiki_root / "wiki" / "액션아이템" / "액션아이템.md",
        ]

        for file_path in files_to_check:
            if not file_path.exists():
                self.log_warning(str(file_path), "파일 없음")
                continue

            self.validate_frontmatter(str(file_path))

            # 링크 검증
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                    links = re.findall(link_pattern, content)

                    for text, link_path in links:
                        if not link_path.startswith('http'):
                            # 경로 정규화
                            normalized_path = link_path.replace("\\", "/")
                            # 현재 파일 위치에서 상대경로 계산
                            full_path = (file_path.parent / normalized_path).resolve()
                            # 심볼릭 링크 해석
                            if not full_path.exists():
                                self.log_error(str(file_path), f"깨진 링크: {link_path}")
            except Exception as e:
                self.log_error(str(file_path), f"검증 오류: {str(e)}")

    def validate_index(self):
        """index.md 검증"""
        index_file = self.wiki_root / "wiki" / "index.md"
        if not index_file.exists():
            self.log_error("wiki/index.md", "파일 없음")
            return

        # 토픽 폴더와 index의 링크 일치 확인
        topics_dir = self.wiki_root / "wiki" / "topics"
        if topics_dir.exists():
            topics = set(f.name for f in topics_dir.iterdir() if f.is_dir())

            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    for topic_slug in topics:
                        # index에 해당 토픽이 링크되어 있는지 확인
                        if f"topics/{topic_slug}/" not in content:
                            self.log_warning("wiki/index.md", f"토픽 '{topic_slug}'이 index에 없음 (고아 페이지)")
            except Exception as e:
                self.log_error("wiki/index.md", f"검증 오류: {str(e)}")

    def run(self):
        """모든 검증 실행"""
        print("[LINT] HarnessWiki 기계 검증 시작...\n")

        self.validate_raw_structure()
        self.validate_topic_structure()
        self.validate_rollup_files()
        self.validate_index()

        # 결과 출력
        print("\n" + "="*60)
        print("검증 완료")
        print("="*60 + "\n")

        if self.errors:
            print(f"[ERROR] 오류 ({len(self.errors)}건):")
            for error in self.errors:
                print(f"  {error}")
            print()

        if self.warnings:
            print(f"[WARN] 경고 ({len(self.warnings)}건):")
            for warning in self.warnings:
                print(f"  {warning}")
            print()

        if self.info:
            print(f"[INFO] 정보 ({len(self.info)}건):")
            for info_msg in self.info[:5]:  # 처음 5개만 표시
                print(f"  {info_msg}")
            if len(self.info) > 5:
                print(f"  ... 외 {len(self.info) - 5}건")
            print()

        # 요약
        print("[SUMMARY]")
        print(f"  - 오류: {len(self.errors)}건")
        print(f"  - 경고: {len(self.warnings)}건")
        print(f"  - 정보: {len(self.info)}건")

        # 종료 코드
        return 0 if not self.errors else 1


if __name__ == "__main__":
    wiki_root = sys.argv[1] if len(sys.argv) > 1 else "."
    linter = WikiLinter(wiki_root)
    sys.exit(linter.run())
