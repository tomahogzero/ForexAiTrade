param(
    [string]$CommonFilesFolder = "$env:APPDATA\MetaQuotes\Terminal\Common\Files",
    [string[]]$LogFileNames = @(
        "ForexAiTrade_GOLD_H1_smoke.log",
        "ForexAiTrade_GOLD_H4_smoke.log",
        "ForexAiTrade_EURUSD_H1_smoke.log",
        "ForexAiTrade_USDJPY_H1_smoke.log",
        "ForexAiTrade_GOLD_H1_sanity.log",
        "ForexAiTrade_EURUSD_H1_sanity.log",
        "ForexAiTrade_smoke.log"
    ),
    [string]$OutputRoot = "smoke_test_artifacts"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$targetDir = Join-Path $repoRoot (Join-Path $OutputRoot (Join-Path $stamp "ea_file_logs"))

New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

Write-Host "ForexAiTrade EA file log collector"
Write-Host "Source: $CommonFilesFolder" -ForegroundColor Cyan
Write-Host "Target: $targetDir" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path -LiteralPath $CommonFilesFolder -PathType Container)) {
    Write-Warning "Common Files folder was not found. Check InpMirrorLogsUseCommonFolder and MT5 installation."
    Write-Host "Expected folder:"
    Write-Host $CommonFilesFolder -ForegroundColor Yellow
    exit 1
}

$copied = 0
foreach ($name in $LogFileNames) {
    $sourcePath = Join-Path $CommonFilesFolder $name
    if (Test-Path -LiteralPath $sourcePath -PathType Leaf) {
        Copy-Item -LiteralPath $sourcePath -Destination $targetDir -Force
        Write-Host "Copied: $name" -ForegroundColor Green
        $copied++
    }
}

$readmePath = Join-Path $targetDir "README.txt"
@"
ForexAiTrade EA File Logs
=========================

Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Source:
$CommonFilesFolder

Target:
$targetDir

These files are mirrored EA logs from MT5 when InpMirrorLogsToFile=true.
They are behavior/debug logs only and are not profitability proof.
"@ | Set-Content -Path $readmePath -Encoding UTF8

if ($copied -eq 0) {
    Write-Warning "No ForexAiTrade EA file logs were found."
    Write-Host "After loading a smoke/sanity preset, confirm these inputs:" -ForegroundColor Yellow
    Write-Host "  InpMirrorLogsToFile=true"
    Write-Host "  InpMirrorLogsUseCommonFolder=true"
    Write-Host "Then run the Strategy Tester again and re-run this script."
}
else {
    Write-Host ""
    Write-Host "Copied $copied log file(s)." -ForegroundColor Green
}

Write-Host "README created: $readmePath"
