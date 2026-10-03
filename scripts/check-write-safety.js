#!/usr/bin/env node
// ★ 한 번 입력 = 시트에 정확히 한 번 — index.html 쓰기 경로 안전 검사
// Claude Code PostToolUse 훅이 index.html 수정 후 자동 실행한다 (.claude/settings.json).
// 수동 실행: node scripts/check-write-safety.js
// 실패하면 exit 2 + stderr 로 이유를 알린다.
//
// 검사 내용
//  1) 시트 쓰기(fetch APPS_SCRIPT_URL)는 전송 큐 안 한 곳에서만
//  2) 쓰기 요청에 rid(고유번호)를 붙인다
//  3) 실제 큐 코드를 가짜 시트/Apps Script로 돌려 중복·유실이 없는지
//     (응답 유실, 저장 직후 앱 종료, 오프라인, 의도적 반복 입력)
const fs = require('fs'), vm = require('vm'), path = require('path');

// 훅 입력(JSON)에서 바뀐 파일을 확인 — index.html이 아니면 검사하지 않는다
let stdin = '';
try { if (!process.stdin.isTTY) stdin = fs.readFileSync(0, 'utf8'); } catch (e) {}
try {
    const p = JSON.parse(stdin || '{}');
    const f = (p.tool_input && p.tool_input.file_path) || (p.tool_response && p.tool_response.filePath) || '';
    if (f && !/index\.html$/i.test(f)) process.exit(0);
} catch (e) {}

const fail = msg => {
    console.error(`[쓰기 안전 검사 실패] ${msg}\n→ CLAUDE.md "한 번 입력 = 한 번 기록" 규칙을 확인하세요.`);
    process.exit(2);
};

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

