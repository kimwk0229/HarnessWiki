#!/bin/bash

echo "=== HarnessWiki 링크 검증 리포트 ==="
echo ""

# 변수 초기화
total_files=0
total_links=0
broken_links=0
depth_mismatches=0
obsidian_links=0

# raw 링크 형식 확인 (주제 페이지에서)
echo "1. Raw 링크 검증"
echo "   대상: wiki/topics 내 모든 파일"
raw_link_issues=0
while IFS= read -r file; do
  while IFS= read -r line; do
    # raw 링크를 찾기
    if [[ $line =~ \(.*raw/.* ]]; then
      # 올바른 형식 확인
      if [[ ! $line =~ \(\.\./\.\./\.\./raw/ ]]; then
        echo "   ✗ 깊이 불일치: $file"
        echo "     $line"
        ((raw_link_issues++))
        ((depth_mismatches++))
      fi
    fi
  done < "$file"
done < <(find wiki/topics -name "*.md" -type f)

if [ $raw_link_issues -eq 0 ]; then
  echo "   ✓ 모든 raw 링크 형식 올바름"
fi
echo ""

# 형제 토픽 링크 확인
echo "2. 형제 토픽 링크 검증"
echo "   대상: 결정.md, wiki/topics 내 모든 파일"
topic_link_issues=0

# 결정.md의 토픽 링크 확인
if [ -f wiki/결정/결정.md ]; then
  while IFS= read -r line; do
    if [[ $line =~ \(\.\./topics/ ]]; then
      topic_name=$(echo "$line" | grep -oP '(?<=topics/)[^/]+' | head -1)
      if [ -n "$topic_name" ]; then
        if [ ! -f "wiki/topics/$topic_name/$topic_name.md" ]; then
          echo "   ✗ 깨진 링크 (결정.md): $line"
          ((broken_links++))
          ((topic_link_issues++))
        fi
      fi
    fi
  done < wiki/결정/결정.md
fi

# wiki/topics 내 파일들의 형제 토픽 링크 확인
while IFS= read -r file; do
  dir=$(dirname "$file")
  while IFS= read -r line; do
    if [[ $line =~ \(\.\./.*\.md ]]; then
      # ../로 시작하는 링크 추출
      link=$(echo "$line" | grep -oP '\(\.\./[^)]+' | sed 's/^(//' | head -1)
      if [ -n "$link" ]; then
        target_file="$dir/$link"
        if [ ! -f "$target_file" ]; then
          echo "   ✗ 깨진 형제 토픽 링크: $file"
          echo "     찾는 파일: $target_file"
          ((broken_links++))
          ((topic_link_issues++))
        fi
      fi
    fi
  done < "$file"
done < <(find wiki/topics -name "*.md" -type f)

if [ $topic_link_issues -eq 0 ]; then
  echo "   ✓ 모든 형제 토픽 링크 유효함"
fi
echo ""

# Obsidian 위키링크 확인
echo "3. Obsidian 위키링크 검증"
obsidian_count=$(grep -r '\[\[' wiki/ --include="*.md" | wc -l)
if [ $obsidian_count -eq 0 ]; then
  echo "   ✓ Obsidian 위키링크([[...]]) 없음"
else
  echo "   ✗ 발견된 Obsidian 위키링크: $obsidian_count"
  ((obsidian_links=$obsidian_count))
fi
echo ""

echo "=== 최종 요약 ==="
file_count=$(find wiki -name "*.md" -type f | wc -l)
link_count=$(grep -rho '\[.*\](' wiki/ --include="*.md" | wc -l)
echo "검사 파일 수: $file_count"
echo "총 링크 수: $link_count"
echo "깨진 링크: $broken_links"
echo "깊이 불일치: $depth_mismatches"
echo "Obsidian 위키링크: $obsidian_links"
