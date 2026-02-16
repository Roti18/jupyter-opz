@echo off
setlocal enabledelayedexpansion
echo ==========================================
echo    Update Project Identity ^& Repository
echo ==========================================

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

:: Update _config.yml
if exist _config.yml (
    powershell -Command "$c = Get-Content _config.yml; $c = $c -replace '^author: .*', 'author: \"%AUTHOR_NAME%\"'; $c = $c -replace '^  url: .*', '  url: !REPO_URL!'; $c = $c -replace '^  branch: .*', '  branch: main'; if ($c -match '^copyright:') { $c = $c -replace '^copyright: .*', 'copyright: \"%CURRENT_YEAR%\"' } else { $c = $c -replace '^author: .*', \"author: `\"%AUTHOR_NAME%`\"`ncopyright: `\"%CURRENT_YEAR%`\"\" }; Set-Content _config.yml $c"
    echo [SUCCESS] _config.yml updated.
) else (
    echo [ERROR] _config.yml not found!
    pause
    exit /b 1
)

echo ------------------------------------------
echo Identity: %AUTHOR_NAME% ^| %CURRENT_YEAR%
echo Repo URL: !REPO_URL!
echo ------------------------------------------

set /p BUILD_NOW="Build ^& Publish now? (y/n): "
if /i "%BUILD_NOW%"=="y" (
    call scripts\publish.bat
)

echo Done.
pause
