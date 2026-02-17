@echo off
setlocal enabledelayedexpansion
echo ==========================================
echo    Installing Jupyter Book 1.0.3 (VENV)
echo ==========================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python first.
    pause
    exit /b 1
)

echo [1/6] Creating Virtual Environment (venv)...
python -m venv venv

echo [2/6] Activating Virtual Environment...
call venv\Scripts\activate

echo [3/6] Installing Requirements...
python -m pip install --upgrade pip
pip install -r scripts\requirements.txt

if not exist Pendat (
    if not exist _config.yml (
        jupyter-book create Pendat
    )
)

echo Building Jupyter Book...
jupyter-book build Pendat/

echo [5/6] Moving contents to Root...
if exist Pendat (
    xcopy /E /H /Y Pendat .
)

echo [6/7] Cleaning up sample files...
if exist Pendat rmdir /S /Q Pendat
if exist .nojekyll del .nojekyll
echo. > .nojekyll
:: Only delete defaults if there is a Pendat folder (fresh install)
if exist Pendat (
    del /F /Q markdown.md markdown-notebooks.md notebooks.ipynb 2>nul
)
if exist _build\html\markdown.html del /F /Q _build\html\markdown.html
if exist _build\html\markdown-notebooks.html del /F /Q _build\html\markdown-notebooks.html
if exist _build\html\notebooks.html del /F /Q _build\html\notebooks.html
if exist docs\markdown.html del /F /Q docs\markdown.html
if exist docs\markdown-notebooks.html del /F /Q docs\markdown-notebooks.html
if exist docs\notebooks.html del /F /Q docs\notebooks.html

echo [7/7] Project Identity Setup...
echo ------------------------------------------
set /p AUTHOR_NAME="Enter Author Name (Default: Roti18): "
if "%AUTHOR_NAME%"=="" set AUTHOR_NAME=Roti18

set /p REPO_URL="Enter GitHub Repository URL (e.g. https://github.com/roti18/jupyter-opz): "
if "!REPO_URL!"=="" (
    for %%I in (.) do set REPO_NAME=%%~nxI
    set REPO_URL=https://github.com/Roti18/!REPO_NAME!
)

:: Get Current Year
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set dt=%%i
set CURRENT_YEAR=%dt:~0,4%

if exist _config.yml (
    powershell -Command "$c = Get-Content _config.yml -Raw; $c = $c -replace '(?m)^author: .*', 'author: \"%AUTHOR_NAME%\"'; $c = $c -replace '(?m)^  url: .*', '  url: !REPO_URL!'; $c = $c -replace '(?m)^  branch: .*', '  branch: main'; if ($c -match '(?m)^copyright:') { $c = $c -replace '(?m)^copyright: .*', 'copyright: \"%CURRENT_YEAR%\"' } else { $c = $c -replace '(?m)^author: .*', \"author: `\"%AUTHOR_NAME%`\"`ncopyright: `\"%CURRENT_YEAR%`\"\" }; if ($c -notmatch 'exclude_patterns:') { $c += \"`n`n# Pattern to exclude from the build`nexclude_patterns: [`\"_build`\", `\"docs`\", `\"venv`\", `\"scripts`\", `\"run.bat`\", `\"run.sh`\", `\"README.md`\"]\" }; Set-Content _config.yml $c -NoNewline"
)
echo [SUCCESS] Identity updated: %AUTHOR_NAME% ^| %CURRENT_YEAR%
echo [SUCCESS] Repository set to: !REPO_URL!

call scripts\publish.bat

echo ==========================================
echo    Process Finished ^& Published!
echo    Venv: Active
echo    Run 'run.bat dev' to start Canvas.
echo ==========================================
pause