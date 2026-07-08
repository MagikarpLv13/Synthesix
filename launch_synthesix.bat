@echo off
REM Lanceur Synthesix : se place dans le dossier du script puis lance l'app
REM via le venv local. Garde la fenetre ouverte si une erreur survient.
cd /d "%~dp0"

set "SYNTHESIX_BROWSER=brave"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    echo [Synthesix] .venv introuvable, tentative avec le python du systeme...
    python main.py
)

if errorlevel 1 (
    echo.
    echo [Synthesix] L'application s'est arretee avec une erreur.
    pause
)
