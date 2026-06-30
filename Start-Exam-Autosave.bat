@echo off
REM Windows launcher -- double-click this file to start exam autosave.
REM Keep the window it opens OPEN for the whole exam.

REM Move to the folder that contains this launcher (the exam repo root).
cd /d "%~dp0"

echo Starting exam autosave...

where python >nul 2>&1
if %errorlevel%==0 (
    python .automations\autosave.py
    goto done
)

where py >nul 2>&1
if %errorlevel%==0 (
    py .automations\autosave.py
    goto done
)

echo.
echo ERROR: Python is not installed or not on your PATH.
echo Install Python 3, then double-click this file again.

:done
echo.
pause
