<#
.SYNOPSIS
  FoodLAB Guidebook Creator (FG) Unified PowerShell CLI
.DESCRIPTION
  Builds Markdown documents from content/ into clean PDFs in build/ using
  an isolated LaTeX modular compiler in latex-formatter/.
#>

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [string]$Target = "all"
)

$RootDir = $PSScriptRoot
if (-not $RootDir) { $RootDir = (Get-Location).Path }
$BuildDir = Join-Path $RootDir "build"
$ContentDir = Join-Path $RootDir "content"
$FormatterDir = Join-Path $RootDir "latex-formatter"
$ScriptsDir = Join-Path $RootDir "scripts"

function Ensure-Directories {
    if (-not (Test-Path -LiteralPath $BuildDir)) {
        New-Item -ItemType Directory -Path $BuildDir | Out-Null
    }
    if (-not (Test-Path -LiteralPath $FormatterDir)) {
        New-Item -ItemType Directory -Path $FormatterDir | Out-Null
    }
    if (-not (Test-Path -LiteralPath $ContentDir)) {
        New-Item -ItemType Directory -Path $ContentDir | Out-Null
    }
}

function Clean-AuxFiles {
    Start-Sleep -Milliseconds 200

    # 1. Purge non-PDF files in build/
    if (Test-Path -LiteralPath $BuildDir) {
        Get-ChildItem -LiteralPath $BuildDir -File | Where-Object { $_.Extension -ne ".pdf" } | ForEach-Object {
            try { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue } catch {}
        }
    }

    # 2. Purge auxiliary compilation files in latex-formatter/
    if (Test-Path -LiteralPath $FormatterDir) {
        $AuxExtensions = @(".aux", ".log", ".toc", ".lof", ".lot", ".fls", ".fdb_latexmk", ".synctex.gz", ".out", ".bbl", ".blg", ".tmp")
        Get-ChildItem -LiteralPath $FormatterDir -File | Where-Object { $AuxExtensions -contains $_.Extension -or $_.Name.Contains(".synctex") } | ForEach-Object {
            try { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue } catch {}
        }
    }

    # 3. Clean accidental literal folders
    $AccidentalDirs = @(
        (Join-Path $RootDir "`$BuildDir"),
        (Join-Path $RootDir "`$BuilDir"),
        (Join-Path $RootDir "`$builddir")
    )
    foreach ($dir in $AccidentalDirs) {
        if (Test-Path -LiteralPath $dir) {
            Remove-Item -LiteralPath $dir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

function Clean-Cache {
    Write-Host "==> [CLEAN-CACHE] Purging generated LaTeX files (Preserving PDFs in build/)..." -ForegroundColor Yellow

    $ChaptersDir = Join-Path $FormatterDir "chapters"
    if (Test-Path -LiteralPath $ChaptersDir) {
        Get-ChildItem -LiteralPath $ChaptersDir -Directory | ForEach-Object {
            Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    $AppendicesDir = Join-Path $FormatterDir "appendices"
    if (Test-Path -LiteralPath $AppendicesDir) {
        Get-ChildItem -LiteralPath $AppendicesDir -Directory | ForEach-Object {
            Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    $ConfigDir = Join-Path $FormatterDir "config"
    if (Test-Path -LiteralPath $ConfigDir) {
        Get-ChildItem -LiteralPath $ConfigDir -Filter "metadata_*.tex" | ForEach-Object {
            Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue
        }
    }

    $FrontmatterDir = Join-Path $FormatterDir "frontmatter"
    if (Test-Path -LiteralPath $FrontmatterDir) {
        Get-ChildItem -LiteralPath $FrontmatterDir -Filter "kata_pengantar_*.tex" | ForEach-Object {
            Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue
        }
    }

    if (Test-Path -LiteralPath $FormatterDir) {
        Get-ChildItem -LiteralPath $FormatterDir -Filter "*.tex" | ForEach-Object {
            Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue
        }
    }

    Clean-AuxFiles
    Write-Host "==> [DONE] Cache cleaned. All PDF deliverables remain safe in build/." -ForegroundColor Green
}

function Show-AvailableDocuments {
    if (-not (Test-Path -LiteralPath $ContentDir)) { return }
    $Mds = Get-ChildItem -LiteralPath $ContentDir -Filter "*.md"
    if ($Mds.Count -gt 0) {
        Write-Host "Available documents in content/:" -ForegroundColor Gray
        foreach ($m in $Mds) {
            $isTmpl = Is-TemplateFile $m.Name
            $tag = if ($isTmpl) { " (template, excluded from 'all')" } else { "" }
            Write-Host "  - $($m.BaseName)$tag" -ForegroundColor Cyan
        }
    } else {
        Write-Host "No documents found in content/ directory." -ForegroundColor Yellow
    }
}

function Is-TemplateFile([string]$FileName) {
    if ($FileName -like "template-*" -or $FileName -like "template_*" -or $FileName -like "_*") {
        return $true
    }
    $FullPath = Join-Path $ContentDir $FileName
    if (Test-Path -LiteralPath $FullPath) {
        # Check first 25 lines for template tag
        $HeaderLines = Get-Content -LiteralPath $FullPath -TotalCount 25 -ErrorAction SilentlyContinue
        foreach ($line in $HeaderLines) {
            if ($line -match '^\s*template\s*:\s*("true"|true|1|yes)\s*$') {
                return $true
            }
        }
    }
    return $false
}

function Resolve-Python {
    if (Get-Command python -ErrorAction SilentlyContinue) { return "python" }
    if (Get-Command py -ErrorAction SilentlyContinue) { return "py" }
    if (Get-Command python3 -ErrorAction SilentlyContinue) { return "python3" }
    return $null
}

function Resolve-TexEnvironment {
    $hasPerl = (Get-Command perl -ErrorAction SilentlyContinue) -ne $null

    if ($hasPerl -and (Get-Command latexmk -ErrorAction SilentlyContinue)) { return "latexmk" }
    if (Get-Command pdflatex -ErrorAction SilentlyContinue) { return "pdflatex" }

    $CandidatePaths = @(
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64",
        "C:\Program Files\MiKTeX\miktex\bin\x64",
        "C:\Program Files (x86)\MiKTeX\miktex\bin",
        "$env:APPDATA\TinyTeX\bin\windows",
        "C:\texlive\2026\bin\windows",
        "C:\texlive\2025\bin\windows",
        "C:\texlive\2024\bin\windows",
        "C:\texlive\2023\bin\windows",
        "C:\texlive\2022\bin\windows"
    )

    foreach ($p in $CandidatePaths) {
        if (Test-Path -LiteralPath $p) {
            $env:PATH = "$p;$env:PATH"
            if ($hasPerl -and (Get-Command latexmk -ErrorAction SilentlyContinue)) { return "latexmk" }
            if (Get-Command pdflatex -ErrorAction SilentlyContinue) { return "pdflatex" }
        }
    }

    if (Get-Command wsl -ErrorAction SilentlyContinue) {
        $wslLatex = wsl which latexmk 2>$null
        if ($wslLatex) { return "wsl-latexmk" }
        $wslPdfLatex = wsl which pdflatex 2>$null
        if ($wslPdfLatex) { return "wsl-pdflatex" }
    }

    return $null
}

function Invoke-DocBuild([string]$RawInput, [string]$PythonCmd, [string]$TexEngine) {
    Ensure-Directories

    # Strip any file extension user might have typed (e.g. driver.md, driver.ml, driver.tex, driver.pdf)
    $BaseName = [System.IO.Path]::GetFileNameWithoutExtension($RawInput)
    if (-not $BaseName) { $BaseName = $RawInput }

    $MdFile = Join-Path $ContentDir "$BaseName.md"
    if (-not (Test-Path -LiteralPath $MdFile)) {
        Write-Host ""
        Write-Host "[ERROR] Document '$BaseName' was not found in content/ directory." -ForegroundColor Red
        Write-Host ""
        Show-AvailableDocuments
        Write-Host ""
        Write-Host "Usage:" -ForegroundColor Gray
        Write-Host "  fg <document-name>    Compile a specific document"
        Write-Host "  fg all                Compile all active documents"
        Write-Host "  fg help               Display command usage"
        Write-Host ""
        exit 1
    }

    $ScriptFile = Join-Path $ScriptsDir "md2latex.py"
    Write-Host "==> [MD2LATEX] Converting content/$BaseName.md -> latex-formatter/..." -ForegroundColor Cyan

    & $PythonCmd $ScriptFile --input $MdFile --formatter-dir $FormatterDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to convert Markdown to LaTeX structure." -ForegroundColor Red
        exit 1
    }

    $MasterDoc = "$BaseName.tex"
    Write-Host "==> [BUILD] Compiling $MasterDoc into build/$BaseName.pdf..." -ForegroundColor Cyan

    Push-Location $FormatterDir
    try {
        switch ($TexEngine) {
            "latexmk" {
                & latexmk -pdf -interaction=nonstopmode -synctex=1 -file-line-error -outdir="../build" $MasterDoc
            }
            "pdflatex" {
                Write-Host "    [Pass 1/2] Generating document structure..." -ForegroundColor Gray
                & pdflatex -interaction=nonstopmode -synctex=1 -file-line-error -enable-installer -output-directory="../build" $MasterDoc | Out-Null
                Write-Host "    [Pass 2/2] Resolving pagination and references..." -ForegroundColor Gray
                & pdflatex -interaction=nonstopmode -synctex=1 -file-line-error -enable-installer -output-directory="../build" $MasterDoc | Out-Null
            }
            "wsl-latexmk" {
                wsl latexmk -pdf -interaction=nonstopmode -synctex=1 -file-line-error -outdir="../build" $MasterDoc
            }
            "wsl-pdflatex" {
                wsl pdflatex -interaction=nonstopmode -synctex=1 -file-line-error -output-directory="../build" $MasterDoc
                wsl pdflatex -interaction=nonstopmode -synctex=1 -file-line-error -output-directory="../build" $MasterDoc
            }
            default {
                Write-Host "[ERROR] No LaTeX compiler found on PATH or standard TeX distributions." -ForegroundColor Red
                exit 1
            }
        }
    } finally {
        Pop-Location
    }

    Clean-AuxFiles

    $FinalPdf = Join-Path $BuildDir "$BaseName.pdf"
    if (Test-Path -LiteralPath $FinalPdf) {
        Write-Host "==> [DONE] Success: $FinalPdf (Clean build/ directory)" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] PDF output '$FinalPdf' was not produced. Please check compiler output." -ForegroundColor Yellow
    }
}

# Normalize target
$RawArg = $Target.Trim()

if ($RawArg -eq "clean-cache") {
    Clean-Cache
    exit 0
}
if ($RawArg -eq "clean") {
    Write-Host "==> [CLEAN] Purging auxiliary files in build/ and latex-formatter/..." -ForegroundColor Yellow
    Clean-AuxFiles
    Write-Host "==> [DONE] Auxiliary files cleaned." -ForegroundColor Green
    exit 0
}
if ($RawArg -eq "clean-all") {
    Write-Host "==> [DISTCLEAN] Purging build/ directory and LaTeX cache..." -ForegroundColor Red
    if (Test-Path -LiteralPath $BuildDir) {
        Remove-Item -Recurse -Force -LiteralPath $BuildDir -ErrorAction SilentlyContinue
    }
    Clean-Cache
    Write-Host "==> [DONE] Everything cleaned." -ForegroundColor Green
    exit 0
}
if ($RawArg -eq "help" -or $RawArg -eq "-h" -or $RawArg -eq "--help") {
    Write-Host "FoodLAB Guidebook Creator (FG) CLI" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: fg <target>"
    Write-Host "Commands:"
    Write-Host "  fg <name>          Compile content/<name>.md -> build/<name>.pdf"
    Write-Host "  fg all             Compile all active handbooks (skips templates)"
    Write-Host "  fg clean-cache     Remove generated LaTeX files (keeps PDFs in build/)"
    Write-Host "  fg clean           Remove intermediate auxiliary files"
    Write-Host "  fg clean-all       Purge build/ folder and LaTeX cache entirely"
    Write-Host ""
    Show-AvailableDocuments
    exit 0
}

$PythonCmd = Resolve-Python
$TexEngine = Resolve-TexEnvironment

if (-not $PythonCmd) {
    Write-Host "[ERROR] Python was not found on system PATH. Please ensure Python 3 is installed." -ForegroundColor Red
    exit 1
}

if ($RawArg -eq "all") {
    if (-not (Test-Path -LiteralPath $ContentDir)) {
        Write-Host "[INFO] Directory content/ does not exist yet." -ForegroundColor Yellow
        exit 0
    }
    $AllMds = Get-ChildItem -LiteralPath $ContentDir -Filter "*.md"
    $CompiledCount = 0
    foreach ($m in $AllMds) {
        if (Is-TemplateFile $m.Name) {
            Write-Host "[SKIP] $($m.Name) is marked as template (run 'fg $($m.BaseName)' to compile explicitly)." -ForegroundColor DarkGray
            continue
        }
        Invoke-DocBuild $m.BaseName $PythonCmd $TexEngine
        $CompiledCount++
    }
    if ($CompiledCount -eq 0) {
        Write-Host ""
        Write-Host "[INFO] No non-template documents found in content/ to build." -ForegroundColor Yellow
        Write-Host "To compile a template file directly, run: fg template-id or fg template-en" -ForegroundColor Gray
    }
} else {
    Invoke-DocBuild $RawArg $PythonCmd $TexEngine
}
