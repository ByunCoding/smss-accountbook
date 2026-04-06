# 할부 기능 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 지출 입력 폼에 무이자 할부 선택 기능을 추가하여, 총액과 개월 수 입력 시 각 월 시트에 분할 저장

**Architecture:** 금액 입력 행 옆에 개월 수 select를 추가하고, submitExpense에서 할부 선택 시 N번 순차 API 호출로 각 월에 저장. Apps Script는 변경 없이 기존 add action 재사용.

**Tech Stack:** Vanilla JS, HTML, CSS (단일 index.html 파일), Google Apps Script (변경 없음)

---

## 파일 변경 맵

| 파일 | 변경 내용 |
|------|----------|
| index.html HTML (~4210-4216) | 금액 행에 installmentWrapper 추가 (select + 미리보기) |
| index.html CSS (~2100-2400 입력 모달 섹션) | 가로 배치, 미리보기 스타일, 다크모드, 모바일 |
| index.html JS setInputType (4752) | income 모드 시 installmentWrapper 숨김/표시 |
| index.html JS openInputModal (7803) | 모달 열 때 select 초기화 |
| index.html JS applyQuickSuggestion (7915) | 빠른 입력 적용 시 select 초기화 |
| index.html JS openEditModal (8214) | 수정 모드 열 때 select 초기화 |
| index.html JS submitExpense (8027) | 할부 분기 처리, N번 순차 API 호출 |
| index.html JS 새 함수 updateInstallmentPreview | select 변경 시 미리보기 텍스트 업데이트 |

---

## Task 1: HTML — 금액 행에 할부 select와 미리보기 추가

**Files:**
- Modify: index.html:4210-4216

### 현재 코드 (4210-4216)

```html
<div class="input-form-group">
    <label><i class="ri-money-dollar-circle-line"></i> 금액</label>
    <div class="amount-input-wrapper">
        <input type="text" id="inputAmount" placeholder="0" required inputmode="numeric" oninput="formatAmountInput(this)">
        <span class="currency">원</span>
    </div>
</div>
```

- [ ] **Step 1: 금액 행 HTML 수정**

아래 코드로 교체:

```html
<div class="input-form-group" id="installmentFormGroup">
    <label><i class="ri-money-dollar-circle-line"></i> 금액</label>
    <div class="amount-installment-row">
        <div class="amount-input-wrapper">
            <input type="text" id="inputAmount" placeholder="0" required inputmode="numeric" oninput="formatAmountInput(this); updateInstallmentPreview();">
            <span class="currency">원</span>
        </div>
        <select id="inputInstallment" class="installment-select" onchange="updateInstallmentPreview()">
            <option value="1">일시불</option>
            <option value="2">2개월</option>
            <option value="3">3개월</option>
            <option value="6">6개월</option>
            <option value="12">12개월</option>
        </select>
    </div>
    <div class="installment-preview" id="installmentPreview" style="display:none;"></div>
</div>
```

- [ ] **Step 2: 브라우저에서 렌더링 확인**

index.html 을 브라우저로 열고 + 버튼 클릭.
금액 입력란 옆에 "일시불" 드롭다운이 보이는지 확인.
미리보기 div는 아직 숨겨진 상태여야 함.

- [ ] **Step 3: 커밋**

```bash
git add index.html
git commit -m "feat: 할부 select UI 추가 (HTML)"
```

---

## Task 2: CSS — 가로 배치, 미리보기 스타일, 다크모드, 모바일

**Files:**
- Modify: index.html CSS 섹션 (입력 모달 스타일, ~2100-2400)

기존 .amount-input-wrapper CSS 블록 아래에 추가할 스타일:

- [ ] **Step 1: CSS 추가**

CSS 섹션에서 `.amount-input-wrapper` 스타일 블록을 찾아 그 아래에 삽입:

