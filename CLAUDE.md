# CLAUDE.md - smss-accountbook

## 프로젝트 개요
SMSS 가계부 - GitHub Pages로 호스팅되는 PWA 가계부 앱
- URL: https://byuncoding.github.io/smss-accountbook/
- 메인 파일: `index.html` (약 8200줄, 단일 파일)
- 아카이브: `data/*.json` (과거 월 정적 데이터), `data/index.json` (월 목록)

## 개발 환경 주의
- **저장소 위치: `C:\Users\tkdal\Documents\GitHub\smss-accountbook`**
  (2026-09-29에 OneDrive 밖으로 옮겼다. **OneDrive에 두면 `.git`이 손상된다** —
  실제로 동기화 해제 중 이동이 중단돼 `.git`이 비고 파일이 사라졌다.
  옛 경로 `OneDrive\Documents\GitHub\smss-accountbook`는 쓰지 말 것)
- **git이 PATH에 없다.** GitHub Desktop 번들 git을 쓴다:
  `$env:LOCALAPPDATA\GitHubDesktop\app-<버전>\resources\app\git\cmd\git.exe`
  (`app-*` 폴더가 여러 개면 가장 높은 버전 사용)
- **그냥 `git push`는 CLI에서 안 된다.** GitHub Desktop이 토큰을 자체 형식
  (`GitHub - https://api.github.com/<user>`)으로 저장해서 credential manager가 못 찾는다.
  → **`scripts\push.ps1`** 을 쓴다. 그 토큰을 자격 증명 관리자에서 메모리로만 읽어
  일회용 credential helper로 넘긴다 (디스크·git 설정에 남기지 않음).
  토큰 blob은 **UTF-8** 이다 — UTF-16으로 읽으면 20자짜리 깨진 값이 나와 인증 실패한다
