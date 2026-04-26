#!/usr/bin/env bash
# Hook: PreCompact
# 컨텍스트 압축 전 핵심 정보를 주입 → 압축 후에도 중요 내용 보존

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || REPO_ROOT="$CLAUDE_PROJECT_DIR"
cd "$REPO_ROOT" || exit 0

CONTEXT="=== 컨텍스트 압축 전 보존 지침 ===\n"
CONTEXT="${CONTEXT}아래 내용은 압축 후에도 반드시 유지할 것:\n"
CONTEXT="${CONTEXT}- 현재 진행 중인 작업 단계\n"
CONTEXT="${CONTEXT}- 고객사명, 담당자, 날짜 등 고유 정보\n"
CONTEXT="${CONTEXT}- 미완료 다음 액션 항목\n"
CONTEXT="${CONTEXT}- CS 케이스 상태 및 해결 여부\n"
CONTEXT="${CONTEXT}\n⚠️ CRITICAL 규칙 (압축 후에도 절대 잊지 말 것):\n"
CONTEXT="${CONTEXT}- 기밀정보 포함 시 즉시 경고\n"
CONTEXT="${CONTEXT}- 확인 불가 시 추측 금지, '확인 불가' 명시\n"
CONTEXT="${CONTEXT}- 파일 수정 전 반드시 전체 읽기 먼저\n"
CONTEXT="${CONTEXT}- v2/_backup 파일 생성 금지\n"
CONTEXT="${CONTEXT}- 검증 없이 완료 선언 금지\n\n"

# 현재 TODO.md 주입 (가장 중요한 컨텍스트)
TODO="$REPO_ROOT/TODO.md"
if [ -f "$TODO" ]; then
  TODO_CONTENT=$(cat "$TODO")
  CONTEXT="${CONTEXT}=== 현재 TODO.md (압축 후 보존 필수) ===\n$TODO_CONTENT\n"
fi

# 파이프라인 현황 주입 (딜 단계 보존)
PIPELINE="$REPO_ROOT/영업기록/파이프라인.md"
if [ -f "$PIPELINE" ]; then
  PIPELINE_CONTENT=$(cat "$PIPELINE")
  CONTEXT="${CONTEXT}\n=== 영업 파이프라인 현황 (압축 후 보존 필수) ===\n$PIPELINE_CONTENT\n"
fi

# JSON 출력
if [ -n "$CONTEXT" ]; then
  ESCAPED=$(PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python3 -c \
    'import sys,json; print(json.dumps(sys.stdin.read(), ensure_ascii=False))' \
    <<< "$CONTEXT" 2>/dev/null || echo '""')
  echo "{\"additionalContext\": $ESCAPED}"
fi