```css
/* ===== 할부 선택 ===== */
.amount-installment-row {
    display: flex;
    gap: 8px;
    align-items: center;
}

.amount-installment-row .amount-input-wrapper {
    flex: 1;
}

.installment-select {
    flex-shrink: 0;
    padding: 12px 10px;
    border: 1.5px solid var(--gray-200);
    border-radius: 10px;
    background: var(--bg-card);
    color: var(--gray-700);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    outline: none;
    transition: border-color 0.2s;
    min-width: 72px;
}

.installment-select:focus {
    border-color: var(--primary);
}

.installment-preview {
    margin-top: 6px;
    padding: 8px 12px;
    background: rgba(37,99,235,0.08);
    border-radius: 8px;
    font-size: 0.82rem;
    color: var(--primary);
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}

[data-theme="dark"] .installment-select {
    background: var(--bg-card);
    border-color: var(--gray-600);
    color: var(--gray-200);
}

[data-theme="dark"] .installment-preview {
    background: rgba(37,99,235,0.15);
    color: #93c5fd;
}

@media (max-width: 768px) {
    .installment-select {
        min-width: 64px;
        font-size: 0.85rem;
        padding: 12px 8px;
    }
}
```

- [ ] **Step 2: 시각적으로 확인**

브라우저에서 모달 열기.
금액/드롭다운이 한 줄로 나란히 배치되는지 확인.
다크모드 전환 시 색상이 깨지지 않는지 확인.
모바일 크기(375px)로 좁혀도 드롭다운이 한 줄 유지되는지 확인.

- [ ] **Step 3: 커밋**

```bash
git add index.html
git commit -m "feat: 할부 select CSS 스타일 추가"
```

---

## Task 3: JS — updateInstallmentPreview 함수 추가

**Files:**
- Modify: index.html JS 섹션 (submitExpense 함수 8027줄 바로 위에 삽입)

DOM API를 사용해 안전하게 렌더링 (innerHTML 사용 금지):

- [ ] **Step 1: 함수 추가**

submitExpense 함수(8027줄) 바로 위에 삽입:

```javascript
// 할부 미리보기 업데이트 (DOM API 사용, innerHTML 금지)
function updateInstallmentPreview() {
    const installmentEl = document.getElementById('inputInstallment');
    const preview = document.getElementById('installmentPreview');
    if (!preview || !installmentEl) return;

    const months = parseInt(installmentEl.value || '1');
    if (months <= 1) {
        preview.style.display = 'none';
        return;
    }

    const rawAmount = (document.getElementById('inputAmount').value || '').replace(/,/g, '');
    const total = parseInt(rawAmount) || 0;
    if (total <= 0) {
        preview.style.display = 'none';
        return;
    }

    const monthly = Math.floor(total / months);

    preview.textContent = '';
    const icon = document.createElement('i');
    icon.className = 'ri-bank-card-line';
    const text = document.createTextNode(
        ' 월 ' + monthly.toLocaleString() + '원 \u00d7 ' + months + '개월 = ' + total.toLocaleString() + '원'
    );
    preview.appendChild(icon);
    preview.appendChild(text);
    preview.style.display = 'flex';
}
```

- [ ] **Step 2: 동작 확인**

브라우저에서 금액에 300000 입력 후 3개월 선택.
미리보기에 "월 100,000원 × 3개월 = 300,000원" 이 표시되는지 확인.
일시불 선택 시 미리보기 사라지는지 확인.
금액을 지우면 미리보기 사라지는지 확인.

- [ ] **Step 3: 커밋**

```bash
git add index.html
git commit -m "feat: 할부 미리보기 함수 추가"
```

---

## Task 4: JS — 모달 초기화 함수들에 할부 reset 추가

**Files:**
- Modify: index.html JS
  - openInputModal (7803)
  - openEditModal (8214)
  - applyQuickSuggestion (7915)
  - setInputType (4752)

아래 초기화 헬퍼 코드를 각 함수에 삽입한다:

```javascript
// 할부 초기화 스니펫 (각 함수에 복사)
const installmentEl = document.getElementById('inputInstallment');
if (installmentEl) installmentEl.value = '1';
const previewEl = document.getElementById('installmentPreview');
if (previewEl) previewEl.style.display = 'none';
```

### 4-1. openInputModal

- [ ] **Step 1:** renderQuickSuggestions() 호출 바로 위에 초기화 스니펫 삽입.

### 4-2. openEditModal

- [ ] **Step 2:** 함수 마지막 setTimeout 블록 위에 초기화 스니펫 삽입.

