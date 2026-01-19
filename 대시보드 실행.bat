@echo off
chcp 65001 > nul
echo ========================================
echo SMSS 가계부 대시보드
echo ========================================
echo.
cd /d "%~dp0"

echo Flask 설치 확인 중...
pip install flask flask-cors -q

echo.
echo 서버를 시작합니다...
echo 브라우저에서 http://localhost:5000 으로 접속하세요.
echo 종료하려면 이 창을 닫거나 Ctrl+C를 누르세요.
echo ========================================
echo.

python server.py
pause
