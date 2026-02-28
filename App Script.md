function doGet(e) {
  var action = e.parameter.action;

  if (action === 'getSheetList') {
    var r1 = getSheetList();
    return ContentService.createTextOutput(JSON.stringify({success: true, sheets: r1.sheets, incomeSheetGid: r1.incomeSheetGid})).setMimeType(ContentService.MimeType.JSON);
  }
  if (action === 'add') {
    var r2 = addExpense(e.parameter.date, e.parameter.category, e.parameter.item, e.parameter.person, e.parameter.amount, e.parameter.year);
    return ContentService.createTextOutput(JSON.stringify(r2)).setMimeType(ContentService.MimeType.JSON);
  }
  if (action === 'delete') {
    var r3 = deleteExpense(e.parameter.date, e.parameter.category, e.parameter.item, e.parameter.person, e.parameter.amount);
    return ContentService.createTextOutput(JSON.stringify(r3)).setMimeType(ContentService.MimeType.JSON);
  }
  if (action === 'addIncome') {
    var r4 = addIncome(e.parameter.date, e.parameter.category, e.parameter.item, e.parameter.amount, e.parameter.year);
    return ContentService.createTextOutput(JSON.stringify(r4)).setMimeType(ContentService.MimeType.JSON);
  }
  if (action === 'deleteIncome') {
    var r5 = deleteIncome(e.parameter.date, e.parameter.category, e.parameter.item, e.parameter.amount);
    return ContentService.createTextOutput(JSON.stringify(r5)).setMimeType(ContentService.MimeType.JSON);
  }
  if (action === 'getSettings') {
    var r6 = getSettings();
    return ContentService.createTextOutput(JSON.stringify(r6)).setMimeType(ContentService.MimeType.JSON);
  }
  if (action === 'saveSettings') {
    var r7 = saveSettingsData(JSON.parse(e.parameter.settings));
    return ContentService.createTextOutput(JSON.stringify(r7)).setMimeType(ContentService.MimeType.JSON);
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
    var re = /^\d{2}\.\d{1,2}$/;
    if (re.test(name)) {
      var parts = name.split('.');
      var year = '20' + parts[0];
      var month = parts[1].length === 1 ? '0' + parts[1] : parts[1];
      sheetList.push({name: name, monthKey: year + '-' + month, gid: sheets[i].getSheetId()});
    }
    if (name === '\uC218\uC785') {
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

function findNextEmptyRowInColumn(sheet, col, startRow) {
  var colData = sheet.getRange(startRow, col, 200, 1).getValues();
  for (var i = 0; i < colData.length; i++) {
    if (colData[i][0] === '' || colData[i][0] === null) {
      return startRow + i;
    }
  }
  return startRow + colData.length;
}

function normalizeDate(dateValue) {
  if (dateValue instanceof Date) {
    var yyyy = dateValue.getFullYear();
    var mm = String(dateValue.getMonth() + 1);
    var dd = String(dateValue.getDate());
    if (mm.length === 1) { mm = '0' + mm; }
    if (dd.length === 1) { dd = '0' + dd; }
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
    if (!sheet) { return {success: false, error: 'Sheet not found'}; }
    var data = sheet.getDataRange().getValues();
    var targetAmount = Number(amount);
    for (var i = data.length - 1; i >= 1; i--) {
      var row = data[i];
      var rowDate = normalizeDate(row[0]);
      var rowAmount = Number(String(row[3]).replace(/[,]/g, ''));
      if (rowDate === date && row[1] === category && rowAmount === targetAmount) {
        sheet.deleteRow(i + 1);
        return {success: true, message: 'Deleted', row: i + 1};
      }
    }
    return {success: false, error: 'Not found'};
  } catch (error) {
    return {success: false, error: error.toString()};
  }
}

function addIncome(date, category, item, amount, year) {
  try {
    var ss = SpreadsheetApp.openById('1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk');
    var sheetName = getSheetNameFromDate(date, year);
    var sheet = getOrCreateSheet(ss, sheetName);
    var newRow = findNextEmptyRowInColumn(sheet, 8, 10);
    sheet.getRange(newRow, 8).setValue(date);
    sheet.getRange(newRow, 9).setValue(category);
    sheet.getRange(newRow, 10).setValue(item || '');
    sheet.getRange(newRow, 11).setValue(Number(amount));
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
    if (!sheet) { return {success: false, error: 'Sheet not found'}; }
    var lastRow = sheet.getLastRow();
    if (lastRow < 10) { return {success: false, error: 'Not found'}; }
    var data = sheet.getRange(10, 8, lastRow - 9, 4).getValues();
    var targetAmount = Number(amount);
    for (var i = data.length - 1; i >= 0; i--) {
      var row = data[i];
      var rowDate = normalizeDate(row[0]);
      var rowAmount = Number(String(row[3]).replace(/[,]/g, ''));
      if (rowDate === date && row[1] === category && rowAmount === targetAmount) {
        sheet.getRange(10 + i, 8, 1, 4).clearContent();
        return {success: true, message: 'Income deleted', row: 10 + i};
      }
    }
    return {success: false, error: 'Not found'};
  } catch (error) {
    return {success: false, error: error.toString()};
  }
}

function getSettings() {
  try {
    var ss = SpreadsheetApp.openById('1EuWNGb3fEpLEbZwocIk6afSmmjiSTo2-rAu5qqfFnbk');
    var sheet = ss.getSheetByName('SETTINGS');
    if (!sheet) { return {success: true, settings: getDefaultSettings()}; }
    var lastRow = sheet.getLastRow();
    if (lastRow <= 1) { return {success: true, settings: getDefaultSettings()}; }
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
      if (!name) { continue; }
      if (type === 'category') {
        categories.push({name: name, emoji: emoji || '', color: color || '#9CA3AF'});
      } else if (type === 'payment') {
        paymentMethods.push({name: name, emoji: emoji || ''});
      } else if (type === 'budget') {
        budgets[name] = Number(color) || 0;
      } else if (type === 'income') {
        incomeCategories.push({name: name, emoji: emoji || '', amount: Number(color) || 0});
      } else if (type === 'recurring') {
        try {
          var meta = JSON.parse(emoji);
          recurringIncomes.push({id: meta.id, category: name, amount: Number(color) || 0, description: meta.description || '', dayOfMonth: meta.dayOfMonth || 1, createdMonths: meta.createdMonths || []});
        } catch (ex) {}
      }
    }
    if (categories.length === 0 && paymentMethods.length === 0) {
      return {success: true, settings: getDefaultSettings()};
    }
    var result = {categories: categories, paymentMethods: paymentMethods};
    if (Object.keys(budgets).length > 0) { result.budgets = budgets; }
    if (incomeCategories.length > 0) { result.incomeCategories = incomeCategories; }
    result.recurringIncomes = recurringIncomes;
    return {success: true, settings: result};
  } catch (error) {
    return {success: false, error: error.toString()};
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
    if (lastRow > 1) { sheet.deleteRows(2, lastRow - 1); }
    var rows = [];
    for (var i = 0; i < settings.categories.length; i++) {
      var cat = settings.categories[i];
      rows.push(['category', cat.name, cat.emoji, cat.color]);
    }
    for (var j = 0; j < settings.paymentMethods.length; j++) {
      var pm = settings.paymentMethods[j];
      rows.push(['payment', pm.name, pm.emoji, '']);
    }
    if (settings.budgets) {
      var budgetKeys = Object.keys(settings.budgets);
      for (var k = 0; k < budgetKeys.length; k++) {
        rows.push(['budget', budgetKeys[k], '', settings.budgets[budgetKeys[k]]]);
      }
    }
    if (settings.incomeCategories) {
      for (var m = 0; m < settings.incomeCategories.length; m++) {
        var ic = settings.incomeCategories[m];
        rows.push(['income', ic.name, ic.emoji, ic.amount || 0]);
      }
    }
    if (settings.recurringIncomes) {
      for (var r = 0; r < settings.recurringIncomes.length; r++) {
        var ri = settings.recurringIncomes[r];
        var meta = JSON.stringify({id: ri.id, description: ri.description || '', dayOfMonth: ri.dayOfMonth || 1, createdMonths: ri.createdMonths || []});
        rows.push(['recurring', ri.category, meta, ri.amount || 0]);
      }
    }
    if (rows.length > 0) { sheet.getRange(2, 1, rows.length, 4).setValues(rows); }
    return {success: true};
  } catch (error) {
    return {success: false, error: error.toString()};
  }
}

function getDefaultSettings() {
  return {
    categories: [
      {name: '\uC678\uC2DD', emoji: '\uD83C\uDF7D\uFE0F', color: '#F97316'},
      {name: '\uC2DD\uBE44', emoji: '\uD83D\uDED2', color: '#22C55E'},
      {name: '\uCE74\uD398', emoji: '\u2615', color: '#A16207'},
      {name: '\uC1FC\uD551', emoji: '\uD83D\uDECD\uFE0F', color: '#A855F7'},
      {name: '\uC0DD\uD65C\uBE44', emoji: '\uD83C\uDFE0', color: '#3B82F6'},
      {name: '\uBCD1\uC6D0\uBE44', emoji: '\uD83C\uDFE5', color: '#EF4444'},
      {name: '\uC721\uC544\uBE44', emoji: '\uD83D\uDC76', color: '#EC4899'},
      {name: '\uC57D\uC18D', emoji: '\uD83D\uDC65', color: '#EAB308'},
      {name: '\uC5EC\uD589\uBE44', emoji: '\u2708\uFE0F', color: '#06B6D4'},
      {name: '\uCC28\uB7C9\uC720\uC9C0\uBE44', emoji: '\uD83D\uDE97', color: '#64748B'},
      {name: '\uAD00\uB9AC\uBE44', emoji: '\uD83C\uDFE2', color: '#14B8A6'},
      {name: '\uACBD\uC870\uC0AC\uBE44', emoji: '\uD83D\uDC90', color: '#F43F5E'},
      {name: '\uAD50\uD1B5\uBE44', emoji: '\uD83D\uDE8C', color: '#6366F1'},
      {name: '\uC790\uAE30\uACC4\uBC1C\uBE44', emoji: '\uD83D\uDCDA', color: '#8B5CF6'},
      {name: '\uAC74\uAC15\uC2DD\uD488', emoji: '\uD83D\uDC8A', color: '#84CC16'},
      {name: '\uAE30\uD0C0', emoji: '\uD83D\uDCE6', color: '#9CA3AF'}
    ],
    paymentMethods: [
      {name: '\uD604\uB300\uCE74\uB4DC_\uC0C1\uBBFC', emoji: '\uD83D\uDD34'},
      {name: '\uD604\uB300\uCE74\uB4DC_\uC2DC\uB9AC', emoji: '\uD83D\uDFE0'},
      {name: '\uAD6D\uBBFC\uCE74\uB4DC', emoji: '\uD83D\uDFE1'},
      {name: '\uCFE0\uD321\uC640\uC6B0\uCE74\uB4DC', emoji: '\uD83D\uDFE3'},
      {name: '\uC0BC\uC131\uCE74\uB4DC', emoji: '\uD83D\uDD35'},
      {name: '\uAD6D\uBBFC\uD589\uBCF5\uCE74\uB4DC', emoji: '\uD83D\uDFE2'},
      {name: '\uACC4\uC88C\uC774\uCCB4', emoji: '\uD83C\uDFE6'},
      {name: '\uD604\uAE08', emoji: '\uD83D\uDCB5'}
    ],
    budgets: {
      '\uC2DD\uBE44': 400000,
      '\uC678\uC2DD': 300000,
      '\uC0DD\uD65C\uBE44': 300000,
      '\uCE74\uD398': 0,
      '\uC1FC\uD551': 0,
      '\uBCD1\uC6D0\uBE44': 0,
      '\uC721\uC544\uBE44': 0,
      '\uC57D\uC18D': 0,
      '\uC5EC\uD589\uBE44': 0,
      '\uCC28\uB7C9\uC720\uC9C0\uBE44': 0,
      '\uAD00\uB9AC\uBE44': 0,
      '\uACBD\uC870\uC0AC\uBE44': 0,
      '\uAD50\uD1B5\uBE44': 0
    },
    incomeCategories: [
      {name: '\uC6D4\uAE09', emoji: '\uD83D\uDCB0', amount: 0},
      {name: '\uB514\uC13C\uD130', emoji: '\uD83C\uDFE2', amount: 0},
      {name: '\uBD80\uC218\uC785', emoji: '\uD83C\uDFE0', amount: 0}
    ],
    recurringIncomes: []
  };
}
