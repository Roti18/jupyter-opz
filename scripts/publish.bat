@echo off
setlocal
echo ==========================================
echo    Deploying Jupyter Book to /docs
echo ==========================================

:: Activate venv
if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo [ERROR] venv not found. Run run.bat install first.
    pause
    exit /b 1
)

echo [1/4] Auto-Generating Table of Contents (_toc.yml)...
if exist intro.md del /F /Q intro.md
powershell -Command "$ignore = @('README.md', 'requirements.txt', '.nojekyll', 'markdown.md', 'markdown-notebooks.md', 'notebooks.ipynb'); $files = Get-ChildItem -Path . -Include *.md, *.ipynb -Recurse -Depth 1 | Where-Object { $_.Name -notin $ignore -and $_.FullName -notmatch 'venv|_build|docs|scripts' }; $numbered = $files | Where-Object { $_.Name -match '^\d+' } | Sort-Object Name; $nonNumbered = $files | Where-Object { $_.Name -notmatch '^\d+' } | Sort-Object Name; $finalList = $numbered + $nonNumbered; $toc = 'format: jb-book' + \"`n\" + 'root: md/intro' + \"`n\" + 'chapters:'; foreach ($f in $finalList) { $relPath = (Resolve-Path -Path $f.FullName -Relative) -replace '^\.\\', '' -replace '\.(md|ipynb)$', '' -replace '\\', '/'; if ($relPath -eq 'md/intro' -or $relPath -eq 'intro') { continue }; $content = Get-Content $f.FullName -TotalCount 20; $h1 = $content | Where-Object { $_ -match '^#\s+(.+)' } | Select-Object -First 1; if ($h1) { $title = ($h1 -replace '^#\s+', '').Trim() } else { $title = ($f.BaseName -replace '^\d+[_-]', '' -replace '[-_]', ' ').Trim() }; $toc += \"`n\" + '- file: ' + $relPath + \"`n\" + '  title: \"' + $title + '\"' }; $toc | Out-File -FilePath _toc.yml -Encoding ASCII"

echo [2/4] Building Jupyter Book...
jupyter-book build .

echo [3/4] Preparing /docs folder...
if exist docs rmdir /S /Q docs
mkdir docs

echo [4/4] Copying build files to /docs...
xcopy /E /H /Y _build\html docs\
echo. > docs\.nojekyll
if exist scripts\canvas-restricted.html copy scripts\canvas-restricted.html docs\canvas.html

echo ==========================================
echo    Done! Sidebar ^& Titles automated.
echo ==========================================
pause
goto :eof