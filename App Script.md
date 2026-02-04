function doGet(e) {
  var action = e.parameter.action;

  if (action === 'getSheetList') {
    var result = getSheetList();
    return ContentService.createTextOutput(JSON.stringify({success: true, sheets: result.sheets, incomeSheetGid: result.incomeSheetGid})).setMimeType(ContentService.MimeType.JSON);
  }

  if (action === 'add') {
    var result = addExpense(e.parameter.date, e.parameter.category, e.parameter.item, e.parameter.person, e.parameter.amount, e.parameter.year);
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  }

  if (action === 'delete') {
    var result = deleteExpense(e.parameter.date, e.parameter.category, e.parameter.item, e.parameter.person, e.parameter.amount);
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  }

  if (action === 'addIncome') {
    var result = addIncome(e.parameter.date, e.parameter.category, e.parameter.item, e.parameter.amount, e.parameter.year);
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  }

  if (action === 'deleteIncome') {
    var result = deleteIncome(e.parameter.date, e.parameter.category, e.parameter.item, e.parameter.amount);
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  }

  if (action === 'getSettings') {
    var result = getSettings();
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  }

  if (action === 'saveSettings') {
    var settings = JSON.parse(e.parameter.settings);
    var result = saveSettingsData(settings);
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  }

  return ContentService.createTextOutput(JSON.stringify({success: false, error: 'Unknown action'})).setMimeType(ContentService.MimeType.JSON);
}

function getSheetList() {
  var ss = SpreadsheetApp.openById('1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk');
  var sheets = ss.getSheets();
  var sheetList = [];
  var incomeSheetGid = null;
  for (var i = 0; i < sheets.length; i++) {
    var name = sheets[i].getName();
    if (/^\d{2}\.\d{1,2}$/.test(name)) {
      var parts = name.split('.');
      var year = '20' + parts[0];
      var month = parts[1].length === 1 ? '0' + parts[1] : parts[1];
      sheetList.push({name: name, monthKey: year + '-' + month, gid: sheets[i].getSheetId()});
    }
    if (name === '수입') {
      incomeSheetGid = sheets[i].getSheetId();
    }
  }
  return {sheets: sheetList, incomeSheetGid: incomeSheetGid};
}

function getSheetNameFromDate(dateStr, year) {
  var parts = dateStr.split('-');
  var month = parseInt(parts[1], 10);
  var yy = String(year).slice(-2);
  return yy + '.' + month;
}

function getOrCreateSheet(ss, sheetName) {
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }
  return sheet;
}

function findNextEmptyRow(sheet, startRow) {
  var colA = sheet.getRange(startRow, 1, 200, 1).getValues();
  for (var i = 0; i < colA.length; i++) {
    if (colA[i][0] === '' || colA[i][0] === null) {
      return startRow + i;
    }
  }
  return startRow + colA.length;
}

function normalizeDate(dateValue) {
  if (dateValue instanceof Date) {
    var yyyy = dateValue.getFullYear();
    var mm = String(dateValue.getMonth() + 1);
    var dd = String(dateValue.getDate());
    if (mm.length === 1) mm = '0' + mm;
    if (dd.length === 1) dd = '0' + dd;
    return yyyy + '-' + mm + '-' + dd;
  }
  if (typeof dateValue === 'string') {
    var cleaned = dateValue.replace(/\.\s*/g, '-').replace(/-$/, '');
    var parts = cleaned.split('-');
    if (parts.length === 3) {
      var y = parts[0];
      var m = parts[1].length === 1 ? '0' + parts[1] : parts[1];
      var d = parts[2].length === 1 ? '0' + parts[2] : parts[2];
      return y + '-' + m + '-' + d;
    }
  }
  return '';
}

function addExpense(date, category, item, person, amount, year) {
  try {
    var ss = SpreadsheetApp.openById('1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk');
    var sheetName = getSheetNameFromDate(date, year);
    var sheet = getOrCreateSheet(ss, sheetName);
    var newRow = findNextEmptyRow(sheet, 10);
    sheet.getRange(newRow, 1).setValue(date);
    sheet.getRange(newRow, 2).setValue(category);
    sheet.getRange(newRow, 3).setValue(item);
    sheet.getRange(newRow, 4).setValue(Number(amount));
    sheet.getRange(newRow, 6).setValue(person);
    return {success: true, message: 'Added', row: newRow};
  } catch (error) {
    return {success: false, error: error.toString()};
  }
}

