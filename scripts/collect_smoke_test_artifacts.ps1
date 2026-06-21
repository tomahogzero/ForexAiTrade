param(
    [string[]]$ReportPaths,
    [string[]]$LogPaths,
    [string]$OutputRoot = "smoke_test_artifacts"
)

$ErrorActionPreference = "Stop"

function Copy-ProvidedFiles {
    param(
        [string[]]$Paths,
        [string]$Destination
    )

    if ($null -eq $Paths -or $Paths.Count -eq 0) {
        return
    }

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null

    foreach ($path in $Paths) {
        if ([string]::IsNullOrWhiteSpace($path)) {
            continue
        }

        $cleanPath = $path.Trim('"')
        if (Test-Path -LiteralPath $cleanPath -PathType Leaf) {
            Copy-Item -LiteralPath $cleanPath -Destination $Destination -Force
            Write-Host "Copied: $cleanPath"
        }
        elseif (Test-Path -LiteralPath $cleanPath -PathType Container) {
            $folderName = Split-Path -Leaf $cleanPath
            $targetFolder = Join-Path $Destination $folderName
            Copy-Item -LiteralPath $cleanPath -Destination $targetFolder -Recurse -Force
            Write-Host "Copied folder: $cleanPath"
        }
        else {
            Write-Warning "Path not found, skipped: $cleanPath"
        }
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$artifactRoot = Join-Path $repoRoot (Join-Path $OutputRoot $stamp)
$reportsDir = Join-Path $artifactRoot "reports"
$logsDir = Join-Path $artifactRoot "logs"

New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

Write-Host "Created artifact folder:"
Write-Host $artifactRoot -ForegroundColor Cyan

if ($null -eq $ReportPaths -or $ReportPaths.Count -eq 0) {
    Write-Host ""
    Write-Host "If automatic collection is not reliable, export MT5 Strategy Tester reports manually and place them here:"
    Write-Host $reportsDir -ForegroundColor Yellow
    $manualReports = Read-Host "Optional: paste report file/folder paths separated by semicolon, or press Enter"
    if (-not [string]::IsNullOrWhiteSpace($manualReports)) {
        $ReportPaths = $manualReports -split ";"
    }
}

if ($null -eq $LogPaths -or $LogPaths.Count -eq 0) {
    Write-Host ""
    Write-Host "Optional: provide MT5 Journal/Experts log files or screenshot folders."
    Write-Host "They will be copied here:"
    Write-Host $logsDir -ForegroundColor Yellow
    $manualLogs = Read-Host "Optional: paste log/screenshot file/folder paths separated by semicolon, or press Enter"
    if (-not [string]::IsNullOrWhiteSpace($manualLogs)) {
        $LogPaths = $manualLogs -split ";"
    }
}

Copy-ProvidedFiles -Paths $ReportPaths -Destination $reportsDir
Copy-ProvidedFiles -Paths $LogPaths -Destination $logsDir

$readme = @"
ForexAiTrade Smoke Test Artifacts
=================================

Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Please send this whole folder back for review:
$artifactRoot

Recommended contents:

1. MT5 Strategy Tester exported report files
   - HTML, HTM, XML, CSV, or TXT are useful.

2. MT5 Journal / Experts logs
   - Include the period covering EA initialization and the test run.
   - Logs should show symbol diagnostics and safety block reasons.

3. Screenshots
   - Strategy Tester settings page.
   - Inputs tab showing loaded preset.
   - Results tab.
   - Graph tab if available.
   - Journal tab with ForexAiTrade messages.

4. Notes
   - Symbol tested, for example GOLDm#.
   - Timeframe, for example H1.
   - Preset used.
   - Period tested.
   - Any unexpected behavior.

Do not include live account passwords or private credentials.
Smoke tests are behavior checks only, not profitability proof.
"@

$readmePath = Join-Path $artifactRoot "README.txt"
$readme | Set-Content -Path $readmePath -Encoding UTF8

Write-Host ""
Write-Host "README created: $readmePath" -ForegroundColor Green
Write-Host "Done. Review the folder and add any missing reports/screenshots before sending it back."
