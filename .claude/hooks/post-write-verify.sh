#!/usr/bin/env bash
# Hook: PostToolUse (matcher: Write)
# 파일 저장 후 교차 검증이 필요한 경로 감지 시 Claude에게 권장 메시지 전달
# 강제 보장: "미팅/CS/일일기록 저장 후 → 검증 자동 트리거"

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || REPO_ROOT="$CLAUDE_PROJECT_DIR"
PENDING_FILE="$REPO_ROOT/.claude/state/pending-verification.txt"

# stdin에서 저장된 파일 경로 추출
FILE_PATH=$(PYTHONUTF8=1 python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    inp = data.get('tool_input', data)
    print(inp.get('file_path', ''))
except:
    print('')
" 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# 상대경로로 정규화
REL_PATH="${FILE_PATH#$REPO_ROOT/}"

# state 디렉토리 보장
mkdir -p "$REPO_ROOT/.claude/state" 2>/dev/null

TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
TRIGGERED=""

# 1. 미팅 파일 (고객관리/*/YYYY-MM-DD*.md)
if echo "$REL_PATH" | grep -qE "고객관리/[^/]+/[0-9]{4}-[0-9]{2}-[0-9]{2}.*\.md$"; then
    echo "[$TIMESTAMP] meeting|$REL_PATH" >> "$PENDING_FILE"
    TRIGGERED="meeting"
    cat <<EOF
🔔 미팅 기록 저장 감지: $REL_PATH
→ 다음 단계 필수: 문서점검 에이전트로 프로파일·파이프라인·TODO 정합성 교차 검증
EOF
fi

# 2. CS 파일 (CS/**/*.md, CS_인덱스 제외)
if echo "$REL_PATH" | grep -qE "^CS/.+\.md$" && ! echo "$REL_PATH" | grep -qE "CS_인덱스|CLAUDE|FAQ"; then
    echo "[$TIMESTAMP] cs|$REL_PATH" >> "$PENDING_FILE"
    TRIGGERED="cs"
    cat <<EOF
🔔 CS 케이스 저장 감지: $REL_PATH
→ 다음 단계 필수: CS_인덱스 갱신 + TODO.md 후속 조치 반영 확인
EOF
fi

# 3. 일일기록 (일일기록/YYYY-MM-DD*.md)
if echo "$REL_PATH" | grep -qE "^일일기록/[0-9]{4}-[0-9]{2}-[0-9]{2}.*\.md$"; then
    echo "[$TIMESTAMP] daily|$REL_PATH" >> "$PENDING_FILE"
    TRIGGERED="daily"
    cat <<EOF
🔔 일일기록 저장 감지: $REL_PATH
→ 다음 단계 필수: 문서점검 에이전트로 전체 정합성 최종 점검 (TODO ↔ 파이프라인 ↔ 실제 파일)
EOF
fi

exit 0
