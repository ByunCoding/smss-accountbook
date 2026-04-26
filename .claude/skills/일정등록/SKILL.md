---
name: 일정등록
description: 일정을 Google Calendar에 등록한다. "일정", "캘린더", "등록해줘", "넣어줘", "스케줄", "다음주", "이번주 일정" 등 일정 관련 표현 시 자동 실행.
disable-model-invocation: false
argument-hint: "[일정 내용]"
hooks:
  Stop:
    - type: command
      command: "bash -c 'echo \"$(date \"+%Y-%m-%d %H:%M\") 일정등록 완료\" >> \"$CLAUDE_PROJECT_DIR/일일기록/skill-log.txt\" 2>/dev/null || true'"
---

# 일정등록

## 목적
사용자가 말하는 일정을 파싱하여 Google Calendar MCP로 등록한다.

## 실행 순서

### Step 1: 일정 파싱
사용자 메시지에서 아래 정보를 추출한다:

| 항목 | 필수 | 비고 |
|------|------|------|
| 일정명 | O | 고객사명 포함 시 `[와트]` 프리픽스 자동 부착 |
| 날짜 | O | "화요일", "다음주 수요일", "4/8" 등 자연어 → 정확한 날짜로 변환 |
| 시간 | △ | 미정이면 종일 이벤트로 등록 |
| 지역 | △ | 대전, 양재, 일산 등 — summary 뒤에 `(지역)` 표시 + location에도 포함 |
| 설명 | △ | 참석자, 발표시간 등 부가정보 → description에 포함 |

### Step 2: 사용자 확인
파싱한 일정을 테이블로 보여주고 확인받는다:

```
📅 등록할 일정:
| 날짜 | 시간 | 일정명 | 장소 |
|------|------|--------|------|
| 4/8  | 16:00 | [와트] 환경공단 미팅 (대전) | 대전 |

맞으면 "ㅇㅇ", 수정할 거 있으면 말씀해주세요.
```

- 일정이 1건이고 명확하면 확인 없이 바로 등록해도 됨
- 2건 이상이면 반드시 테이블로 확인

### Step 3: Google Calendar 등록
`mcp__claude_ai_Google_Calendar__gcal_create_event` 도구를 사용한다.

**등록 규칙:**
- `calendarId`: "primary"
- `summary`: `[와트] ` 프리픽스 + 일정명 + 지역 정보가 있으면 ` (지역명)` 후미 부착
  - 예: `[와트] 환경공단 미팅 (대전)`, `[와트] 공공기관 방문 (양재)`
- `start/end`: 
  - 시간 확정 → `dateTime` (RFC3339, timeZone: "Asia/Seoul")
  - 시간 미정 → `date` (종일 이벤트)
  - 종료 시간 모르면 시작 후 1시간으로 기본 설정
- `location`: 있으면 포함
- `description`: 참석자·발표시간 등 부가정보
- `reminders`: 사용하지 않음 (useDefault: true)
- `sendUpdates`: "none"

**여러 건이면 병렬로 동시 등록한다.**

### Step 4: 완료 보고
```
✅ Google Calendar 등록 완료

| 날짜 | 시간 | 일정명 |
|------|------|--------|
| ... | ... | ... |

코오롱 시간 확정되면 말씀해주세요 — 바로 업데이트하겠습니다.
```

- 시간 미정 건이 있으면 마지막에 리마인드
- 등록 실패 건이 있으면 사유와 함께 재시도 여부 확인

### Step 5: 일정 수정/삭제
사용자가 "시간 바뀌었어", "취소됐어" 등 말하면:
- 수정: `mcp__claude_ai_Google_Calendar__gcal_update_event` 사용
- 삭제: `mcp__claude_ai_Google_Calendar__gcal_delete_event` 사용

## 자연어 날짜 변환 규칙
- "내일" → 오늘 + 1일
- "다음주 화요일" → 다음 주 화요일 날짜
- "이번주 금요일" → 이번 주 금요일 날짜
- "4/8" → 2026-04-08 (현재 연도 기준)
- "화요일" → 가장 가까운 다음 화요일

## 주의사항
- Google Calendar MCP가 연결되어 있지 않으면 `/mcp`에서 연결하라고 안내
- 기밀 정보(계약 금액, 내부 전략 등)는 캘린더 description에 넣지 않음
