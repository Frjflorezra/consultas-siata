@echo off
setlocal
cd /d "%~dp0ruido_cli"

set VENV_DIR=.venv
set VENV_PY=%VENV_DIR%\Scripts\python.exe

if not exist "%VENV_PY%" (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 -m venv %VENV_DIR%
  ) else (
    python -m venv %VENV_DIR%
  )
  "%VENV_PY%" -m pip install --upgrade pip >nul
  "%VENV_PY%" -m pip install -r requirements.txt || goto :end
)

echo Iniciando interfaz... (cierra esta ventana para terminar)
"%VENV_PY%" gui.py

:end
endlocal

