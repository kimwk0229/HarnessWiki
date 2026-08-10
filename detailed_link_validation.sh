#!/bin/bash

echo "=== 상세 링크 검증 ==="
echo ""

# 모든 마크다운 링크 추출 및 검증
echo "링크 형식별 검증:"
echo ""

# 1. Raw 링크 (../../raw/ 형식 검증)
echo "1. Action-items.md & Decisions.md의 Raw 링크 (2단계 상향)"
count=0
while IFS= read -r line; do
  if [[ $line =~ \(../../raw/ ]]; then
    ((count++))
  fi
done < wiki/액션아이템/액션아이템.md
while IFS= read -r line; do
  if [[ $line =~ \(../../raw/ ]]; then
    ((count++))
  fi
done < wiki/decisions/decisions.md
echo "   발견: $count개 (올바른 형식)"
echo ""

# 2. Raw 링크 (../../../raw/ 형식 검증 - 주제 페이지)
echo "2. 주제 페이지의 Raw 링크 (3단계 상향)"
count=0
while IFS= read -r file; do
  while IFS= read -r line; do
    if [[ $line =~ \(\.\./\.\./\.\./raw/ ]]; then
      ((count++))
    fi
  done < "$file"
done < <(find wiki/topics -name "*.md" -type f)
echo "   발견: $count개 (올바른 형식)"
echo ""

# 3. 형제 토픽 링크 검증 (../토픽/토픽.md)
echo "3. 형제 토픽 링크 (../topic/topic.md 형식)"
count=0
while IFS= read -r file; do
  while IFS= read -r line; do
    if [[ $line =~ \(\.\./[^/]+/[^/]+\.md ]]; then
      ((count++))
    fi
  done < "$file"
done < <(find wiki/topics -name "*.md" -type f)
while IFS= read -r line; do
  if [[ $line =~ \(\.\./topics/ ]]; then
    ((count++))
  fi
done < wiki/decisions/decisions.md
echo "   발견: $count개 (올바른 형식)"
echo ""

# 4. 다른 경로의 링크 (decisions, 액션아이템)
echo "4. 기타 구조적 링크 (../../decisions/, ../../액션아이템/ 등)"
count=0
while IFS= read -r file; do
  while IFS= read -r line; do
    if [[ $line =~ \(\.\./\.\./[a-z-]+/ ]]; then
      ((count++))
    fi
  done < "$file"
done < <(find wiki/topics -name "*.md" -type f)
echo "   발견: $count개"
echo ""

