param(
    [string]$TargetMt5DataFolder = "C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$testerProfileDir = Join-Path $TargetMt5DataFolder "MQL5\Profiles\Tester"

if (-not (Test-Path -LiteralPath $testerProfileDir -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $testerProfileDir | Out-Null
}

$sourcePreset = Join-Path $repoRoot "presets\tester\EURUSD_H1_smoke_test.set"
$targetPreset = Join-Path $testerProfileDir "ForexAiTrade.set"
Copy-Item -LiteralPath $sourcePreset -Destination $targetPreset -Force

$iniPath = Join-Path $testerProfileDir "ForexAiTrade.EURUSD.H1.20260319_20260618.000.ini"
$ini = @"
;Expert Advisor single test: ForexAiTrade, EURUSD H1, every tick, 2026.03.19 - 2026.06.18
[Tester]
Expert=ForexAiTrade.ex5
Symbol=EURUSD
Period=H1
Optimization=0
Model=0
FromDate=2026.03.19
ToDate=2026.06.18
ForwardMode=0
Deposit=10000
Currency=USD
ProfitInPips=0
Leverage=500
ExecutionMode=0
OptimizationCriterion=0
Visual=0
[TesterInputs]
; Safety
InpLiveTradingEnabled=true||false||0||true||N
InpDemoSafeMode=true||false||0||true||N
InpMagicNumber=26062003||26061901||1||260619010||N
InpSlippagePoints=20||20||1||200||N
InpTradeOnlyOnNewBar=true||false||0||true||N
InpManageExistingPositions=true||false||0||true||N
InpRequireStrategyTester=true||false||0||true||N
; Broker Symbol Handling
InpAllowedSymbolsCsv=EURUSD,EURUSD#
InpCanonicalSymbolName=EURUSD
InpBrokerGoldSymbolName=GOLDm#
InpPrintSymbolDiagnostics=true||false||0||true||N
; Logging
InpMirrorLogsToFile=true||false||0||true||N
InpMirrorLogsUseCommonFolder=true||false||0||true||N
InpMirrorLogFileName=ForexAiTrade_EURUSD_H1_smoke.log
; Timeframes
InpSignalTimeframe=16385||0||0||49153||N
; Risk
InpRiskPercentPerTrade=0.10||0.5||0.050000||5.000000||N
InpMaxDailyLossPercent=1.00||2.0||0.200000||20.000000||N
InpMaxWeeklyLossPercent=3.00||5.0||0.500000||50.000000||N
InpMaxTotalDrawdownPercent=10.00||20.0||2.000000||200.000000||N
InpMaxOpenOrders=1||1||1||10||N
InpMaxSpreadPoints=25||25||1||250||N
InpMaxLosingStreak=4||4||1||40||N
InpEquityKillSwitchPercent=15.00||30.0||3.000000||300.000000||N
InpMinLot=0.01||0.01||0.001000||0.100000||N
InpMaxLot=0.50||2.0||0.200000||20.000000||N
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

$ini | Set-Content -Path $iniPath -Encoding ASCII

Write-Host "Installed Strategy Tester preset/profile:"
Write-Host $targetPreset -ForegroundColor Cyan
Write-Host $iniPath -ForegroundColor Cyan