function deleteExpense(date, category, item, person, amount) {
  try {
    var ss = SpreadsheetApp.openById('1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk');
    var dateParts = date.split('-');
    var year = dateParts[0];
    var month = parseInt(dateParts[1], 10);
    var sheetName = year.slice(-2) + '.' + month;
    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      return {success: false, error: 'Sheet not found'};
    }
    var data = sheet.getDataRange().getValues();
    var targetAmount = Number(amount);
    var targetDate = date;

    for (var i = data.length - 1; i >= 1; i--) {
      var row = data[i];
      var rowDate = normalizeDate(row[0]);
      var rowAmount = Number(String(row[3]).replace(/[,]/g, ''));

      if (rowDate === targetDate && row[1] === category && rowAmount === targetAmount) {
        sheet.deleteRow(i + 1);
        return {success: true, message: 'Deleted', row: i + 1};
      }
    }
    return {success: false, error: 'Not found'};
  } catch (error) {
    return {success: false, error: error.toString()};
  }
}

// ===== 수입 관리 (월별 시트 H-K열) =====

function findNextEmptyRowInColumn(sheet, col, startRow) {
  var colData = sheet.getRange(startRow, col, 200, 1).getValues();
  for (var i = 0; i < colData.length; i++) {
    if (colData[i][0] === '' || colData[i][0] === null) {
      return startRow + i;
    }
  }
  return startRow + colData.length;
}

function addIncome(date, category, item, amount, year) {
  try {
    var ss = SpreadsheetApp.openById('1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk');
    var sheetName = getSheetNameFromDate(date, year);
    var sheet = getOrCreateSheet(ss, sheetName);
    var newRow = findNextEmptyRowInColumn(sheet, 8, 10); // H열(8) 기준
    sheet.getRange(newRow, 8).setValue(date);       // H열: 날짜
    sheet.getRange(newRow, 9).setValue(category);    // I열: 카테고리
    sheet.getRange(newRow, 10).setValue(item || ''); // J열: 메모
    sheet.getRange(newRow, 11).setValue(Number(amount)); // K열: 금액
    return {success: true, message: 'Income added', row: newRow};
  } catch (error) {
    return {success: false, error: error.toString()};
  }
}

function deleteIncome(date, category, item, amount) {
  try {
    var ss = SpreadsheetApp.openById('1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk');
    var dateParts = date.split('-');
    var year = dateParts[0];
    var month = parseInt(dateParts[1], 10);
    var sheetName = year.slice(-2) + '.' + month;
    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      return {success: false, error: 'Sheet not found'};
    }
    var lastRow = sheet.getLastRow();
    if (lastRow < 10) {
      return {success: false, error: 'Not found'};
    }
    var data = sheet.getRange(10, 8, lastRow - 9, 4).getValues(); // H-K열, 10행부터
    var targetAmount = Number(amount);

    for (var i = data.length - 1; i >= 0; i--) {
      var row = data[i];
      var rowDate = normalizeDate(row[0]);
      var rowAmount = Number(String(row[3]).replace(/[,]/g, ''));

      if (rowDate === date && row[1] === category && rowAmount === targetAmount) {
        var actualRow = 10 + i;
        // 행 삭제 불가 (지출 데이터 보호) → H-K 셀만 클리어
        sheet.getRange(actualRow, 8, 1, 4).clearContent();
        return {success: true, message: 'Income deleted', row: actualRow};
      }
    }
    return {success: false, error: 'Not found'};
  } catch (error) {
    return {success: false, error: error.toString()};
  }
}

// ===== 설정 관리 =====

function getSettings() {
  try {
    var ss = SpreadsheetApp.openById('1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk');
    var sheet = ss.getSheetByName('SETTINGS');

    if (!sheet) {
      return { success: true, settings: getDefaultSettings() };
    }

    var lastRow = sheet.getLastRow();
    if (lastRow <= 1) {
      return { success: true, settings: getDefaultSettings() };
    }

    var data = sheet.getRange(2, 1, lastRow - 1, 4).getValues();
    var categories = [];
    var paymentMethods = [];
    var budgets = {};
    var incomeCategories = [];
    var recurringIncomes = [];

    for (var i = 0; i < data.length; i++) {
      var type = data[i][0];
      var name = data[i][1];
      var emoji = data[i][2];
      var color = data[i][3];

      if (!name) continue;

      if (type === 'category') {
        categories.push({ name: name, emoji: emoji || '🏷️', color: color || '#9CA3AF' });
      } else if (type === 'payment') {
        paymentMethods.push({ name: name, emoji: emoji || '💳' });
      } else if (type === 'budget') {
        budgets[name] = Number(color) || 0;
      } else if (type === 'income') {
        incomeCategories.push({ name: name, emoji: emoji || '💰', amount: Number(color) || 0 });
      } else if (type === 'recurring') {
        try {
          var meta = JSON.parse(emoji);
          recurringIncomes.push({
            id: meta.id,
            category: name,
            amount: Number(color) || 0,
            description: meta.description || '',
            dayOfMonth: meta.dayOfMonth || 1,
            createdMonths: meta.createdMonths || []
          });
        } catch (e) {
          // JSON 파싱 실패 시 스킵
        }
      }
    }

    if (categories.length === 0 && paymentMethods.length === 0) {
      return { success: true, settings: getDefaultSettings() };
    }

    var result = { categories: categories, paymentMethods: paymentMethods };
    if (Object.keys(budgets).length > 0) {
      result.budgets = budgets;
    }
    if (incomeCategories.length > 0) {
      result.incomeCategories = incomeCategories;
    }
    result.recurringIncomes = recurringIncomes;
    return { success: true, settings: result };
  } catch (error) {
    return { success: false, error: error.toString() };
  }
}

