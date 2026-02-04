# CLAUDE.md - smss-accountbook

## 프로젝트 개요
SMSS 가계부 - GitHub Pages로 호스팅되는 PWA 가계부 앱
- URL: https://byuncoding.github.io/smss-accountbook/
- 메인 파일: `index.html` (약 5900줄)
- 아카이브: `data/*.json` (과거 월 정적 데이터), `data/index.json` (월 목록)

## 배포 규칙
**중요: 모든 작업 완료 후 반드시 커밋 & 푸시**
```bash
git add index.html && git commit -m "메시지" && git push
```
- GitHub Pages 자동 배포 (1-2분 소요)
- 커밋 메시지에 Co-Authored-By 포함

## 기술 스택
- Vanilla JavaScript (프레임워크 없음)
- Chart.js (차트)
- Remixicon (아이콘)
- Google Apps Script (백엔드 API)
- Google Sheets (데이터 저장소)
- PWA (manifest.json, service-worker.js)
- GitHub Actions (매월 자동 아카이브)

## index.html 구조 (라인 번호 참조용)

### CSS 섹션 (~3000줄)
| 라인 범위 | 내용 |
|----------|------|
| 16-420 | 기본 CSS 변수, 다크모드 |
| 420-600 | 헤더, 월 탭, 네비게이션 |
| 600-1300 | 카드, 차트, 테이블 스타일 |
| 1300-1400 | 삭제 버튼, 빈 상태 UI |
| 1800-2100 | 모바일 반응형 |
| 2100-2400 | 입력 모달 스타일 |
| 2400-2700 | 토스트, 설정 모달 |

### HTML 섹션 (2900-3500줄)
| 라인 범위 | 내용 |
|----------|------|
| 2900-2950 | 로딩 오버레이, 헤더 |
| 2950-3000 | 월 탭, 네비게이션 |
| 3000-3200 | 월간 리포트 탭 |
| 3200-3250 | 상세 내역 탭 (필터, 테이블) |
| 3350-3420 | 지출 입력 모달 |
| 3420-3550 | 설정 모달, 예산 모달 |

### JavaScript 섹션 (3600-5900줄)
| 라인 범위 | 내용 |
|----------|------|
| 3600-3700 | 전역 변수, 설정 |
| 3700-3900 | 데이터 로드 (loadData, loadFreshData) |
| 3900-4100 | 캐시 관리 |
| 4100-4300 | 월 선택, 대시보드 업데이트 |
| 4300-4700 | 차트 생성 (Chart.js) |
| 4700-5000 | 예산 관리 |
| 5000-5300 | 필터, 테이블 렌더링 |
| 5300-5600 | 카테고리 자동 추천 (CATEGORY_KEYWORDS) |
| 5600-5800 | 지출 저장/삭제 (submitExpense, deleteExpense) |
| 5800-5900 | 초기화, 이벤트 리스너 |

## 데이터 로딩 아키텍처

### 데이터 소스 (2계층)
- **정적 JSON** (`data/*.json`): 과거 월 아카이브. `data/index.json`에서 월 목록 동적 로드
- **Google Sheets** (`GOOGLE_SHEETS`): 최근 월 + 현재 월. Apps Script API로 시트 목록 조회

### 로딩 흐름 (`loadAllExpenses`)
1. `data/index.json` fetch → 아카이브된 월 목록 확인
2. `GOOGLE_SHEETS`에 있는 월은 JSON 로드에서 제외 (중복 방지)
3. 과거 월: localStorage 캐시 히트 시 스킵 (30일 유효)
4. 현재 월: 항상 Google Sheets에서 새로 로드 (`isCurrentMonth()` 체크)

### 캐시 구조 (localStorage)
| 키 | 용도 | 만료 |
|----|------|------|
| `smss_accountbook_cache_v2` | 전체 데이터 캐시 (즉시 표시용) | 5분 |
| `smss_expense_month_cache` | 월별 개별 캐시 (과거 월 스킵용) | 30일 |
| `smss_sheet_list_cache` | 시트 목록 캐시 | 5분 |

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
- `loadFreshData()` - API에서 새 데이터 가져오기
- `loadAllExpenses()` - 월별 병렬 로드 (JSON + Sheets, 캐시 적용)
- `submitExpense()` - 지출 저장
- `deleteExpenseByData()` - 지출 삭제

### UI 관련
- `renderExpenseTable()` - 상세내역 테이블 렌더링
- `updateDashboard()` - 대시보드 전체 업데이트
- `showToast()` - 토스트 알림 표시
- `openInputModal()` / `closeInputModal()` - 입력 모달

### 설정 관련
- `loadSettings()` / `saveSettings()` - 카테고리/결제수단 설정
- `suggestCategory()` - 키워드 기반 카테고리 자동 추천

## 카테고리 키워드 매핑 (CATEGORY_KEYWORDS)
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
- 모바일 반응형 (`@media (max-width: 768px)`) 확인
- PWA standalone 모드 스크롤 이슈 주의
- `service-worker.js` 수정 시 `CACHE_NAME` 버전 올려야 기존 캐시 갱신됨
- `data/index.json`에 새 월 추가 시 자동으로 JSON 로드 대상에 포함됨
- `GOOGLE_SHEETS`에 있는 월은 JSON보다 Sheets 우선 로드 (중복 방지 자동 처리)
