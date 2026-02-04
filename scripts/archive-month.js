#!/usr/bin/env node
/**
 * archive-month.js
 * 지난달 Google Sheets 데이터를 JSON 파일로 아카이브
 *
 * 사용법: node scripts/archive-month.js [YYYY-MM]
 * - 인자 없으면 지난달 자동 계산
 * - 인자 있으면 해당 월 아카이브
 */

const fs = require('fs');
const path = require('path');

// 설정
const SHEET_ID = '1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk';
const SHEET_LIST_URL = 'https://script.google.com/macros/s/AKfycbwg7wuVXbkdaua3yCqIWPyrjSXW8070LNCzkWidcLHy82VRctMYw554iyYGV2TqlDpdOQ/exec';
const DATA_DIR = path.join(__dirname, '..', 'data');
const INDEX_FILE = path.join(DATA_DIR, 'index.json');

// 고정비 카테고리
const FIXED_CATEGORIES = ['관리비', '대출이자', '보험료', '통신비', '구독료', '교육비'];

// 지난달 계산
function getTargetMonth(arg) {
    if (arg) {
        const match = arg.match(/^(\d{4})-(\d{2})$/);
        if (!match) {
            console.error(`잘못된 형식: ${arg} (YYYY-MM 형식 사용)`);
            process.exit(1);
        }
        return arg;
    }
    const now = new Date();
    const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    return `${lastMonth.getFullYear()}-${String(lastMonth.getMonth() + 1).padStart(2, '0')}`;
}

// Apps Script에서 시트 목록 조회
async function getSheetList() {
    const response = await fetch(`${SHEET_LIST_URL}?action=getSheetList`);
    const result = await response.json();
    if (!result.success || !result.sheets) {
        throw new Error('시트 목록 조회 실패: ' + JSON.stringify(result));
    }
    return result.sheets; // [{ monthKey: '2026-01', gid: 123, name: '26.1' }, ...]
}

// Google Sheets CSV 가져오기
async function fetchSheetCSV(gid) {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?tqx=out:csv&gid=${gid}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`CSV 가져오기 실패: ${response.status}`);
    return response.text();
}

// CSV 라인 파싱 (따옴표 처리)
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') inQuotes = !inQuotes;
        else if (char === ',' && !inQuotes) { result.push(current); current = ''; }
        else current += char;
    }
    result.push(current);
    return result;
}

// CSV → 지출/수입 데이터 파싱
function parseCSV(csvText, monthKey, gid) {
    const lines = csvText.split('\n');
    const expenses = [];
    const income = [];
    const [year, month] = monthKey.split('-').map(Number);

    for (let i = 0; i < lines.length; i++) {
        const columns = parseCSVLine(lines[i]);

        // A-F열: 지출 데이터
        const dateStr = columns[0]?.trim();
        if (dateStr && dateStr.match(/^\d{4}[\.\-]/)) {
            const rawCategory = columns[1]?.trim();
            const category = rawCategory === '공유숙박' ? '부수입' : rawCategory;
            const description = columns[2]?.trim();
            const amountStr = columns[3]?.replace(/[",₩\s]/g, '');
            const amount = parseFloat(amountStr);
            const paymentMethod = columns[5]?.trim();

            if (category && amount && !isNaN(amount)) {
                let normalizedDate = dateStr.replace(/\.\s*/g, '-').replace(/-$/, '');
                if (normalizedDate.match(/^\d{4}-\d{1,2}-\d{1,2}$/)) {
                    const parts = normalizedDate.split('-');
                    normalizedDate = `${parts[0]}-${parts[1].padStart(2, '0')}-${parts[2].padStart(2, '0')}`;
                }

                expenses.push({
                    date: normalizedDate,
                    year, month, category,
                    description: description || '',
                    amount,
                    payment_method: paymentMethod || '미지정',
                    isFixed: FIXED_CATEGORIES.includes(category),
                    id: `legacy_${String(i).padStart(6, '0')}`
                });
            }
        }

        // H-K열: 수입 데이터 (columns[7]=H, [8]=I, [9]=J, [10]=K)
        const incomeDateStr = columns[7]?.trim();
        if (incomeDateStr && incomeDateStr.match(/^\d{4}[\.\-]/)) {
            const incomeCategory = columns[8]?.trim();
            const incomeDesc = columns[9]?.trim();
            const incomeAmountStr = columns[10]?.replace(/[",₩\s]/g, '');
            const incomeAmount = parseFloat(incomeAmountStr);

            if (incomeCategory && incomeAmount && !isNaN(incomeAmount)) {
                let normalizedIncomeDate = incomeDateStr.replace(/\.\s*/g, '-').replace(/-$/, '');
                if (normalizedIncomeDate.match(/^\d{4}-\d{1,2}-\d{1,2}$/)) {
                    const parts = normalizedIncomeDate.split('-');
                    normalizedIncomeDate = `${parts[0]}-${parts[1].padStart(2, '0')}-${parts[2].padStart(2, '0')}`;
                }

                income.push({
                    date: normalizedIncomeDate,
                    year, month,
                    category: incomeCategory,
                    description: incomeDesc || '',
                    amount: incomeAmount,
                    id: `income_${String(i).padStart(6, '0')}`
                });
            }
        }
    }

    return { expenses, income };
}

// index.json 업데이트
function updateIndex(monthKey) {
    let index = [];
    if (fs.existsSync(INDEX_FILE)) {
        index = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf-8'));
    }
    if (!index.includes(monthKey)) {
        index.push(monthKey);
        index.sort();
        fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2) + '\n');
        console.log(`index.json 업데이트: ${monthKey} 추가`);
    } else {
        console.log(`index.json: ${monthKey} 이미 존재`);
    }
}

// 메인 실행
async function main() {
    const targetMonth = getTargetMonth(process.argv[2]);
    console.log(`아카이브 대상: ${targetMonth}`);

    // 이미 아카이브 파일이 있는지 확인
    const outputFile = path.join(DATA_DIR, `${targetMonth}.json`);
    if (fs.existsSync(outputFile)) {
        console.log(`${outputFile} 이미 존재 → 덮어쓰기`);
    }

    // 시트 목록 조회
    console.log('시트 목록 조회 중...');
    const sheets = await getSheetList();
    const targetSheet = sheets.find(s => s.monthKey === targetMonth);

    if (!targetSheet) {
        console.error(`${targetMonth} 시트를 찾을 수 없습니다.`);
        console.log('사용 가능한 시트:', sheets.map(s => s.monthKey).join(', '));
        process.exit(1);
    }

    console.log(`시트 발견: ${targetSheet.name} (GID: ${targetSheet.gid})`);

    // CSV 가져오기
    console.log('CSV 데이터 다운로드 중...');
    const csv = await fetchSheetCSV(targetSheet.gid);

    // 파싱
    const { expenses, income } = parseCSV(csv, targetMonth, targetSheet.gid);
    console.log(`파싱 완료: 지출 ${expenses.length}건, 수입 ${income.length}건`);

    // JSON 저장
    const output = income.length > 0 ? { expenses, income } : expenses;
    fs.writeFileSync(outputFile, JSON.stringify(output, null, 2) + '\n');
    console.log(`저장 완료: ${outputFile}`);

    // index.json 업데이트
    updateIndex(targetMonth);

    console.log('아카이브 완료!');
}

main().catch(err => {
    console.error('아카이브 실패:', err);
    process.exit(1);
});
