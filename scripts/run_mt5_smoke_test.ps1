param(
    [string]$TerminalExe = "C:\Program Files\XM Global MT5\terminal64.exe",
    [string]$Symbol = "EURUSD",
    [string]$Period = "H1",
    [string]$FromDate = "2026.03.19",
    [string]$ToDate = "2026.06.18",
    [int]$Deposit = 10000,
    [string]$Currency = "USD"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$artifactRoot = Join-Path $repoRoot (Join-Path "smoke_test_artifacts" $stamp)
$configPath = Join-Path $artifactRoot "mt5_smoke_test.ini"
$reportPath = Join-Path $artifactRoot ("ForexAiTrade_{0}_{1}_smoke_report" -f ($Symbol -replace '[\\/:*?""<>|#]', '_'), $Period)

New-Item -ItemType Directory -Force -Path $artifactRoot | Out-Null

$canonical = $Symbol
if ($Symbol -match "EURUSD") {
    $canonical = "EURUSD"
}
elseif ($Symbol -match "USDJPY") {
    $canonical = "USDJPY"
}
elseif ($Symbol -match "GOLD|XAU") {
    $canonical = "GOLD"
}

$magic = 26062003
if ($Symbol -match "GOLD|XAU") {
    $magic = if ($Period -eq "H4") { 26062002 } else { 26062001 }
}
elseif ($Symbol -match "USDJPY") {
    $magic = 26062004
}

$risk = if ($Symbol -match "GOLD|XAU") { "0.05" } else { "0.10" }
$maxSpread = if ($Symbol -match "GOLD|XAU") { "100" } else { "25" }
$maxLot = if ($Symbol -match "GOLD|XAU") { "0.20" } else { "0.50" }
$allowedSymbols = if ($Symbol -match "GOLD|XAU") { "GOLDm#,GOLD#,GOLD,XAUUSD" } elseif ($Symbol -match "USDJPY") { "USDJPY,USDJPY#" } else { "EURUSD,EURUSD#" }
$logSymbolName = ($canonical -replace '[^A-Za-z0-9_]', '_')
$logFile = "ForexAiTrade_${logSymbolName}_${Period}_smoke.log"
$timeframeInput = switch ($Period.ToUpperInvariant()) {
    "M1" { 1 }
    "M5" { 5 }
    "M15" { 15 }
    "M30" { 30 }
    "H1" { 16385 }
    "H4" { 16388 }
    "D1" { 16408 }
    default { 16385 }
}

$config = @"
; ForexAiTrade command-line smoke test
[Tester]
Expert=ForexAiTrade\ForexAiTrade.ex5
Symbol=$Symbol
Period=$Period
Optimization=0
Model=0
FromDate=$FromDate
ToDate=$ToDate
ForwardMode=0
Deposit=$Deposit
Currency=$Currency
ProfitInPips=0
Leverage=500
ExecutionMode=0
OptimizationCriterion=0
Visual=0
Report=$reportPath
ReplaceReport=1

[TesterInputs]
; Safety
InpLiveTradingEnabled=true||false||0||true||N
InpDemoSafeMode=true||false||0||true||N
InpMagicNumber=$magic||26061901||1||260619010||N
InpSlippagePoints=20||20||1||200||N
InpTradeOnlyOnNewBar=true||false||0||true||N
InpManageExistingPositions=true||false||0||true||N
InpRequireStrategyTester=true||false||0||true||N
; Broker Symbol Handling
InpAllowedSymbolsCsv=$allowedSymbols
InpCanonicalSymbolName=$canonical
InpBrokerGoldSymbolName=GOLDm#
InpPrintSymbolDiagnostics=true||false||0||true||N
; Logging
InpMirrorLogsToFile=true||false||0||true||N
InpMirrorLogsUseCommonFolder=true||false||0||true||N
InpMirrorLogFileName=$logFile
; Timeframes
InpSignalTimeframe=$timeframeInput||0||0||49153||N
; Risk
InpRiskPercentPerTrade=$risk||0.5||0.050000||5.000000||N
InpMaxDailyLossPercent=1.00||2.0||0.200000||20.000000||N
InpMaxWeeklyLossPercent=3.00||5.0||0.500000||50.000000||N
InpMaxTotalDrawdownPercent=10.00||20.0||2.000000||200.000000||N
InpMaxOpenOrders=1||1||1||10||N
InpMaxSpreadPoints=$maxSpread||25||1||250||N
InpMaxLosingStreak=4||4||1||40||N
InpEquityKillSwitchPercent=15.00||30.0||3.000000||300.000000||N
InpMinLot=0.01||0.01||0.001000||0.100000||N
InpMaxLot=$maxLot||2.0||0.200000||20.000000||N
; Regime Detector
InpAdxPeriod=14||14||1||140||N
InpTrendAdxMin=22.0||22.0||2.200000||220.000000||N
InpSidewayAdxMax=18.0||18.0||1.800000||180.000000||N
InpAtrPeriod=14||14||1||140||N
InpMinAtrPercent=0.03||0.03||0.003000||0.300000||N
InpMaxAtrPercent=0.8||0.8||0.080000||8.000000||N
InpEmaFastPeriod=50||50||1||500||N
InpEmaSlowPeriod=200||200||1||2000||N
InpTrendSlopeMinPoints=8.0||8.0||0.800000||80.000000||N
InpBandsPeriod=20||20||1||200||N
InpBandsDeviation=2.0||2.0||0.200000||20.000000||N
InpBreakoutBbWidthMinPct=0.2||0.2||0.020000||2.000000||N
InpSidewayBbWidthMaxPct=0.18||0.18||0.018000||1.800000||N
; Trend Following
InpTrendAtrStop=2.0||2.0||0.200000||20.000000||N
InpTrendRewardRisk=2.0||2.0||0.200000||20.000000||N
InpTrendPullbackEmaPeriod=20||20||1||200||N
; Breakout
InpBreakoutLookbackBars=24||24||1||240||N
InpBreakoutAtrBuffer=0.15||0.15||0.015000||1.500000||N
InpBreakoutAtrStop=1.8||1.8||0.180000||18.000000||N
InpBreakoutRewardRisk=1.8||1.8||0.180000||18.000000||N
; Mean Reversion
InpMeanRevAtrStop=1.5||1.5||0.150000||15.000000||N
InpMeanRevRewardRisk=1.2||1.2||0.120000||12.000000||N
InpMeanRevRsiBuyMax=35.0||35.0||3.500000||350.000000||N
InpMeanRevRsiSellMin=65.0||65.0||6.500000||650.000000||N
InpRsiPeriod=14||14||1||140||N
; Position Management
InpUseTrailingStop=true||false||0||true||N
InpTrailingAtrMultiplier=1.5||1.5||0.150000||15.000000||N
"@

$config | Set-Content -Path $configPath -Encoding ASCII

Write-Host "Created MT5 smoke-test config:"
Write-Host $configPath -ForegroundColor Cyan
Write-Host "Expected report prefix:"
Write-Host $reportPath -ForegroundColor Cyan
Write-Host "Expected EA file log:"
Write-Host "$env:APPDATA\MetaQuotes\Terminal\Common\Files\$logFile" -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath $TerminalExe -PathType Leaf)) {
    throw "MT5 terminal executable not found: $TerminalExe"
}

Start-Process -FilePath $TerminalExe -ArgumentList "/config:`"$configPath`"" -WindowStyle Hidden

Write-Host "MT5 was launched with the smoke-test config. Wait for Strategy Tester to finish, then run:"
Write-Host "powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\collect_ea_file_logs.ps1" -ForegroundColor Yellow
