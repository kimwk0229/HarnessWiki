#!/bin/bash

echo "=== 고아 페이지 및 추가 검증 ==="
echo ""

# index.md에 등록되지 않은 토픽 찾기
echo "1. 고아 페이지 검증"
echo "   (index.md 및 다른 페이지에서 링크되지 않은 토픽)"
echo ""

find wiki/topics -name "*.md" -type f -mindepth 2 -maxdepth 2 | sort | while read file; do
  # 파일명을 추출 (폴더/파일.md)
  topic=$(basename "$(dirname "$file")")
  topic_file=$(basename "$file")
  
  # 같은 이름의 폴더/파일이 아니면 스킵 (폴더 노트 구조 확인)
  if [ "$topic" != "${topic_file%.md}" ]; then
    echo "   ✗ 폴더 노트 구조 위반: $file"
    echo "     (폴더명: $topic, 파일명: ${topic_file%.md})"
    continue
  fi
  
  # index.md에서 이 토픽을 참조하는지 확인
  if ! grep -q "wiki/topics/$topic/" index.md; then
    echo "   ! 고아 페이지: $file"
    echo "     (index.md에 등록되지 않음)"
  fi
done

echo ""

# 모든 토픽이 링크되는 페이지 확인
echo "2. 토픽 링크 현황"
echo ""
find wiki/topics -name "*.md" -type f -mindepth 2 -maxdepth 2 | sort | while read file; do
  topic=$(basename "$(dirname "$file")")
  link_count=$(grep -r "wiki/topics/$topic/" . --include="*.md" 2>/dev/null | grep -v "^$file:" | wc -l)
  # index.md도 포함하므로 1 이상이면 적어도 index.md에는 링크됨
  if [ $link_count -gt 0 ]; then
    echo "   ✓ $topic: $link_count개 페이지에서 링크"
  else
    echo "   ✗ $topic: 어떤 페이지에서도 링크되지 않음"
  fi
done

echo ""
echo "3. 날짜 형식 확인 (raw 폴더)"
echo "   (YYYY-MM-DD_슬러그 형식 검증)"
echo ""

find raw -mindepth 1 -maxdepth 1 -type d | sort | while read dir; do
  dirname=$(basename "$dir")
  # YYYY-MM-DD 패턴 확인
  if [[ ! $dirname =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}_ ]]; then
    echo "   ✗ 날짜 형식 오류: $dirname"
  fi
  
  # meta.md와 raw.md 확인
  if [ ! -f "$dir/meta.md" ]; then
    echo "   ✗ 메타파일 누락: $dirname/meta.md"
  fi
  if [ ! -f "$dir/raw.md" ]; then
    echo "   ✗ 원본파일 누락: $dirname/raw.md"
  fi
done

