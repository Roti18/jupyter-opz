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

echo [1/4] Cleaning & Generating Table of Contents (_toc.yml)...
if exist _build rmdir /S /Q _build
if exist docs rmdir /S /Q docs

powershell -Command "$ignore = @('README.md', 'requirements.txt', '.nojekyll', 'markdown.md', 'markdown-notebooks.md', 'notebooks.ipynb'); $files = Get-ChildItem -Path . -Recurse -Depth 1 | Where-Object { ($PSItem.Extension -eq '.md' -or $PSItem.Extension -eq '.ipynb') -and $PSItem.Name -notin $ignore -and $PSItem.FullName -notmatch 'venv|_build|docs|scripts' }; $finalList = @(); foreach ($f in $files) { $relPath = (Resolve-Path -Path $f.FullName -Relative) -replace '^\.\\', '' -replace '\.(md|ipynb)$', '' -replace '\\', '/'; if ($relPath -eq 'intro') { continue }; $finalList += $f }; $sortedList = $finalList | Sort-Object Name; $toc = 'format: jb-book' + [char]10 + 'root: intro'; if ($sortedList.Count -gt 0) { $toc += [char]10 + 'chapters:'; foreach ($f in $sortedList) { $relPath = (Resolve-Path -Path $f.FullName -Relative) -replace '^\.\\', '' -replace '\.(md|ipynb)$', '' -replace '\\', '/'; $content = Get-Content $f.FullName -TotalCount 20; $h1 = $content | Where-Object { $PSItem -match '^#\s+' } | Select-Object -First 1; if ($h1) { $title = $h1 -replace '^#\s+','' } else { $title = ($f.BaseName -replace '^\d+[_-]', '' -replace '[-_]', ' ') }; $toc += [char]10 + '- file: ' + $relPath + [char]10 + '  title: \"' + $title.Trim() + '\"' } }; $toc | Out-File -FilePath _toc.yml -Encoding UTF8"

echo [2/4] Building Jupyter Book...
call .\venv\Scripts\jupyter-book build --all .

echo [3/4] Preparing /docs folder...
mkdir docs

echo [4/4] Copying build files to /docs...
xcopy /E /H /Y _build\html docs\
echo. > docs\.nojekyll
if exist scripts\canvas-restricted.html copy /Y scripts\canvas-restricted.html docs\canvas.html

echo ==========================================
echo    Done! Sidebar ^& Titles automated.
echo ==========================================
pause
goto :eof