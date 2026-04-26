#!/usr/bin/env bash
# Hook: SessionStart
# 출근 후 세션 시작 시 TODO.md + 최근 일일기록 + 최근 커밋을 컨텍스트로 주입

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || REPO_ROOT="$CLAUDE_PROJECT_DIR"
cd "$REPO_ROOT" || exit 0

# 최신 변경사항 pull (다른 PC에서 작업한 내용 반영)
git pull --ff-only 2>/dev/null || true

CONTEXT=""

# 오늘 날짜 + 요일 주입 (날짜 오류 방지)
KST_DATE=$(python3 -c "
from datetime import datetime, timezone, timedelta
kst = datetime.now(timezone(timedelta(hours=9)))
days = ['월','화','수','목','금','토','일']
print(kst.strftime('%Y-%m-%d') + ' (' + days[kst.weekday()] + ')')
" 2>/dev/null || date '+%Y-%m-%d')
CONTEXT="=== 오늘 날짜 (KST) ===\n$KST_DATE\n\n"

# TODO.md 로드
TODO="$REPO_ROOT/TODO.md"
if [ -f "$TODO" ]; then
  TODO_CONTENT=$(cat "$TODO")
  CONTEXT="=== TODO.md ===\n$TODO_CONTENT\n\n"
fi

# 가장 최근 일일기록 로드 (오늘 or 어제)
DAILY_DIR="$REPO_ROOT/일일기록"
if [ -d "$DAILY_DIR" ]; then
  TODAY=$(date '+%Y-%m-%d')
  YESTERDAY=$(python3 -c "from datetime import date, timedelta; print(date.today() - timedelta(days=1))" 2>/dev/null || echo "")

  for CHECK_DATE in "$TODAY" "$YESTERDAY"; do
    DAILY_FILE="$DAILY_DIR/$CHECK_DATE.md"
    if [ -f "$DAILY_FILE" ]; then
      DAILY_CONTENT=$(cat "$DAILY_FILE")
      CONTEXT="${CONTEXT}=== 최근 일일기록 ($CHECK_DATE) ===\n$DAILY_CONTENT\n\n"
      break
    fi
  done
fi

# 파이프라인 현황 로드
PIPELINE="$REPO_ROOT/영업기록/파이프라인.md"
if [ -f "$PIPELINE" ]; then
  PIPELINE_CONTENT=$(cat "$PIPELINE")
  CONTEXT="${CONTEXT}=== 영업 파이프라인 현황 ===\n$PIPELINE_CONTENT\n\n"
fi

# 최근 커밋 5개
RECENT_COMMITS=$(git log --oneline -5 2>/dev/null || true)
if [ -n "$RECENT_COMMITS" ]; then
  CONTEXT="${CONTEXT}=== 최근 커밋 ===\n$RECENT_COMMITS"
fi

# JSON으로 출력
if [ -n "$CONTEXT" ]; then
  ESCAPED=$(PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python3 -c 'import sys,json; print(json.dumps(sys.stdin.read(), ensure_ascii=False))' <<< "$CONTEXT" 2>/dev/null || echo '""')
  echo "{\"additionalContext\": $ESCAPED}"
fi
