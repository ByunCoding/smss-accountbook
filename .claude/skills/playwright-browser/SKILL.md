---
name: playwright-browser
description: Use when needing to browse websites, take screenshots, fill forms, or automate any browser task. Triggers on "웹사이트 열어줘", "캡처해줘", "검색해줘", "사이트 확인", "브라우저로", "스크린샷", "페이지 열어", or any request to interact with a URL.
disable-model-invocation: false
---

# Playwright 브라우저 자동화

MCP로 실제 브라우저를 제어한다. URL이 있으면 무조건 이 스킬로 처리.

## 기본 작업 흐름

### 페이지 열기 + 확인
1. `browser_navigate` — URL 이동
2. `browser_snapshot` — 현재 페이지 구조 파악 (클릭할 요소 찾기)
3. `browser_take_screenshot` — 시각적 확인이 필요할 때

### 정보 수집 (리서치)
1. `browser_navigate` → URL 이동
2. `browser_snapshot` → 페이지 내용 읽기
3. 필요 시 `browser_click`으로 더 보기 / 탭 이동
4. 결과를 요약해서 답변

### 양식 입력 / 로그인
1. `browser_navigate` → 페이지 이동
2. `browser_snapshot` → 입력 필드 파악
3. `browser_fill_form` 또는 `browser_type` → 입력
4. `browser_click` → 제출
5. `browser_wait_for` → 결과 대기

### 스크린샷 저장
1. `browser_navigate` → 페이지 이동
2. `browser_take_screenshot` → 캡처
3. 파일 경로 사용자에게 알려주기

## 주요 도구 레퍼런스

| 도구 | 언제 쓰나 |
|------|---------|
| `browser_navigate` | URL로 이동 |
| `browser_snapshot` | 현재 페이지 DOM 구조 읽기 (요소 찾기 전 필수) |
| `browser_take_screenshot` | 화면 캡처 |
| `browser_click` | 버튼·링크 클릭 |
| `browser_type` | 텍스트 필드에 입력 |
| `browser_fill_form` | 여러 필드 한번에 입력 |
| `browser_wait_for` | 페이지 로딩·요소 등장 대기 |
| `browser_navigate_back` | 뒤로 가기 |
| `browser_tabs` | 열린 탭 목록 확인 |
| `browser_evaluate` | JavaScript 직접 실행 |
| `browser_press_key` | 키보드 입력 (Enter, Escape 등) |
| `browser_network_requests` | 네트워크 요청 확인 |
| `browser_close` | 브라우저 종료 |

## 실전 패턴

### 고객사 사이트 리서치
```
browser_navigate(url) →
browser_snapshot() →  # 내용 파악
browser_take_screenshot() →  # 캡처 저장
결과 요약 → 고객관리/ 또는 영업기록/에 저장 제안
```

### 검색 결과 수집
```
browser_navigate("https://www.google.com") →
browser_type(검색어) →
browser_press_key("Enter") →
browser_wait_for(결과 로딩) →
browser_snapshot() →  # 결과 읽기
```

### 여러 페이지 순차 탐색
```
browser_navigate(URL1) → snapshot → 정보 추출
browser_navigate(URL2) → snapshot → 정보 추출
결과 통합 요약
```

## 주의사항
- `browser_snapshot` 없이 `browser_click` 하지 말 것 — 요소를 먼저 파악해야 정확히 클릭 가능
- 로그인이 필요한 사이트는 사용자에게 먼저 확인
- 개인정보 입력이 필요한 경우 반드시 사용자가 직접 입력하도록 안내