function saveSettingsData(settings) {
  try {
    var ss = SpreadsheetApp.openById('1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk');
    var sheet = ss.getSheetByName('SETTINGS');

    if (!sheet) {
      sheet = ss.insertSheet('SETTINGS');
      sheet.getRange('A1:D1').setValues([['type', 'name', 'emoji', 'color']]);
    }

    var lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      sheet.deleteRows(2, lastRow - 1);
    }

    var rows = [];

    for (var i = 0; i < settings.categories.length; i++) {
      var cat = settings.categories[i];
      rows.push(['category', cat.name, cat.emoji, cat.color]);
    }

    for (var j = 0; j < settings.paymentMethods.length; j++) {
      var pm = settings.paymentMethods[j];
      rows.push(['payment', pm.name, pm.emoji, '']);
    }

    // 예산 저장
    if (settings.budgets) {
      var budgetKeys = Object.keys(settings.budgets);
      for (var k = 0; k < budgetKeys.length; k++) {
        rows.push(['budget', budgetKeys[k], '', settings.budgets[budgetKeys[k]]]);
      }
    }

    // 수입 카테고리 저장
    if (settings.incomeCategories) {
      for (var m = 0; m < settings.incomeCategories.length; m++) {
        var ic = settings.incomeCategories[m];
        rows.push(['income', ic.name, ic.emoji, ic.amount || 0]);
      }
    }

    // 고정수입 저장
    if (settings.recurringIncomes) {
      for (var r = 0; r < settings.recurringIncomes.length; r++) {
        var ri = settings.recurringIncomes[r];
        var meta = JSON.stringify({
          id: ri.id,
          description: ri.description || '',
          dayOfMonth: ri.dayOfMonth || 1,
          createdMonths: ri.createdMonths || []
        });
        rows.push(['recurring', ri.category, meta, ri.amount || 0]);
      }
    }

    if (rows.length > 0) {
      sheet.getRange(2, 1, rows.length, 4).setValues(rows);
    }

    return { success: true };
  } catch (error) {
    return { success: false, error: error.toString() };
  }
}

function getDefaultSettings() {
  return {
    categories: [
      { name: '외식', emoji: '🍽️', color: '#F97316' },
      { name: '식비', emoji: '🛒', color: '#22C55E' },
      { name: '카페', emoji: '☕', color: '#A16207' },
      { name: '쇼핑', emoji: '🛍️', color: '#A855F7' },
      { name: '생활비', emoji: '🏠', color: '#3B82F6' },
      { name: '병원비', emoji: '🏥', color: '#EF4444' },
      { name: '육아비', emoji: '👶', color: '#EC4899' },
      { name: '약속', emoji: '👥', color: '#EAB308' },
      { name: '여행비', emoji: '✈️', color: '#06B6D4' },
      { name: '차량유지비', emoji: '🚗', color: '#64748B' },
      { name: '관리비', emoji: '🏢', color: '#14B8A6' },
      { name: '경조사비', emoji: '💐', color: '#F43F5E' },
      { name: '교통비', emoji: '🚌', color: '#6366F1' },
      { name: '자기계발비', emoji: '📚', color: '#8B5CF6' },
      { name: '건강식품', emoji: '💊', color: '#84CC16' },
      { name: '기타', emoji: '📦', color: '#9CA3AF' }
    ],
    paymentMethods: [
      { name: '현대카드_상민', emoji: '🔴' },
      { name: '현대카드_시리', emoji: '🟠' },
      { name: '국민카드', emoji: '🟡' },
      { name: '쿠팡와우카드', emoji: '🟣' },
      { name: '삼성카드', emoji: '🔵' },
      { name: '국민행복카드', emoji: '🟢' },
      { name: '계좌이체', emoji: '🏦' },
      { name: '현금', emoji: '💵' }
    ],
    budgets: {
      '식비': 400000,
      '외식': 300000,
      '생활비': 300000,
      '카페': 0,
      '쇼핑': 0,
      '병원비': 0,
      '육아비': 0,
      '약속': 0,
      '여행비': 0,
      '차량유지비': 0,
      '관리비': 0,
      '경조사비': 0,
      '교통비': 0
    },
    incomeCategories: [
      { name: '월급', emoji: '💰', amount: 0 },
      { name: '디센터', emoji: '🏢', amount: 0 },
      { name: '부수입', emoji: '🏠', amount: 0 }
    ],
    recurringIncomes: []
  };
}
