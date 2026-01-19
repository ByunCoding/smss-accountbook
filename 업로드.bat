@echo off
chcp 65001 > nul
echo ========================================
echo   SMSS 가계부 - GitHub 업로드
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 변경사항 확인 중...
git status --short

echo.
echo [2/4] 파일 추가 중...
git add .

echo.
echo [3/4] 커밋 생성 중...
set /p msg="커밋 메시지 (Enter = 데이터 업데이트): "
if "%msg%"=="" set msg=데이터 업데이트

git commit -m "%msg%"

echo.
echo [4/4] GitHub에 푸시 중...
git push

echo.
echo ========================================
echo   완료! 웹사이트가 곧 업데이트됩니다.
echo   https://byuncoding.github.io/smss-accountbook/
echo ========================================
echo.
pause