### 4-3. applyQuickSuggestion

- [ ] **Step 3:** 함수 마지막 줄(inputAmount value 설정) 뒤에 초기화 스니펫 삽입.

### 4-4. setInputType

- [ ] **Step 4:** income 분기와 expense 분기에 각각 추가.

income 블록 끝에 추가:
```javascript
// 할부 숨기기
const installmentFormGroup = document.getElementById('installmentFormGroup');
if (installmentFormGroup) installmentFormGroup.style.display = 'none';
```

expense 블록 끝에 추가:
```javascript
// 할부 표시 및 초기화
const installmentFormGroup = document.getElementById('installmentFormGroup');
if (installmentFormGroup) installmentFormGroup.style.display = '';
const installmentEl = document.getElementById('inputInstallment');
if (installmentEl) installmentEl.value = '1';
const previewEl = document.getElementById('installmentPreview');
if (previewEl) previewEl.style.display = 'none';
```

- [ ] **Step 5: 동작 확인**

1. 모달 열기 → 할부 select가 "일시불"인지 확인
2. 3개월 선택 후 모달 닫고 다시 열기 → "일시불"로 초기화되는지 확인
3. 수입 탭 클릭 → 할부 영역 사라지는지 확인
4. 지출 탭 클릭 → 할부 영역 다시 보이고 "일시불"인지 확인
5. 3개월 선택 후 빠른 입력 클릭 → "일시불"로 초기화되는지 확인
6. 기존 지출 내역 수정 클릭 → "일시불"로 초기화되는지 확인

- [ ] **Step 6: 커밋**

```bash
git add index.html
git commit -m "feat: 모달 초기화 시 할부 select 리셋 추가"
```

---

## Task 5: JS — submitExpense 할부 분기 처리

**Files:**
- Modify: index.html JS submitExpense (8027)

submitExpense 내 지출 저장 블록(8128줄 이후 `} else {` 블록)을 아래 코드로 교체.
수입(isIncome) 블록은 건드리지 말 것.

- [ ] **Step 1: 지출 저장 블록 교체**

기존 else 블록:
```javascript
} else {
    // 지출은 기존 지출 시트에 저장
    const params = new URLSearchParams({
        action: 'add',
        year: year.toString(),
        date: date,
        category: category,
        item: description,
        person: payment,
        amount: amount.toString()
    });

    await fetch(`${APPS_SCRIPT_URL}?${params.toString()}`);

    console.log('Expense submitted to Apps Script');

    // 로컬 데이터에도 추가 (즉시 반영)
    const newExpense = {
        date: date,
        year: year,
        month: month,
        category: category,
        description: description,
        amount: amount,
        payment_method: payment,
        isFixed: FIXED_CATEGORIES.includes(category),
        id: `local_${Date.now()}`
    };

    expenseData.expenses.push(newExpense);
}
```

