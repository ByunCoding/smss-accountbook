#!/usr/bin/env python3
"""
PreToolUse hook — WATT 프로젝트 보호 가드레일.
stdin으로 JSON 입력 받아 위험 패턴 감지 시 exit 2로 차단.
fail-safe: 예외 발생 시 exit 0 (허용) — 훅 때문에 작업 막히는 사태 방지.
"""
import json
import re
import sys

try:
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROTECTED_DIRS = ["..private", "고객관리", "CS", "영업기록", "일일기록", "성과기록", "주간보고"]
V2_PATTERN = re.compile(r"(_v\d+|_backup|_bak|_copy|\(복사본\)|_사본)\.[^./\\]+$", re.IGNORECASE)


def block(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def check_bash(cmd: str) -> None:
    low = cmd.lower()

    # rm -rf / del /s 보호 폴더
    if re.search(r"\b(rm\s+(-[rRfF]+\s*)+|rmdir\s+/s|del\s+/s)", cmd):
        for d in PROTECTED_DIRS:
            if d in cmd:
                block(
                    f"❌ PreToolUse 차단: 보호 폴더 '{d}' 대상 삭제 명령어 감지.\n"
                    f"   명령어: {cmd}\n"
                    f"   이 폴더의 내용은 업무 기록이라 복구가 어렵습니다.\n"
                    f"   정말 필요하면 터미널에서 직접 실행해주세요."
                )

    # git push --force to master/main
    if "git push" in low and ("--force" in low or re.search(r"\s-f(\s|$)", cmd)):
        if re.search(r"(master|main)", low):
            block(
                "❌ PreToolUse 차단: master/main 브랜치에 force push 시도.\n"
                "   히스토리 손실 위험. 정말 필요하면 터미널에서 직접 실행해주세요."
            )

    # git reset --hard
    if re.search(r"git\s+reset\s+--hard", low):
        block(
            "❌ PreToolUse 차단: git reset --hard 시도.\n"
            "   작업 손실 위험. 필요 시 터미널에서 직접 실행해주세요."
        )


def check_write(path: str) -> None:
    # 파일명 기준 v2/backup/copy 패턴 (경로 전체 아닌 파일명만)
    basename = re.split(r"[\\/]", path)[-1]
    if V2_PATTERN.search(basename):
        block(
            f"❌ PreToolUse 차단: v2/백업/복사본 파일명 생성 금지.\n"
            f"   파일명: {basename}\n"
            f"   → 원본 파일을 직접 수정하세요. 파일이 열려있어 저장 실패하면 "
            f"사용자에게 '파일 닫아주세요' 요청."
        )


def main() -> None:
    # stdin을 bytes로 읽어서 UTF-8/cp949 순차 시도 (Windows 환경 대응)
    try:
        raw_bytes = sys.stdin.buffer.read()
        if not raw_bytes.strip():
            sys.exit(0)
        for enc in ("utf-8", "cp949", "latin-1"):
            try:
                raw = raw_bytes.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            sys.exit(0)
        data = json.loads(raw)
    except Exception:
        # 파싱 실패 = 허용 (fail-safe)
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}

    try:
        if tool_name == "Bash":
            cmd = tool_input.get("command", "") or ""
            check_bash(cmd)
        elif tool_name == "Write":
            path = tool_input.get("file_path", "") or ""
            check_write(path)
        # Edit/MultiEdit은 기존 파일 수정이라 차단 안 함
    except SystemExit:
        raise
    except Exception:
        # 패턴 매칭 중 에러 = 허용 (fail-safe)
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
