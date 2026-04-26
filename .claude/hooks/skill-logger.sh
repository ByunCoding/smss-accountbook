#!/usr/bin/env bash
# Hook: PostToolUse (matcher: Skill)
# 스킬 사용 시마다 일일기록/skill-log.txt에 기록
# Claude Code 훅은 stdin으로 JSON을 전달함

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || REPO_ROOT="$CLAUDE_PROJECT_DIR"
LOG_FILE="$REPO_ROOT/일일기록/skill-log.txt"

# stdin에서 JSON 읽기 → tool_input.skill 추출
SKILL_NAME=$(PYTHONUTF8=1 python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # PostToolUse 페이로드: {tool_name, tool_input, tool_response, ...}
    inp = data.get('tool_input', data)
    print(inp.get('skill', ''))
except:
    print('')
" 2>/dev/null)

if [ -z "$SKILL_NAME" ]; then
    exit 0
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
echo "$TIMESTAMP  $SKILL_NAME" >> "$LOG_FILE"
