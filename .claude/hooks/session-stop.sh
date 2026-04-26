#!/usr/bin/env bash
# Hook: Stop
# 세션 종료 시 변경사항 자동 커밋 & 푸시

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || REPO_ROOT="$CLAUDE_PROJECT_DIR"
cd "$REPO_ROOT" || exit 0

# 변경사항 스테이징
git add -A 2>/dev/null || true

# 변경사항 없으면 종료
if git diff-index --quiet HEAD 2>/dev/null; then
  exit 0
fi

# 커밋
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
git commit -m "w: $TIMESTAMP" 2>/dev/null || true

# 푸시 (실패해도 무시)
git push 2>/dev/null || true
