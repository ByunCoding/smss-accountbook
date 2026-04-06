# 할부 기능 설계 문서

**날짜**: 2026-04-07
**프로젝트**: smss-accountbook
**상태**: 승인됨

---

## 개요

지출 입력 폼에 무이자 할부 개념을 추가한다. 사용자가 총액과 개월 수를 입력하면 앱이 자동으로 각 월에 분할된 금액을 저장한다.

---

## 요구사항

- 무이자 할부만 지원 (이자 계산 없음)
- 지원 개월 수: 일시불, 2, 3, 6, 12개월
- 메모 자동 표기: `에어팟 (1/3)`, `에어팟 (2/3)`, `에어팟 (3/3)`
- 할부 미리보기: 개월 선택 시 `월 100,000원 × 3개월 = 300,000원` 표시 (Remixicon `ri-bank-card-line` 아이콘 사용, 이모지 사용 금지)
- 기존 일시불 동작은 완전히 동일하게 유지
- 수입 입력 모드에서는 할부 선택 필드 숨김

---

## 선행 확인 사항 (구현 차단 조건)

**Apps Script `add` action의 미래 월 시트 자동 생성 여부**를 반드시 구현 전 확인해야 한다.

- 6개월, 12개월 할부 시 현재 월 이후 시트가 존재하지 않을 수 있음
- Apps Script가 해당 월 시트를 자동 생성하지 않으면 저장 실패
- 확인 방법: Apps Script 코드에서 `add` action이 시트를 없을 때 새로 만드는지 검토
- 자동 생성하지 않는다면: 구현 범위를 현재 월 + GOOGLE_SHEETS에 정의된 월로 제한하거나, Apps Script 수정 필요

---

## UI 설계

### 금액 입력 행 변경

기존:
```
[금액 라벨]
[금액 입력 ____원]
```

변경 후:
```
[금액 라벨]
[금액 입력 ____원] [일시불 ▼]
[미리보기: <ri-bank-card-line> 월 100,000원 × 3개월 = 300,000원]  ← 할부 선택 시만 표시
```

### 드롭다운 옵션
- 일시불 (기본값, value="1")
- 2개월 (value="2")
- 3개월 (value="3")
- 6개월 (value="6")
- 12개월 (value="12")

### 수입 모드에서 처리
`setInputType('income')` 호출 시 `#installmentWrapper`(select + 미리보기 묶음) `display: none`.
`setInputType('expense')` 호출 시 다시 표시.

---

## 데이터 처리

### 금액 나머지 처리 (명시적 규칙)

```
월 금액 = Math.floor(totalAmount / months)
마지막 달 금액 = totalAmount - (월 금액 × (months - 1))
```

예: 100,000원 / 3개월 → 33,333 + 33,333 + 33,334

### 일시불 (기존 동작 유지)

`installments === 1` 이면 기존 `submitExpense` 로직 그대로 실행.

### 할부 처리 흐름

1. totalAmount, months 읽기
2. 월 금액 = `Math.floor(totalAmount / months)`, 마지막 달 금액 = 나머지 합산
3. 각 달(N = 0, 1, ..., months-1) 순회:
   - **날짜**: `new Date(origYear, origMonth - 1 + N, origDay)` → JS 자동 오버플로우 처리
   - **year 파라미터**: 반드시 computed Date에서 `getFullYear()` 추출 (크로스 연도 처리)
   - **month 파라미터**: computed Date에서 `getMonth() + 1` 추출
   - **메모**: `${description ? description + ' ' : ''}(${N+1}/${months})`
   - **금액**: N < months-1 이면 월 금액, N === months-1 이면 마지막 달 금액
4. Apps Script `add` action 호출 (순차, await)
5. **오류 처리**: 특정 달 호출 실패 시 즉시 중단. 토스트: `"N/${months}개월 저장 중 오류 발생. 일부만 저장되었을 수 있습니다."`
6. 로컬 `expenseData.expenses`에 N개 항목 추가:
   - `id: \`local_${Date.now()}_${N}\`` (중복 방지를 위해 인덱스 접미사 포함)
7. 성공 토스트: `"300,000원 → 3개월 할부로 저장되었습니다 (월 100,000원)"`

### 메모 생성 규칙

```
원본 메모가 있을 때:  "에어팟 (1/3)", "에어팟 (2/3)", "에어팟 (3/3)"
원본 메모가 없을 때:  "(1/3)", "(2/3)", "(3/3)"
```

---

## 변경 파일 및 범위

| 항목 | 변경 내용 |
|------|----------|
| HTML | 금액 행에 `#installmentWrapper` div 추가 (`#inputInstallment` select + `#installmentPreview` span 포함) |
| CSS | 금액-개월 수 가로 배치 (`display: flex`, `gap`), 미리보기 스타일 (소문자, primary 컬러), 다크모드 대응 |
| JS `submitExpense` | 할부 분기 처리, N번 순차 API 호출, 크로스 연도 year 처리, 오류 처리 |
| JS `openInputModal` | `#inputInstallment` → value="1" 초기화, `#installmentPreview` 숨김 |
| JS `openEditModal` | `#inputInstallment` → value="1" 초기화, `#installmentPreview` 숨김 (수정 모드에서도 초기화 필요) |
| JS `setInputType` | income 모드 시 `#installmentWrapper` 숨김, expense 모드 시 표시 |
| JS `applyQuickSuggestion` | 빠른 입력 적용 시 `#inputInstallment` → value="1" 초기화, `#installmentPreview` 숨김 |
| JS 새 함수 `updateInstallmentPreview` | select 변경 시 미리보기 텍스트 업데이트 |
| Apps Script | **변경 없음** — 기존 `add` action 재사용 |

---

## 주의사항

- **Apps Script 미래 월 시트 자동 생성 여부**: 구현 전 확인 필수 (선행 확인 사항 섹션 참고)
- 할부 항목 삭제는 각 달에서 개별 삭제 (일반 지출과 동일). 전체 취소 기능은 이번 범위 외.
- 수정(edit) 모드에서 할부 항목은 해당 달 단일 항목만 수정 (기존 수정 로직 재사용, 할부 select는 일시불로 초기화).
- 다크모드(`[data-theme="dark"]`), 모바일 반응형(`@media (max-width: 768px)`) CSS 동시 적용 필요.
- 미래 월은 항상 새로 로드되므로 별도 캐시 무효화 불필요.
