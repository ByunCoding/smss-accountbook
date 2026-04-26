#!/bin/bash
# PreToolUse hook wrapper — Python 스크립트 호출
# git bash + Windows Python 경로 변환 이슈 피하려고 스크립트 자기 위치로 cd 후 상대경로 실행
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
cd "$SCRIPT_DIR" && python pre-tool-use.py