- 셸은 Windows PowerShell 5.1 → `&&` / `?:` / `??` 사용 불가, `;` + `if ($?)` 로 대체
  - 네이티브 exe에 큰따옴표가 든 인자를 넘기면 잘못 쪼개진다 →
    커밋 메시지는 파일에 써서 `git commit -F <파일>`
  - 백틱 3개(```) 를 문자열에 직접 넣지 말 것 → `[char]96` 으로 조립
- 로컬 확인은 `node`로 정적 서버를 띄운다 (서비스워커는 localhost에서만 동작)

## 배포 규칙
**중요: 모든 작업 완료 후 반드시 커밋 & 푸시**
```powershell
$git = "$env:LOCALAPPDATA\GitHubDesktop\app-3.6.6\resources\app\git\cmd\git.exe"
& $git add index.html; if ($?) { & $git commit -F 커밋메시지.txt }
powershell -ExecutionPolicy Bypass -File scripts\push.ps1
```
- GitHub Pages 자동 배포 (1-2분 소요)
  - 배포 확인은 `?b=<난수>` 를 붙여 받을 것. 루트 URL은 CDN이 최대 10분 옛 버전을 준다
- 커밋 메시지에 Co-Authored-By 포함
- **`service-worker.js` 수정 시 `CACHE_NAME` 버전을 올려야** 기존 캐시가 갱신된다
- `업로드.bat`은 **동작하지 않는다** (bare `git`이 PATH에 없음)

## 기술 스택
- Vanilla JavaScript (프레임워크 없음)
- Chart.js (차트)
- Remixicon (아이콘)
- Google Apps Script (백엔드 API)
- Google Sheets (데이터 저장소)
- PWA (manifest.json, service-worker.js)
- GitHub Actions (매월 자동 아카이브)

## index.html 구조 (총 ~9800줄)

> 줄 번호는 수정하면 밀린다. 함수를 찾을 때는 **줄 번호보다 함수명 grep**을 우선할 것.

| 라인 범위 | 내용 |
|----------|------|
| 1-20 | head (preconnect, chart.js defer, manifest) |
| 21-4016 | `<style>` — CSS 전체 |
| 4018-4742 | HTML 본문 (헤더, 탭, 카드, 모달) |
| 4743-9802 | `<script>` — JS 전체 (인라인 1개 블록) |

### CSS 주요 구간
| 라인 | 내용 |
|------|------|
| 25-100 | CSS 변수 (라이트/다크) |
| 499-520 | 헤더 새로고침 버튼 + 미전송 배지 기준점 |
| 2094-2100 | `.expense-card-list` (모바일 전용, 기본 숨김) |
| 2250-2255 | 모바일 @media 에서 카드 표시 / 테이블 숨김 |
| 3430-3475 | 토스트 |
| 3477-3550 | `.sw-update-toast`(새 버전 안내), `.pending-badge`(미전송) |
| 3552+ | 모바일 반응형 `@media (max-width: 768px)` |

### JS 주요 구간
| 라인 | 내용 |
|------|------|
| 4744-4805 | 설정 상수 (`SHEET_ID`, `GOOGLE_SHEETS`, `SHEET_LIST_URL`) |
| 4885-5040 | 설정 로드/저장 (`loadSettings`, `saveSettings`) |
| 5404-5520 | 고정수입 관리 |
| 5521-5760 | 고정비 관리, `processRecurringIncomes` |
| 5766-5850 | 캐시 관리, 시트 목록 로드 |
| 5850-6000 | `loadData` / `forceRefresh` / `loadFreshData` |
| 6003-6165 | 월 캐시 + **`loadAllExpenses`** (데이터 출처 결정) |
| 6180-6360 | CSV 파싱 (`parseCSVToExpenses`, `parseMonthlyData`) |
| 6369-6535 | **월별 인덱스 + `calculateSummary` + `patchSummary`** |
| 6537-6690 | 대시보드 초기화, 월 탭 선택 |
| 6691-6766 | `updateDashboard`, 차트 생성 분기 |
| 6768-7460 | 대시보드 카드들 (지표/히트맵/인사이트/비교) |
| 7457-7560 | 예산 탭 |
| 7562-7920 | 차트 (Chart.js), 연간 요약 |
| 7920-8035 | 필터 |
| 8036-8275 | **`renderExpenseTable`** (상세 내역) |
| 8364-8560 | **전송 큐 (outbox)** — 유실 방지의 핵심 |
| 8599-8660 | `suggestCategory` (CATEGORY_KEYWORDS) |
| 8664-8790 | 커스텀 날짜 선택기 |
| 8792-9060 | 입력 모달, 자주쓰는 지출 |
| 9072-9410 | `undoDelete`, **`submitExpense`** |
| 9491-9580 | `deleteExpenseByData` |
| 9594-9700 | 다크모드 |
| 9698-9802 | 서비스워커 등록, `showUpdateToast`, `fastStart` |

## 데이터 로딩 아키텍처

### 데이터 소스 (2계층)
- **정적 JSON** (`data/*.json`): 과거 월 아카이브. `data/index.json`에서 월 목록 동적 로드
- **Google Sheets** (`GOOGLE_SHEETS`): 현재 월. Apps Script API로 시트 목록 조회

### 로딩 흐름 (`loadAllExpenses(forceSheets)`)
**중요: 정적 JSON이 우선이다.** 시트가 아니다.

1. `data/index.json` fetch → 아카이브된 월 목록(`archivedSet`) 확인 (24시간 캐시)
2. Google Sheets에서 읽는 월 = 다음 중 하나라도 해당되는 월만
   - `forceSheets === true` (헤더 새로고침 버튼)
   - 아카이브가 아직 없는 월 (`!archivedSet.has(month)`)
   - 현재 월 또는 미래 월 (`isCurrentOrFutureMonth`) — 할부가 미래 월 시트를 만든다
3. 나머지 아카이브된 월은 전부 `data/<월>.json` 에서 읽는다
4. 과거 월: localStorage 캐시 히트 시 네트워크 스킵 (30일 유효)

> **왜 이렇게 했나**: 예전에는 `GOOGLE_SHEETS`에 있는 월이 무조건 시트에서 로드됐다.
> 그런데 아카이브가 끝난 월(2026-01~08)의 시트가 그대로 남아 있어서 매번 gviz CSV를
> 10번 받았다 (실측 개당 450~2,860ms). 이제 현재 월 1개만 받는다.
>
> **트레이드오프**: 시트에서 지난 달을 직접 수정하면 앱에 바로 안 뜬다.
> → 헤더 **새로고침 버튼**(`forceRefresh`)을 누르면 `forceSheets=true`로 전부 다시 읽는다.

### 캐시 구조 (localStorage)
| 키 | 용도 | 만료 |
|----|------|------|
| `smss_accountbook_cache_v2` | 전체 데이터 캐시 (즉시 표시용) | 5분 |
| `smss_expense_month_cache` | 월별 개별 캐시 (과거 월 스킵용) | 30일 |
| `smss_sheet_list_cache` | 시트 목록 캐시 | 5분 |
| `smss_index_json_cache` | `data/index.json` 캐시 | 24시간 |
| `smss_outbox_v1` | **미전송 쓰기 큐** (유실 방지) | 없음 (전송 성공 시 제거) |

### ⛔ 절대 규칙: 한 번 입력 = 시트에 정확히 한 번 기록
**사용자가 한 번 저장하면 시트에는 반드시 한 번만 들어가야 한다. 중복 기록은 버그다.**
(2026-09에만 같은 내역이 2~4번 들어간 묶음이 11개. 원인: 응답을 못 받으면 무조건 재전송 +
GET 쓰기 요청을 통신망이 자동 재전송 + Apps Script에 중복 방지 없음)

- 시트 쓰기는 **`enqueueApi()` → 전송 큐 한 곳**에서만. `fetch(APPS_SCRIPT_URL…)` 를 새로 만들지 말 것
- 모든 쓰기 요청에 **`rid`(=큐 항목 id)** 를 붙인다. 재전송해도 같은 rid → Apps Script가 무시
- 서버가 rid를 지원하지 않으면(`smss_server_idem` 미설정) **보내기 전 시트 행 수를 세고**,
  결과가 불확실하면 **다시 세어 늘었으면 성공 처리** — 확인 못 하면 보내지 않는다 (`countSheetMatches`)
- "실패하면 다시 보낸다"를 추가 요청에 쓰지 말 것. 반드시 위 확인을 거친다
- **자동 검사**: `index.html` 을 고치면 PostToolUse 훅이 `node scripts/check-write-safety.js` 를 돌린다
  (직접 fetch 개수, rid, 응답 유실·앱 종료·오프라인 시나리오). 실패하면 exit 2 — **통과할 때까지 커밋 금지**
- **구버전 Apps Script의 지출 삭제는 `deleteRow`(행 전체)라 같은 행의 수입(H~K)까지 지운다.**
  앱은 지출 삭제 전후 수입 목록을 비교해 사라진 수입을 다시 넣는다 (`restoreLostIncomes`).
  **스크립트로 지출을 대량 삭제할 때도 반드시 enqueueApi를 거칠 것** (2026-10-03 9월 정리 중 수입 1건 유실)
- Apps Script 쪽 수정본은 `App Script.md` (rid 중복 무시 + LockService + 정확한 행 삭제 + A~F만 비움).
  **사용자가 붙여넣고 재배포해야 적용된다** — 적용되면 응답에 `idem: true`

### 전송 큐 (outbox) — 데이터 유실 방지
모든 쓰기(`add`/`delete`/`addIncome`/`deleteIncome`)는 `enqueueApi()`로 큐에 넣고,
`flushOutbox()`가 **하나씩 순서대로(직렬)** 전송한다.

- **왜 큐인가**: 예전에는 `fetch(...).catch(console.error)`로 쏘고 끝이라, 네트워크가
  끊긴 상태에서 입력하면 "저장되었습니다" 토스트만 뜨고 시트에는 안 들어갔다.
  캐시가 만료되면 입력이 조용히 사라졌다.
- **왜 직렬인가**: 할부 12개월을 동시에 쏘면 Apps Script가 "빈 행 찾기 → 쓰기"를 하므로
  동시 실행끼리 같은 행을 덮어쓸 수 있었다.
- `flushOutbox()`는 이미 전송 중이면 **진행 중인 Promise를 반환**한다 (await가 실제로 기다려야 함)
- 온라인 복귀(`online`), 탭 복귀(`visibilitychange`), 30초 주기로 재시도
- 헤더 새로고침 버튼에 미전송 건수가 배지로 표시된다 (`updatePendingBadge`)
- `forceRefresh`는 큐를 먼저 비운 뒤 시트를 읽는다 (안 그러면 방금 입력이 결과에서 빠진다)
- 전체 새로고침 후에는 `reapplyOutbox()`가 미전송 항목을 화면에 되살린다

### 서비스워커 (`service-worker.js`)
- **캐시 우선(stale-while-revalidate)**. 앱 셸을 즉시 반환하고 백그라운드에서 갱신한다
  (예전에는 network-first라 375KB `index.html`을 매번 끝까지 받고 나서 렌더했다)
- `script.google.com` / `docs.google.com` / `sheets.googleapis.com` 은 캐시하지 않는다
- 설치 시 `skipWaiting()`을 하지 않는다 → 새 버전은 `showUpdateToast()`로 사용자에게 안내하고,
  "지금 갱신"을 누르면 `SKIP_WAITING` 메시지 → `controllerchange` → 자동 리로드
- 셸은 `cache.addAll`(전부 성공해야 함), CDN은 개별 `cache.add`(실패 허용)
  — `addAll`은 하나만 실패해도 설치 전체가 롤백되기 때문

### JSON 파일 형식
- 기존: `[{expense}, ...]` (배열)
- 수입 포함: `{ "expenses": [...], "income": [...] }`
- 두 형식 모두 하위 호환 처리됨

### 월별 자동 아카이브
- `scripts/archive-month.js`: 지난달 Google Sheets → JSON 변환
- `.github/workflows/archive-month.yml`: 매달 3일 자동 실행
- 수동 실행: `node scripts/archive-month.js [YYYY-MM]`

## 자주 수정하는 함수들

### 데이터 관련
- `loadData()` - 초기 데이터 로드
- `loadFreshData(isBackground, forceSheets)` - API에서 새 데이터 가져오기
- `loadAllExpenses(forceSheets)` - 월별 병렬 로드 (정적 JSON 우선 + Sheets, 캐시 적용)
- `submitExpense()` - 지출 저장 (→ `enqueueApi`)
- `deleteExpenseByData()` - 지출 삭제 (→ `enqueueApi`)
- `enqueueApi(params, opts)` - **모든 쓰기는 반드시 이걸 거친다.** 직접 fetch 금지 (위 "절대 규칙" 참고)
- `calculateSummary()` - 전체 집계 + 월별 인덱스(`_expensesByMonth`) 생성
- `patchSummary(expense, delta)` - 전체 재계산 없이 1건만 증분 반영 (인덱스도 함께 패치)
- `getMonthExpenses(monthKey)` - 해당 월 지출 조회 (O(1)). 대시보드는 이걸 쓴다

### 현금흐름 기능 (2026-09-29 추가)
- `getBillingPeriod(payY, payM, billingDay, closingDay)` — 카드 청구서의 사용기간 계산
  - `closingDay = 0`: 사용기간 = **전월 1일~말일** (국민카드형, 기본값)
  - `closingDay = k`: 결제일 직전의 k일이 마감 → 그 1개월 (현대카드형)
    - 예) 결제일 25일 / 마감 11일 → 10/25 결제분 = 9/12 ~ 10/11
  - 짧은 달은 말일로 클램프된다 (마감 31일 + 9월 → 9/30)
- `getUpcomingBillings()` — 다가오는 결제 예정 (결제일 오름차순), **카드당 가장 가까운 1건**.
  `payment_method` 이름으로 `_expensesByPayment` 인덱스를 조회한다.
  (예전엔 전체를 4건에서 잘라서 같은 날 결제되는 현대카드_시리가 빠졌다)
  렌더 시 사용 0건 카드는 `.billing-idle` 한 줄로 접는다
- `getInstallmentSummary()` — **할부 입력 시 m개월치 행을 전부 만들어 두는 구조**를 이용해
  "오늘 이후 날짜의 할부 행 합계 = 남은 할부 원금"으로 계산한다
- `getCategoryTrends(monthsBack, topN)` — 선택 월을 마지막으로 하는 N개월 구간.
  `monthly_totals[key].categories` 를 읽으므로 전체 배열을 다시 스캔하지 않는다
- `sparklineSVG(series, months, strokeVar)` — 인라인 SVG. **하드코딩 색 금지**,
  `stroke="var(--토큰)"` 만 쓴다 (다크모드 자동 대응)

### 카드 결제일 저장 위치 (주의)
`billingDay` / `closingDay` 는 `appSettings.paymentMethods[].billingDay` 에 들어가지만,
**배포된 Apps Script의 `getSettings`는 결제수단을 `{name, emoji}`로만 돌려준다.**
→ 시트에서 설정을 다시 읽으면 값이 사라진다. 그래서:
- `saveCardBillingLocal()` 이 `smss_card_billing` 키에 이름 기준으로 따로 보관
- `mergeCardBillingLocal()` 이 **`applySettings()` 맨 앞에서** 다시 합친다
  (모든 로드 경로가 `applySettings`를 거치므로 여기가 유일한 안전 지점)
- `App Script.md` 상단에 **미적용 패치**가 있다 — 붙여넣고 재배포하면 기기 간 동기화된다

### 시각화 규칙
- 기존 16색 `categoryColors`는 **나란히 놓고 색만으로 구분하기에 부적합**하다
  (검증기 결과: `#8B5CF6`↔`#6366F1` 정상시야 ΔE 6.3 — 15 미달, 하드 실패).
  따라서 카테고리 색은 **이름/라벨과 함께** 쓰고, 색 단독 식별에 의존하지 말 것
- 추세 스파크라인의 선 색은 카테고리색이 아니라 **상태색**(증가 `--expense` /
  감소 `--income` / 평탄 `--gray-500`)이며, 반드시 화살표 아이콘 + 퍼센트 텍스트와 함께 낸다
- 카드 결제 예정 막대는 **단일 색**(`--primary`) — 하나의 측정값을 카드별로 비교하는
  magnitude 이므로 카테고리 색을 순번으로 돌려 쓰지 않는다
  (기존 `updatePaymentMethods`는 `paymentColors[index % n]`로 **순위에 색을 매기는**
   안티패턴이 남아 있다. 새 코드에서 따라하지 말 것)
- 검증기: `dataviz` 스킬의 `scripts/validate_palette.js`
  표면색은 라이트 `#FFFFFF`, 다크 `#141516`

### 성능 규칙 (되돌리지 말 것)
- `expenseData.expenses.filter(...)`로 월별 필터링하지 말 것 → `getMonthExpenses(key)` 사용
- `new Intl.NumberFormat`을 함수 안에서 만들지 말 것 → `_krwFormatter` 재사용
- `renderExpenseTable`은 데스크톱 테이블/모바일 카드 중 **보이는 쪽만** 렌더한다 (`isMobile`)
- `setMonthExpenseCache`는 버퍼에만 쓴다 → 로드 끝에 `flushMonthExpenseCache()`가 1회 저장
- `chart.js`는 `defer`다 → `fastStart()`는 반드시 `DOMContentLoaded` 이후에 실행

### UI 관련
- `renderExpenseTable()` - 상세내역 테이블 렌더링
  - **표시 기준 (사용자 결정 2026-10-03)**: 직접 입력한 지출(A~F) + 직접 입력한 수입(H~K)만.
    **고정수입(`[고정]` 메모, 매달 자동 생성)과 고정지출(설정 목록 계산값)은 목록에 넣지 않는다.**
    합계·대시보드·카드에는 그대로 반영된다
  - 할부는 앞으로 갚을 달까지 전부 표시된다 (입력 시 m개월치 행을 만드는 구조)
- `updateDashboard()` - 대시보드 전체 업데이트
- `showToast()` - 토스트 알림 표시
- `openInputModal()` / `closeInputModal()` - 입력 모달

### 설정 관련
- `loadSettings()` / `saveSettings()` - 카테고리/결제수단 설정
- `suggestCategory()` - 메모 입력 시 카테고리 추천 (→ `rankCategories`)

## 메모 → 카테고리 추천 (학습형, 2026-10-03)
`rankCategories(memo, date)` 가 **사용자 본인의 지난 기록**(`expenseData.expenses`)으로 점수를 낸다.
1. 똑같은 메모의 과거 분류 (가장 강함, ×2.5)
2. 단어별 투표 (`_ , + / -` 와 공백으로 분리, 2글자 이상). 모르는 단어는 앞부분 일치(입력 중)·
   포함(3글자 이상만 — `삼성카드`가 `카드`에 걸리던 문제)
3. `CATEGORY_KEYWORDS` — 기록에 없는 새 가게용 보조
4. **여행 중**(전날~당일 기록 2건 이상, 60% 이상 여행비)이면 여행비를 크게 가산
- 가중치 반감기 1년 (`CATEGORY_HALF_LIFE_DAYS`), `기타`는 학습 안 함
- 확신도 = 점수 / (합 + `CATEGORY_UNKNOWN_MASS` 0.8) — 근거 적은 100% 방지
- **확신도 ≥ 0.5 일 때만 자동 선택**, 그 외엔 메모 아래 **후보 칩 최대 3개**(≥ 0.1)
- `_categoryTouched` — 칩/셀렉트로 직접 고르거나, 수정 모드·자주 쓰는 지출이면 자동 선택이 덮어쓰지 않는다
- 모델은 `expenses` 배열 참조/길이가 바뀌면 재학습 (1,500건 ≈ 5ms, 키 입력당 ≈ 0.1ms)
- 시간순 재현 평가(그 시점 이전 기록만 사용, 최근 7개월 585건):
  기존 키워드 자동선택 정답 60.7% / 오답 12.5% → 학습형 64.3% / **9.4%**, 칩 3개 안 정답 81%
  — 평가 시 **index.html의 해당 블록을 vm으로 그대로 떼어 와서** 돌릴 것 (복사본 금지)

## 입력 편의 기능 (2026-10-03)
- **금액 추천 칩** `suggestAmounts(memo)` — 같은 메모의 과거 금액을 많이 쓴 순(동률이면 최근) 3개.
  자동으로 채우지 않는다(탭하면 채움). 할부 행 `(n/m)`은 월 할부금이라 제외.
  모델의 `amounts` 인덱스에 들어 있다 (`getCategoryModel`)
- **다시 입력** `repeatByIndex(idx)` — 상세 내역 카드/행의 복사 버튼. 날짜는 항상 오늘,
  할부 행이면 금액은 비우고 금액 칩으로 고르게 한다
- **저장 토스트 예산 줄** `getBudgetStatusLine(category, date)` — 카테고리 예산 > 변동비 예산(수입-고정비)
  > 카테고리 누적 순. `showToast(msg, type, undo, sub)` 의 4번째 인자
- 결제 알림(Apple Pay/승인 문자) → 입력창 자동 채우기는 **만들었다가 뺐다** (2026-10-03).
  카드사가 주는 건 가맹점명(`쿠팡(주)`)이라 사용자의 메모 방식(`쿠팡_기저귀`)과 맞지 않음
- `renderCategorySelect` / `renderPaymentSelect` 는 **다시 그려도 고른 값을 유지**한다
  (입력 중 설정이 백그라운드로 도착하면 카테고리·결제수단이 지워지던 버그)

## 고정수입 자동 생성 (`processRecurringIncomes`) — 중복 주의
- 고정수입은 **시트에 실제로 `addIncome`을 보낸다.** 중복 판단은 이번 달 시트에서 읽은 수입으로 한다
- **2026-10 3중 생성 사고**: `loadFreshData` 1단계가 이번 달 시트를 먼저 읽고(수입 포함),
  `loadAllExpenses`가 `incomeEntries = []`로 비운 뒤 그 결과를 **지출만** 재사용 → 이번 달 수입이 사라져
  "없음"으로 판단, 새 브라우저(테스트 브라우저 포함)마다 한 벌씩 생성됐다
- 지금은: `_preloadedCurrentMonth.income` 으로 수입도 복원, 그리고
  **`_currentMonthSheetLoaded`가 true일 때만** 생성 (시트 읽기 실패 / 목록에 없는 시트면 목록 갱신 후 판단)
- `loadFromGoogleSheets`는 HTTP 오류를 **throw** 한다 (오류 페이지를 빈 시트로 읽으면 같은 사고)
- **테스트 브라우저로 앱을 열 때는 쓰기 요청을 막을 것.** 고정수입이 자동으로 시트에 써진다:
  `context.route(/script\.google\.com/, r => /action=(add|addIncome|delete|deleteIncome|saveSettings)\b/.test(r.request().url()) ? r.abort() : r.continue())`

## 사람별 지출 (2026-10-03)
- 결제수단 → 사용자: `pm.owner`(설정 화면) > 이름 끝 `_이름` > `공동` (`getPaymentOwner`)
- `owner`도 Apps Script가 저장하지 않으므로 `smss_card_billing` 에 결제일과 함께 보관 (기기별)
- 진행 중인 이번 달은 **같은 기간(1일~오늘)** 끼리 비교. 3개월 평균은 기록 있는 달만 평균

## 카테고리 키워드 매핑 (CATEGORY_KEYWORDS) — 학습형 추천의 보조 사전
```javascript
카페: 스타벅스, 메가커피, 폴바셋, 커피, 라떼...
외식: 쿠팡이츠, 배민, 편의점, 맥도날드, 치킨, 피자...
식비: 이마트, 코스트코, 마켓컬리, 우유...
차량유지비: 주차, 주유, 기름, 세차...
생활비: 다이소, 이케아, 택시, cgv, 영화...
병원비: 병원, 치과, 약국, 진료...
육아비: 행운이, 임산부, 아기, 기저귀...
쇼핑: 올리브영, 옷, 화장품, 충전기...
여행비: 호텔, 펜션, srt, 항공...
경조사비: 축의금, 선물, 집들이...
```

## 입력 폼 순서
1. 날짜
2. 메모 (선택) → 카테고리 자동 추천
3. 금액
4. 카테고리 (자동 추천됨)
5. 결제수단

## 코드 컨벤션
- 한글 주석 사용
- 함수명: camelCase
- CSS 변수: `--primary`, `--income`, `--expense` 등
- 들여쓰기: 4칸 스페이스

## 주의사항
- `index.html` 수정 시 반드시 전체 구조 고려
- CSS 수정 시 다크모드 (`[data-theme="dark"]`) 함께 확인
- 모바일 반응형 (`@media (max-width: 768px)`) 확인 — **사용자는 주로 휴대폰으로 쓴다**
  - `input` 글자는 **16px 이상** (미만이면 iOS가 포커스 시 확대), 숫자 입력은 `inputmode="numeric"`
  - 터치 영역 높이 36px 이상
  - 한글 안내 문구에는 `word-break: keep-all` (한 글자만 다음 줄로 떨어지는 것 방지)
  - 새 섹션은 390px 폭(카드 내부 약 310px)에서 겹침/가로 스크롤을 확인할 것
- **Remixicon은 3.5.0** 이다. 4.x 아이콘(`ri-calendar-schedule-*`, `ri-money-won-circle-*` 등)은
  **빈칸으로 나온다.** 새 아이콘은 브라우저에서 `::before` content가 `none`이 아닌지 확인
- PWA standalone 모드 스크롤 이슈 주의
- `service-worker.js` 수정 시 `CACHE_NAME` 버전 올려야 기존 캐시 갱신됨
- `data/index.json`에 새 월 추가 시 → 그 월은 자동으로 **정적 JSON 우선**이 된다
  (아카이브 후에는 시트를 더 안 읽으므로 로딩이 빨라진다)
- Apps Script `add`/`addIncome` 호출 시 **`year` 파라미터를 반드시 넘길 것.**
  빠뜨리면 `String(undefined).slice(-2)` = `'ed'` → `'ed.9'` 같은 쓰레기 시트가 생성된다
- `patchSummary`에 넘기는 객체에 `year`/`month`가 없으면 `date`에서 유도된다 (테이블 삭제 경로)
- `availableMonths`는 **오래된 순**이다. `[0]`은 가장 오래된 달 (예전 기본 월 선택 버그의 원인).
  입력 모달 기본 날짜는 사용자가 월 탭을 직접 골랐을 때(`_monthPickedByUser`)만 그 달 1일, 아니면 오늘

## 검증 방법 (Playwright MCP 없이)
`node`로 인라인 스크립트를 DOM 스텁과 함께 실행해서 로직을 직접 테스트할 수 있다.
`let`/`const` 바인딩은 샌드박스 전역 속성이 아니므로, 스크립트 끝에 브리지를 덧붙여 접근한다:
```js
const bridge = `;globalThis.__app = { get expenseData(){return expenseData}, loadAllExpenses:(f)=>loadAllExpenses(f), ... };`;
new vm.Script(inlineCode + bridge).runInContext(sandbox);
```
