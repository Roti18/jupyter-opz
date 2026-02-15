@echo off
setlocal
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

echo [4/6] Initializing Project...
if not exist Pendat (
    jupyter-book create Pendat
)

echo Building Jupyter Book...
jupyter-book build Pendat/

echo [5/6] Moving contents to Root...
xcopy /E /H /Y Pendat .

echo [6/6] Cleaning up Pendat folder...
rmdir /S /Q Pendat

:: Create .nojekyll in root
echo. > .nojekyll

echo [8/8] Cleaning up sample files...
del /F /Q markdown.md markdown-notebooks.md notebooks.ipynb 2>nul

echo [7/7] Finishing Installation...

:: Project Identity Setup
echo ------------------------------------------
set /p AUTHOR_NAME="Enter Author Name (Default: Roti18): "
if "%AUTHOR_NAME%"=="" set AUTHOR_NAME=Roti18

set /p REPO_URL="Enter GitHub Repository URL (e.g. https://github.com/roti18/jupyter-opz): "
if "%REPO_URL%"=="" (
    for %%I in (.) do set REPO_NAME=%%~nxI
    set REPO_URL=https://github.com/Roti18/%REPO_NAME%
)

:: Get Current Year
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set dt=%%i
set CURRENT_YEAR=%dt:~0,4%

:: Update _config.yml
if exist _config.yml (
    powershell -Command "$c = Get-Content _config.yml; $c = $c -replace '^author: .*', 'author: \"%AUTHOR_NAME%\"'; $c = $c -replace '^  url: .*', '  url: %REPO_URL%'; $c = $c -replace '^  branch: .*', '  branch: main'; if ($c -match '^copyright:') { $c = $c -replace '^copyright: .*', 'copyright: \"%CURRENT_YEAR%\"' } else { $c = $c -replace '^author: .*', \"author: `\"%AUTHOR_NAME%`\"`ncopyright: `\"%CURRENT_YEAR%`\"\" }; Set-Content _config.yml $c"
)
echo [SUCCESS] Identity updated: %AUTHOR_NAME% ^| %CURRENT_YEAR%
echo [SUCCESS] Repository set to: %REPO_URL%

call scripts\publish.bat

echo ==========================================
echo    Process Finished ^& Published!
echo    Venv: Active
echo    Run 'run.bat dev' to start Canvas.
echo ==========================================
pause