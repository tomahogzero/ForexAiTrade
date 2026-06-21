param(
    [string]$TargetMt5DataFolder
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Assert-Directory {
    param(
        [string]$Path,
        [string]$Description
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "$Description not found: $Path"
    }
}

function Copy-FilteredDirectory {
    param(
        [string]$Source,
        [string]$Destination
    )

    Assert-Directory -Path $Source -Description "Source folder"
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null

    Get-ChildItem -LiteralPath $Source -Recurse -File | Where-Object {
        $_.Extension -notin @(".ex5", ".pyc") -and
        $_.FullName -notmatch "\\__pycache__\\"
    } | ForEach-Object {
        $relative = $_.FullName.Substring($Source.Length).TrimStart("\", "/")
        $target = Join-Path $Destination $relative
        $targetDir = Split-Path -Parent $target
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
        Copy-Item -LiteralPath $_.FullName -Destination $target -Force
        Write-Host "Copied: $relative"
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($TargetMt5DataFolder)) {
    Write-Host "Open MT5, then go to File > Open Data Folder. Paste that folder path below."
    $TargetMt5DataFolder = Read-Host "MT5 Data Folder path"
}

$TargetMt5DataFolder = $TargetMt5DataFolder.Trim('"')

Write-Step "Validating MT5 Data Folder"
Assert-Directory -Path $TargetMt5DataFolder -Description "MT5 Data Folder"
Assert-Directory -Path (Join-Path $TargetMt5DataFolder "MQL5") -Description "MQL5 folder"
Assert-Directory -Path (Join-Path $TargetMt5DataFolder "MQL5\Experts") -Description "MQL5 Experts folder"
Assert-Directory -Path (Join-Path $TargetMt5DataFolder "MQL5\Include") -Description "MQL5 Include folder"

$sourceExperts = Join-Path $repoRoot "MQL5\Experts\ForexAiTrade"
$sourceInclude = Join-Path $repoRoot "MQL5\Include\ForexAiTrade"
$targetExperts = Join-Path $TargetMt5DataFolder "MQL5\Experts\ForexAiTrade"
$targetInclude = Join-Path $TargetMt5DataFolder "MQL5\Include\ForexAiTrade"

Assert-Directory -Path $sourceExperts -Description "ForexAiTrade source Experts folder"
Assert-Directory -Path $sourceInclude -Description "ForexAiTrade source Include folder"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = Join-Path $TargetMt5DataFolder "ForexAiTrade_backup\$stamp"

Write-Step "Backing up existing target files"
if (Test-Path -LiteralPath $targetExperts -PathType Container) {
    $backupExperts = Join-Path $backupRoot "MQL5\Experts\ForexAiTrade"
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupExperts) | Out-Null
    Copy-Item -LiteralPath $targetExperts -Destination $backupExperts -Recurse -Force
    Write-Host "Backed up: $targetExperts -> $backupExperts"
}
else {
    Write-Host "No existing target Experts folder to back up."
}

if (Test-Path -LiteralPath $targetInclude -PathType Container) {
    $backupInclude = Join-Path $backupRoot "MQL5\Include\ForexAiTrade"
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupInclude) | Out-Null
    Copy-Item -LiteralPath $targetInclude -Destination $backupInclude -Recurse -Force
    Write-Host "Backed up: $targetInclude -> $backupInclude"
}
else {
    Write-Host "No existing target Include folder to back up."
}

Write-Step "Copying active ForexAiTrade EA source"
Copy-FilteredDirectory -Source $sourceExperts -Destination $targetExperts
Copy-FilteredDirectory -Source $sourceInclude -Destination $targetInclude

Write-Step "Installation copy complete"
Write-Host "Archive folder was not copied."
Write-Host ".ex5, __pycache__, and .pyc files were not copied."
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open MetaEditor."
Write-Host "2. Open MQL5\Experts\ForexAiTrade\ForexAiTrade.mq5 from the MT5 Data Folder."
Write-Host "3. Compile ForexAiTrade.mq5."
Write-Host "4. Confirm 0 errors and 0 warnings."
Write-Host "5. Open MT5 Strategy Tester."
Write-Host "6. Load a preset from this repo's presets\tester\ or presets\sanity\ folder."
Write-Host "7. Run a no-trade sanity test before any smoke test."
Write-Host ""
Write-Host "Important: Do not attach tester presets to a live/demo chart. They require Strategy Tester by input gate."
