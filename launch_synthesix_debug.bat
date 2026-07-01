@echo off
REM Lanceur Synthesix en mode debug (logs detailles).
REM Affiche les logs a l'ecran ET les enregistre dans synthesix_debug.log.
cd /d "%~dp0"

set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

echo [Synthesix DEBUG] Demarrage avec logs detailles...
echo [Synthesix DEBUG] Les logs sont aussi enregistres dans : "%~dp0synthesix_debug.log"
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%PY%' -u main.py --verbose 2>&1 | Tee-Object -FilePath 'synthesix_debug.log'"

echo.
echo [Synthesix DEBUG] Application arretee. Envoyez synthesix_debug.log si besoin.
pause