교체할 코드:
```javascript
} else {
    // 지출 저장 (일시불 또는 할부)
    const months = parseInt(document.getElementById('inputInstallment')?.value || '1');
    const [origYear, origMonth, origDay] = date.split('-').map(Number);

    if (months <= 1) {
        // 일시불: 기존 로직 그대로
        const params = new URLSearchParams({
            action: 'add',
            year: year.toString(),
            date: date,
            category: category,
            item: description,
            person: payment,
            amount: amount.toString()
        });
        await fetch(`${APPS_SCRIPT_URL}?${params.toString()}`);
        console.log('Expense submitted to Apps Script');

        expenseData.expenses.push({
            date: date,
            year: year,
            month: month,
            category: category,
            description: description,
            amount: amount,
            payment_method: payment,
            isFixed: FIXED_CATEGORIES.includes(category),
            id: `local_${Date.now()}_0`
        });
    } else {
        // 할부: N번 순차 호출
        const monthlyAmount = Math.floor(amount / months);
        let savedCount = 0;

        for (let n = 0; n < months; n++) {
            const installmentDate = new Date(origYear, origMonth - 1 + n, origDay);
            const iYear = installmentDate.getFullYear();
            const iMonth = installmentDate.getMonth() + 1;
            const iDay = installmentDate.getDate();
            const iDateStr = iYear + '-' + String(iMonth).padStart(2, '0') + '-' + String(iDay).padStart(2, '0');
            const iAmount = (n === months - 1)
                ? amount - monthlyAmount * (months - 1)
                : monthlyAmount;
            const iDesc = (description ? description + ' ' : '') + '(' + (n + 1) + '/' + months + ')';

            try {
                const params = new URLSearchParams({
                    action: 'add',
                    year: iYear.toString(),
                    date: iDateStr,
                    category: category,
                    item: iDesc,
                    person: payment,
                    amount: iAmount.toString()
                });
                await fetch(`${APPS_SCRIPT_URL}?${params.toString()}`);

                expenseData.expenses.push({
                    date: iDateStr,
                    year: iYear,
                    month: iMonth,
                    category: category,
                    description: iDesc,
                    amount: iAmount,
                    payment_method: payment,
                    isFixed: FIXED_CATEGORIES.includes(category),
                    id: 'local_' + Date.now() + '_' + n
                });
                savedCount++;
            } catch (e) {
                showToast(savedCount + '/' + months + '개월 저장 중 오류 발생. 일부만 저장되었을 수 있습니다.', 'error');
                throw e;
            }
        }

        // 할부 성공: 직접 마무리 처리 후 return (아래 공통 처리 건너뜀)
        calculateSummary();
        updateDashboard();
        setCachedData(expenseData.expenses);
        showToast(amount.toLocaleString() + '원 → ' + months + '개월 할부로 저장되었습니다 (월 ' + monthlyAmount.toLocaleString() + '원)');
        closeInputModal();
        renderExpenseTable();
        return;
    }
}
```

- [ ] **Step 2: 일시불 저장 확인**

브라우저에서 금액 50000, 일시불 선택 후 저장.
기존과 동일하게 저장되는지 확인.
콘솔에 "Expense submitted to Apps Script" 로그 확인.

- [ ] **Step 3: 할부 저장 확인**

금액 300000, 3개월 선택 후 저장.
네트워크 탭에서 Apps Script URL이 3번 호출되었는지 확인.
각 호출의 item 파라미터: (1/3), (2/3), (3/3) 인지 확인.
각 호출의 date가 1개월씩 밀려 있는지 확인.
토스트: "300,000원 → 3개월 할부로 저장되었습니다 (월 100,000원)" 표시되는지 확인.

- [ ] **Step 4: 크로스 연도 확인 (선택)**

날짜 2026-12-15, 금액 60000, 3개월 선택 후 저장.
각 API 호출의 date와 year 확인:
- 1/3: 2026-12-15, year=2026
- 2/3: 2027-01-15, year=2027
- 3/3: 2027-02-15, year=2027

- [ ] **Step 5: 말일 처리 확인 (선택)**

날짜 2026-01-31, 2개월 할부.
2/2 호출의 date가 2026-02-28인지 확인 (JS 자동 처리).

- [ ] **Step 6: 커밋**

```bash
git add index.html
git commit -m "feat: submitExpense 할부 분기 처리 추가"
```

---

## Task 6: 최종 통합 테스트 및 배포

- [ ] **Step 1: 전체 시나리오 체크리스트**

| 시나리오 | 기대 결과 |
|----------|----------|
| 일시불 저장 | 기존과 동일 |
| 3개월 할부, 메모 있음 | "에어팟 (1/3)" 형태로 각 월에 저장 |
| 3개월 할부, 메모 없음 | "(1/3)" 형태로 각 월에 저장 |
| 수입 탭 전환 | 할부 영역 사라짐 |
| 수정 모드 열기 | 할부 일시불로 초기화 |
| 빠른 입력 클릭 | 할부 일시불로 초기화 |
| 모달 닫고 다시 열기 | 할부 일시불로 초기화 |
| 다크모드 | 미리보기 색상 정상 |
| 모바일 375px | select가 1줄 배치 유지 |

- [ ] **Step 2: 배포**

```bash
git add index.html
git commit -m "feat: 할부 기능 완성 - 지출 입력 시 무이자 분할 저장"
git push
```

GitHub Pages 자동 배포 (1-2분 소요) 후 실제 사이트에서 최종 확인.