// ---- 1) 정적 검사 ----
const writeFetches = html.match(/fetch\(`\$\{APPS_SCRIPT_URL\}/g) || [];
if (writeFetches.length !== 1) {
    fail(`APPS_SCRIPT_URL로 직접 fetch 하는 곳이 ${writeFetches.length}곳. 시트 쓰기는 enqueueApi → 전송 큐 한 곳에서만 해야 한다.`);
}
if (!/rid:\s*item\.id/.test(html)) fail('쓰기 요청에 rid(고유번호)가 빠졌다. 재전송 시 중복 기록된다.');
if (!/function countSheetMatches/.test(html)) fail('countSheetMatches(보내기 전/후 시트 확인)가 없다.');

// ---- 2) 실제 큐 코드로 시나리오 검증 ----
const start = html.indexOf('const OUTBOX_KEY');
const end = html.indexOf('// 온라인 복귀 / 탭 복귀 시 이어서 전송');
if (start < 0 || end < 0) fail('전송 큐 코드 블록을 찾지 못했다 (OUTBOX_KEY ~ 온라인 복귀 주석).');
const block = html.slice(start, end);
const csvFn = (html.match(/function parseCSVLine\([\s\S]*?\n        \}/) || [])[0];
if (!csvFn) fail('parseCSVLine 함수를 찾지 못했다.');

function makeEnv({ idemServer }) {
    const sheet = [];   // [date, category, item, amount, '', person]
    const seen = new Set();
    const store = {};
    const env = { sheet, mode: 'ok' };   // ok | lostResponse | networkDown | closeAfterSend
    const ctx = {
        console: { log() {}, warn() {} },
        setTimeout: (f, ms) => setTimeout(f, Math.min(ms, 5)), clearTimeout,
        URLSearchParams, Promise, JSON, Math, Date, Number, String, Set, Object, Array,
        localStorage: { getItem: k => store[k] ?? null, setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } },
        navigator: { onLine: true },
        document: { getElementById: () => null },
        GOOGLE_SHEETS: { '2026-09': 1 }, SHEET_ID: 'X',
        APPS_SCRIPT_URL: 'https://script.google.com/exec',
        loadSheetList: async () => {},
        fetch: async (url) => {
            if (env.mode === 'networkDown') throw new TypeError('down');
            if (url.includes('gviz')) {
                const csv = sheet.map(r => r.map(c => `"${c}"`).join(',')).join('\n');
                return { ok: true, text: async () => csv };
            }
            const p = Object.fromEntries(new URL(url).searchParams);
            const dup = idemServer && seen.has(p.rid);
            if (!dup) {
                if (p.action === 'add') sheet.push([p.date, p.category, p.item, p.amount, '', p.person]);
                seen.add(p.rid);
            }
            if (env.mode === 'lostResponse') throw new TypeError('response lost');                 // 기록은 됐는데 응답 실패
            if (env.mode === 'closeAfterSend') { env.mode = 'ok'; return new Promise(() => {}); } // 응답 전에 앱 종료
            return { ok: true, json: async () => ({ success: true, idem: idemServer || undefined, duplicate: dup }) };
        },
    };
    vm.createContext(ctx);
    vm.runInContext(csvFn + '\n' + block +
        ';globalThis.enqueueApi=enqueueApi;globalThis.flushOutbox=flushOutbox;globalThis.getOutbox=getOutbox;' +
        'globalThis.drainAgain=(typeof _drainOutboxLocked==="function"?_drainOutboxLocked:_drainOutbox);', ctx);
    env.ctx = ctx;
    return env;
}

const P = { action: 'add', year: '2026', date: '2026-09-17', category: '외식', item: '쿠팡이츠_', person: '쿠팡와우카드', amount: '12500' };
const wait = ms => new Promise(r => setTimeout(r, ms));
const results = [];
const check = (name, cond, extra) => results.push(`${cond ? '✅' : '❌'} ${name} ${extra || ''}`);

(async () => {
    for (const idemServer of [false, true]) {
        const tag = idemServer ? '[서버 수정 후]' : '[서버 수정 전]';

        let e = makeEnv({ idemServer });
        e.ctx.enqueueApi(P); await e.ctx.flushOutbox(); await wait(30);
        check(`${tag} 정상 저장 → 1행`, e.sheet.length === 1 && e.ctx.getOutbox().length === 0, `rows=${e.sheet.length}`);

        e = makeEnv({ idemServer }); e.mode = 'lostResponse';
        e.ctx.enqueueApi(P); await e.ctx.flushOutbox(); await wait(30);
        e.mode = 'ok'; await e.ctx.flushOutbox(); await wait(30); await e.ctx.flushOutbox(); await wait(30);
        check(`${tag} 응답 실패 후 재시도 → 1행`, e.sheet.length === 1 && e.ctx.getOutbox().length === 0, `rows=${e.sheet.length}`);

        e = makeEnv({ idemServer }); e.mode = 'closeAfterSend';
        e.ctx.enqueueApi(P); await wait(30);
        await e.ctx.drainAgain(); await wait(30);   // 앱 재실행
        check(`${tag} 저장 직후 앱 종료 → 재실행 → 1행`, e.sheet.length === 1 && e.ctx.getOutbox().length === 0, `rows=${e.sheet.length}`);

        e = makeEnv({ idemServer }); e.mode = 'networkDown';
        e.ctx.enqueueApi(P); await e.ctx.flushOutbox(); await wait(30);
        const offline = e.sheet.length, queued = e.ctx.getOutbox().length;
        e.mode = 'ok'; await e.ctx.flushOutbox(); await wait(30);
        check(`${tag} 오프라인 입력 → 복귀 후 1행 (유실 없음)`, offline === 0 && queued === 1 && e.sheet.length === 1, `after=${e.sheet.length}`);

        e = makeEnv({ idemServer });
        e.ctx.enqueueApi(P); e.ctx.enqueueApi(P); await e.ctx.flushOutbox(); await wait(30); await e.ctx.flushOutbox(); await wait(30);
        check(`${tag} 의도적으로 2번 입력 → 2행`, e.sheet.length === 2, `rows=${e.sheet.length}`);
    }
    const bad = results.filter(r => r.startsWith('❌'));
    if (bad.length) fail('중복/유실 시나리오 실패:\n' + bad.join('\n'));
    if (!stdin) console.log(results.join('\n'));
    process.exit(0);
})();
