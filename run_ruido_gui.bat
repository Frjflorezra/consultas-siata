@echo off
setlocal enabledelayedexpansion

REM --- Paths ---
set "BASE_DIR=%~dp0ruido_cli"
set "VENV_DIR=%BASE_DIR%\.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "REQ_FILE=%BASE_DIR%\requirements.txt"
set "GUI_FILE=%BASE_DIR%\gui.py"
set "DATA_DIR=%BASE_DIR%\data"

REM --- Go to project dir ---
cd /d "%BASE_DIR%" || (echo [ERROR] Cannot cd into "%BASE_DIR%" & goto :end)

REM --- Crear carpeta data (y .gitkeep opcional) ---
if not exist "%DATA_DIR%" (
  mkdir "%DATA_DIR%"
)
if not exist "%KEEP_FILE%" (
  type nul > "%KEEP_FILE%"
)

REM --- Ensure requirements.txt exists ---
if not exist "%REQ_FILE%" (
  echo [ERROR] requirements.txt not found at:
  echo        "%REQ_FILE%"
  goto :end
)

REM --- Create venv if missing ---
if not exist "%VENV_PY%" (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 -m venv "%VENV_DIR%"
  ) else (
    python -m venv "%VENV_DIR%"
  )
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    goto :end
  )
)

REM --- Upgrade packaging tools (quiet) ---
"%VENV_PY%" -m pip install --upgrade pip setuptools wheel >nul
if errorlevel 1 (
  echo [WARN] Could not upgrade pip/setuptools/wheel. Continuing...
)

REM --- ALWAYS install dependencies ---
echo Installing dependencies from requirements.txt...
"%VENV_PY%" -m pip install -r "%REQ_FILE%"
if errorlevel 1 (
  echo [ERROR] Dependency installation failed.
  goto :end
)

REM --- Launch app ---
echo Iniciando interfaz... (cierra esta ventana para terminar)
"%VENV_PY%" "%GUI_FILE%"
goto :end

:end
endlocal

