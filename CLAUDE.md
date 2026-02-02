# CLAUDE.md - smss-accountbook

## 프로젝트 개요
SMSS 가계부 - GitHub Pages로 호스팅되는 웹 기반 가계부 앱

## 배포 규칙
**중요: 모든 작업 완료 후 반드시 커밋 & 푸시**
- 코드 변경이 완료되면 즉시 `git add`, `git commit`, `git push` 실행
- GitHub Pages로 자동 배포됨: https://byuncoding.github.io/smss-accountbook/

## 기술 스택
- 단일 HTML 파일 (index.html)
- Vanilla JavaScript
- Chart.js (차트)
- Remixicon (아이콘)
- Google Apps Script (백엔드 API)
- Google Sheets (데이터 저장소)

## 주요 구조
- 데이터: `data/*.json` (과거 데이터) + Google Sheets (실시간)
- 캐시: localStorage (1분 만료)
- API: APPS_SCRIPT_URL로 저장/삭제 요청

## 코드 컨벤션
- 한글 주석 사용
- 함수명: camelCase
- CSS 변수: `--primary`, `--income`, `--expense` 등
