param(
    [string]$ResearchMatrixPath = "research\research_matrix.json",
    [string]$TerminalExe = "C:\Program Files\XM Global MT5\terminal64.exe",
    [string]$TerminalDataFolder = "",
    [string]$TesterRootFolder = "",
    [int]$CaseTimeoutMinutes = 10,
    [int]$RetryCount = 0,
    [int]$PollIntervalSeconds = 2,
    [string]$OutputRoot = "research\runs",
    [switch]$KeepTerminalOpen,
    [switch]$UsePortableMode,
    [string]$DedicatedTerminalExe = "",
    [string]$DedicatedDataFolder = "",
    [switch]$IntegrationOnly,
    [string]$CaseId = "",
    [string[]]$CaseIds = @(),
    [string[]]$Phases = @()
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$matrixPath = if ([System.IO.Path]::IsPathRooted($ResearchMatrixPath)) { $ResearchMatrixPath } else { Join-Path $repoRoot $ResearchMatrixPath }
$outputRootPath = if ([System.IO.Path]::IsPathRooted($OutputRoot)) { $OutputRoot } else { Join-Path $repoRoot $OutputRoot }

if (-not [string]::IsNullOrWhiteSpace($DedicatedTerminalExe)) {
    $TerminalExe = $DedicatedTerminalExe
}
if (-not [string]::IsNullOrWhiteSpace($DedicatedDataFolder)) {
    $TerminalDataFolder = $DedicatedDataFolder
}

function Write-RunnerLog {
    param([string]$Path, [string]$Message)
    $line = "$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") $Message"
    Add-Content -Path $Path -Value $line -Encoding UTF8
    Write-Host $line
}

function Convert-TimeframeToInput {
    param([string]$Timeframe)
    switch ($Timeframe.ToUpperInvariant()) {
        "M1" { return 1 }
        "M5" { return 5 }
        "M15" { return 15 }
        "M30" { return 30 }
        "H1" { return 16385 }
        "H4" { return 16388 }
        "D1" { return 16408 }
        default { return 16385 }
    }
}

function Convert-DateForMt5 {
    param([string]$Date)
    return $Date.Replace("-", ".")
}

function Normalize-PhaseList {
    param([string[]]$Values)
    $normalized = @()
    foreach ($value in $Values) {
        if ([string]::IsNullOrWhiteSpace($value)) {
            continue
        }
        foreach ($part in ($value -split ",")) {
            $trimmed = $part.Trim()
            if (-not [string]::IsNullOrWhiteSpace($trimmed)) {
                $normalized += $trimmed
            }
        }
    }
    return @($normalized)
}

function Get-CasePropertyValue {
    param(
        [object]$Case,
        [string]$Name,
        [object]$Default
    )
    if ($null -ne $Case -and $Case.PSObject.Properties.Name -contains $Name -and $null -ne $Case.$Name) {
        return $Case.$Name
    }
    return $Default
}

function Convert-BoolText {
    param([object]$Value)
    return ([System.Convert]::ToBoolean($Value)).ToString().ToLowerInvariant()
}

function Get-TimeframeInputFromCase {
    param([object]$Case, [string]$Name, [string]$DefaultTimeframe)
    $value = [string](Get-CasePropertyValue -Case $Case -Name $Name -Default $DefaultTimeframe)
    if ([string]::IsNullOrWhiteSpace($value)) {
        $value = $DefaultTimeframe
    }
    return Convert-TimeframeToInput -Timeframe $value
}

function Get-CanonicalDefaults {
    param([string]$Symbol, [string]$Canonical, [string]$Timeframe)
    $magic = 26062003
    if ($Canonical -eq "GOLD") {
        $magic = if ($Timeframe -eq "H4") { 26062002 } else { 26062001 }
    }
    elseif ($Canonical -eq "USDJPY") {
        $magic = 26062004
    }

    $allowed = if ($Canonical -eq "GOLD") {
        $Symbol
    }
    elseif ($Canonical -eq "USDJPY") {
        "USDJPY,USDJPY#"
    }
    else {
        "EURUSD,EURUSD#"
    }

    return [pscustomobject]@{
        Magic = $magic
        AllowedSymbols = $allowed
        MaxSpread = if ($Canonical -eq "GOLD") { 100 } else { 25 }
        MaxLot = if ($Canonical -eq "GOLD") { "0.20" } else { "0.50" }
    }
}

function Read-TextFileSafe {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return @()
    }
    return @(Get-Content -LiteralPath $Path -ErrorAction SilentlyContinue)
}

function Find-UpdatedLogs {
    param([string[]]$Roots, [datetime]$Since)
    $logs = @()
    foreach ($root in $Roots) {
        if ([string]::IsNullOrWhiteSpace($root) -or -not (Test-Path -LiteralPath $root -PathType Container)) {
            continue
        }
        $logs += Get-ChildItem -LiteralPath $root -Recurse -Filter "*.log" -File -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -ge $Since } |
            Sort-Object LastWriteTime -Descending
    }
    return $logs
}

function Test-FileStable {
    param([string]$Path, [int]$Polls = 3, [int]$Seconds = 1)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $false
    }

    $last = Get-Item -LiteralPath $Path
    for ($i = 0; $i -lt $Polls; $i++) {
        Start-Sleep -Seconds $Seconds
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            return $false
        }
        $current = Get-Item -LiteralPath $Path
        if ($current.Length -ne $last.Length -or $current.LastWriteTime -ne $last.LastWriteTime) {
            $last = $current
            $i = -1
        }
    }
    return $true
}

function Get-ReportArtifactCandidates {
    param([string]$BasePath)
    return @(
        $BasePath,
        "$BasePath.htm",
        "$BasePath.html",
        "$BasePath.xml",
        "$BasePath.png",
        "$BasePath-hst.png",
        "$BasePath-mfemae.png",
        "$BasePath-holding.png"
    )
}

function Resolve-ReportPath {
    param(
        [string]$BasePath,
        [datetime]$NotBefore = [datetime]::MinValue
    )
    $candidates = @($BasePath, "$BasePath.htm", "$BasePath.html", "$BasePath.xml")
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $item = Get-Item -LiteralPath $candidate
            if ($item.LastWriteTime -lt $NotBefore) {
                continue
            }
            return $candidate
        }
    }
    return $null
}

function Resolve-ReportArtifacts {
    param(
        [string]$BasePath,
        [datetime]$NotBefore = [datetime]::MinValue
    )

    $artifacts = @()
    foreach ($candidate in (Get-ReportArtifactCandidates -BasePath $BasePath)) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $item = Get-Item -LiteralPath $candidate
            if ($item.LastWriteTime -ge $NotBefore) {
                $artifacts += $item
            }
        }
    }
    return @($artifacts)
}

function Copy-ReportArtifacts {
    param(
        [string]$SourceBasePath,
        [string]$TargetBasePath,
        [datetime]$NotBefore = [datetime]::MinValue
    )

    $copied = @()
    foreach ($artifact in (Resolve-ReportArtifacts -BasePath $SourceBasePath -NotBefore $NotBefore)) {
        $suffix = ""
        if ($artifact.FullName.StartsWith($SourceBasePath, [System.StringComparison]::OrdinalIgnoreCase)) {
            $suffix = $artifact.FullName.Substring($SourceBasePath.Length)
        }
        if ([string]::IsNullOrWhiteSpace($suffix)) {
            $suffix = [System.IO.Path]::GetExtension($artifact.FullName)
        }
        $target = "$TargetBasePath$suffix"
        Copy-Item -LiteralPath $artifact.FullName -Destination $target -Force
        $copied += $target
    }
    return @($copied)
}

function Wait-ReportPath {
    param(
        [string]$BasePath,
        [int]$TimeoutSeconds,
        [int]$PollIntervalSeconds,
        [datetime]$NotBefore = [datetime]::MinValue
    )

    $deadline = (Get-Date).AddSeconds([Math]::Max(1, $TimeoutSeconds))
    while ((Get-Date) -lt $deadline) {
        $resolved = Resolve-ReportPath -BasePath $BasePath -NotBefore $NotBefore
        if ($resolved) {
            return $resolved
        }
        Start-Sleep -Seconds ([Math]::Max(1, $PollIntervalSeconds))
    }

    return (Resolve-ReportPath -BasePath $BasePath -NotBefore $NotBefore)
}

function Write-Status {
    param([string]$Path, [hashtable]$Status)
    $Status | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Invoke-PafDiagnosticsParser {
    param(
        [string]$CaseDir,
        [hashtable]$Status,
        [object]$Case
    )

    $enabled = [System.Convert]::ToBoolean((Get-CasePropertyValue -Case $Case -Name "enable_price_action_fibo" -Default $false))
    $diagnosticOnly = [System.Convert]::ToBoolean((Get-CasePropertyValue -Case $Case -Name "price_action_fibo_diagnostics_only" -Default $true))
    if (-not ($enabled -and $diagnosticOnly)) {
        return
    }

    $parser = Join-Path $repoRoot "tools\paf_diagnostic_parser.py"
    if (-not (Test-Path -LiteralPath $parser -PathType Leaf)) {
        $Status.paf_diagnostics_status = "PARSER_MISSING"
        return
    }

    $parseResult = & python $parser --case-dir $CaseDir --results-root (Join-Path $repoRoot "research\results") 2>&1
    if ($LASTEXITCODE -ne 0) {
        $Status.paf_diagnostics_status = "PARSE_ERROR"
        $Status.paf_diagnostics_message = ($parseResult -join "`n")
        return
    }

    $summaryPath = Join-Path $CaseDir "paf_diagnostics.json"
    if (Test-Path -LiteralPath $summaryPath -PathType Leaf) {
        $paf = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json
        $Status.paf_diagnostics_status = "FOUND"
        $Status.paf_diagnostic_count = $paf.diagnostic_count
        $Status.paf_authoritative_source = $paf.authoritative_source
        $Status.paf_tester_excerpt_diagnostic_count = $paf.tester_excerpt_diagnostic_count
        $Status.paf_forbidden_action_marker_count = $paf.forbidden_action_marker_count
        $Status.paf_baseline_fallback_marker_count = $paf.baseline_fallback_marker_count
    }
}

function New-TesterConfig {
    param(
        [object]$Case,
        [string]$Phase,
        [object]$Period,
        [string]$RunId,
        [string]$CaseId,
        [string]$CaseDir,
        [string]$ReportBasePath,
        [string]$EaLogFile,
        [string]$ExitTelemetryFile
    )

    $defaults = Get-CanonicalDefaults -Symbol $Case.actual_symbol -Canonical $Case.canonical_symbol -Timeframe $Case.timeframe
    $magicNumber = [long](Get-CasePropertyValue -Case $Case -Name "magic_number" -Default $defaults.Magic)
    $timeframeInput = Convert-TimeframeToInput -Timeframe $Case.timeframe
    $fromDate = Convert-DateForMt5 -Date $Period.from
    $toDate = Convert-DateForMt5 -Date $Period.to
    $currency = if ($Case.currency) { $Case.currency } else { "USD" }
    $leverage = if ($Case.leverage) { [int]$Case.leverage } else { 500 }
    $model = if ($null -ne $Case.model) { [int]$Case.model } else { 0 }
    $risk = "{0:0.00}" -f [double]$Case.risk_percent
    $deposit = [int]$Case.deposit
    $brokerGoldSymbol = if ($Case.canonical_symbol -eq "GOLD") { $Case.actual_symbol } else { "GOLDm#" }
    $enableExitTelemetry = Convert-BoolText (Get-CasePropertyValue -Case $Case -Name "enable_exit_telemetry" -Default $true)
    $logModifyEvents = Convert-BoolText (Get-CasePropertyValue -Case $Case -Name "log_position_modify_events" -Default $true)
    $modifyStepPoints = "{0:0.##}" -f [double](Get-CasePropertyValue -Case $Case -Name "exit_telemetry_min_modify_step_points" -Default 0)
    $useTrailingStop = Convert-BoolText (Get-CasePropertyValue -Case $Case -Name "use_trailing_stop" -Default $true)
    $trailingMultiplier = "{0:0.##}" -f [double](Get-CasePropertyValue -Case $Case -Name "trailing_atr_multiplier" -Default 1.5)
    $riskGateMode = [string](Get-CasePropertyValue -Case $Case -Name "risk_gate_mode" -Default "NORMAL")
    $cooldownBars = [int](Get-CasePropertyValue -Case $Case -Name "losing_streak_cooldown_bars" -Default 24)
    $manageExistingPositions = Convert-BoolText (Get-CasePropertyValue -Case $Case -Name "manage_existing_positions" -Default $true)
    $enablePriceActionFibo = Convert-BoolText (Get-CasePropertyValue -Case $Case -Name "enable_price_action_fibo" -Default $false)
    $pafDiagnosticsOnly = Convert-BoolText (Get-CasePropertyValue -Case $Case -Name "price_action_fibo_diagnostics_only" -Default $true)
    $pafUsePendingOrders = Convert-BoolText (Get-CasePropertyValue -Case $Case -Name "paf_use_pending_orders" -Default $false)
    $pafMaxPendingOrders = [int](Get-CasePropertyValue -Case $Case -Name "paf_max_pending_orders" -Default 0)
    $pafLogOnlyOnNewBar = Convert-BoolText (Get-CasePropertyValue -Case $Case -Name "paf_log_only_on_new_bar" -Default $true)
    $pafEntryTimeframe = Get-TimeframeInputFromCase -Case $Case -Name "paf_entry_timeframe" -DefaultTimeframe $Case.timeframe
    $pafHigherTimeframe = Get-TimeframeInputFromCase -Case $Case -Name "paf_higher_timeframe" -DefaultTimeframe $Case.timeframe

    $preset = @"
InpLiveTradingEnabled=true
InpDemoSafeMode=true
InpMagicNumber=$magicNumber
InpSlippagePoints=20
InpTradeOnlyOnNewBar=true
InpManageExistingPositions=$manageExistingPositions
InpRequireStrategyTester=true
InpAllowedSymbolsCsv=$($defaults.AllowedSymbols)
InpCanonicalSymbolName=$($Case.canonical_symbol)
InpBrokerGoldSymbolName=$brokerGoldSymbol
InpPrintSymbolDiagnostics=true
InpMirrorLogsToFile=true
InpMirrorLogsUseCommonFolder=true
InpMirrorLogFileName=$EaLogFile
InpEnableExitTelemetry=$enableExitTelemetry
InpExitTelemetryFileName=$ExitTelemetryFile
InpLogPositionModifyEvents=$logModifyEvents
InpLogRMultipleOnClose=true
InpExitTelemetryMinModifyStepPoints=$modifyStepPoints
InpSignalTimeframe=$timeframeInput
InpRiskPercentPerTrade=$risk
InpMaxDailyLossPercent=1.00
InpMaxWeeklyLossPercent=3.00
InpMaxTotalDrawdownPercent=10.00
InpMaxOpenOrders=1
InpMaxSpreadPoints=$($defaults.MaxSpread)
InpMaxLosingStreak=4
InpRiskGateMode=$riskGateMode
InpLosingStreakCooldownBars=$cooldownBars
InpEquityKillSwitchPercent=15.00
InpMinLot=0.01
InpMaxLot=$($defaults.MaxLot)
InpUseTrailingStop=$useTrailingStop
InpManagePositionsOnlyOnNewBar=false
InpTrailingAtrMultiplier=$trailingMultiplier
InpEnablePriceActionFibo=$enablePriceActionFibo
InpPriceActionFiboDiagnosticsOnly=$pafDiagnosticsOnly
InpPAFEntryTimeframe=$pafEntryTimeframe
InpPAFHigherTimeframe=$pafHigherTimeframe
InpPAFUsePendingOrders=$pafUsePendingOrders
InpPAFMaxPendingOrders=$pafMaxPendingOrders
InpPAFLogOnlyOnNewBar=$pafLogOnlyOnNewBar
"@
    $presetPath = Join-Path $CaseDir "effective_preset.set"
    $preset | Set-Content -LiteralPath $presetPath -Encoding ASCII

    $ini = @"
; ForexAiTrade controlled research case
; RunId=$RunId
; CaseId=$CaseId
[Tester]
Expert=ForexAiTrade\ForexAiTrade.ex5
Symbol=$($Case.actual_symbol)
Period=$($Case.timeframe)
Optimization=0
Model=$model
FromDate=$fromDate
ToDate=$toDate
ForwardMode=0
Deposit=$deposit
Currency=$currency
ProfitInPips=0
Leverage=$leverage
ExecutionMode=0
OptimizationCriterion=0
Visual=0
Report=$ReportBasePath
ReplaceReport=1
ShutdownTerminal=1

[TesterInputs]
InpLiveTradingEnabled=true||false||0||true||N
InpDemoSafeMode=true||false||0||true||N
InpMagicNumber=$magicNumber||26061901||1||260619010||N
InpSlippagePoints=20||20||1||200||N
InpTradeOnlyOnNewBar=true||false||0||true||N
InpManageExistingPositions=$manageExistingPositions||false||0||true||N
InpRequireStrategyTester=true||false||0||true||N
InpAllowedSymbolsCsv=$($defaults.AllowedSymbols)
InpCanonicalSymbolName=$($Case.canonical_symbol)
InpBrokerGoldSymbolName=$brokerGoldSymbol
InpPrintSymbolDiagnostics=true||false||0||true||N
InpMirrorLogsToFile=true||false||0||true||N
InpMirrorLogsUseCommonFolder=true||false||0||true||N
InpMirrorLogFileName=$EaLogFile
InpEnableExitTelemetry=$enableExitTelemetry||false||0||true||N
InpExitTelemetryFileName=$ExitTelemetryFile
InpLogPositionModifyEvents=$logModifyEvents||false||0||true||N
InpLogRMultipleOnClose=true||false||0||true||N
InpExitTelemetryMinModifyStepPoints=$modifyStepPoints||0||1||1000||N
InpSignalTimeframe=$timeframeInput||0||0||49153||N
InpRiskPercentPerTrade=$risk||0.5||0.050000||5.000000||N
InpMaxDailyLossPercent=1.00||2.0||0.200000||20.000000||N
InpMaxWeeklyLossPercent=3.00||5.0||0.500000||50.000000||N
InpMaxTotalDrawdownPercent=10.00||20.0||2.000000||200.000000||N
InpMaxOpenOrders=1||1||1||10||N
InpMaxSpreadPoints=$($defaults.MaxSpread)||25||1||250||N
InpMaxLosingStreak=4||4||1||40||N
InpRiskGateMode=$riskGateMode
InpLosingStreakCooldownBars=$cooldownBars||24||1||240||N
InpEquityKillSwitchPercent=15.00||30.0||3.000000||300.000000||N
InpMinLot=0.01||0.01||0.001000||0.100000||N
InpMaxLot=$($defaults.MaxLot)||2.0||0.200000||20.000000||N
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
InpTrendAtrStop=2.0||2.0||0.200000||20.000000||N
InpTrendRewardRisk=2.0||2.0||0.200000||20.000000||N
InpTrendPullbackEmaPeriod=20||20||1||200||N
InpBreakoutLookbackBars=24||24||1||240||N
InpBreakoutAtrBuffer=0.15||0.15||0.015000||1.500000||N
InpBreakoutAtrStop=1.8||1.8||0.180000||18.000000||N
InpBreakoutRewardRisk=1.8||1.8||0.180000||18.000000||N
InpMeanRevAtrStop=1.5||1.5||0.150000||15.000000||N
InpMeanRevRewardRisk=1.2||1.2||0.120000||12.000000||N
InpMeanRevRsiBuyMax=35.0||35.0||3.500000||350.000000||N
InpMeanRevRsiSellMin=65.0||65.0||6.500000||650.000000||N
InpRsiPeriod=14||14||1||140||N
InpUseTrailingStop=$useTrailingStop||false||0||true||N
InpManagePositionsOnlyOnNewBar=false||false||0||true||N
InpTrailingAtrMultiplier=$trailingMultiplier||1.5||0.150000||15.000000||N
InpEnablePriceActionFibo=$enablePriceActionFibo||false||0||true||N
InpPriceActionFiboDiagnosticsOnly=$pafDiagnosticsOnly||false||0||true||N
InpPAFEntryTimeframe=$pafEntryTimeframe||0||0||49153||N
InpPAFHigherTimeframe=$pafHigherTimeframe||0||0||49153||N
InpPAFUsePendingOrders=$pafUsePendingOrders||false||0||true||N
InpPAFMaxPendingOrders=$pafMaxPendingOrders||0||1||10||N
InpPAFLogOnlyOnNewBar=$pafLogOnlyOnNewBar||false||0||true||N
"@
    $iniPath = Join-Path $CaseDir "generated_tester.ini"
    $ini | Set-Content -LiteralPath $iniPath -Encoding ASCII
    return [pscustomobject]@{ IniPath = $iniPath; PresetPath = $presetPath }
}

function Invoke-Case {
    param(
        [object]$Case,
        [string]$Phase,
        [object]$Period,
        [string]$RunId,
        [string]$RunRoot
    )

    $caseId = "$($Case.case_id)_$Phase"
    $caseDir = Join-Path $RunRoot $caseId
    New-Item -ItemType Directory -Force -Path $caseDir | Out-Null
    $runnerLog = Join-Path $caseDir "runner.log"
    $statusPath = Join-Path $caseDir "status.json"

    $caseRecord = [ordered]@{
        run_id = $RunId
        case_id = $caseId
        base_case_id = $Case.case_id
        phase = $Phase
        actual_symbol = $Case.actual_symbol
        canonical_symbol = $Case.canonical_symbol
        timeframe = $Case.timeframe
        period = $Period
        deposit = $Case.deposit
        risk_percent = $Case.risk_percent
        exit_variant = Get-CasePropertyValue -Case $Case -Name "exit_variant" -Default ""
        risk_gate_variant = Get-CasePropertyValue -Case $Case -Name "risk_gate_variant" -Default ""
        risk_gate_mode = Get-CasePropertyValue -Case $Case -Name "risk_gate_mode" -Default "NORMAL"
        losing_streak_cooldown_bars = Get-CasePropertyValue -Case $Case -Name "losing_streak_cooldown_bars" -Default 24
        use_trailing_stop = Get-CasePropertyValue -Case $Case -Name "use_trailing_stop" -Default $true
        trailing_atr_multiplier = Get-CasePropertyValue -Case $Case -Name "trailing_atr_multiplier" -Default 1.5
        diagnostic_only = Get-CasePropertyValue -Case $Case -Name "diagnostic_only" -Default $false
        enable_price_action_fibo = Get-CasePropertyValue -Case $Case -Name "enable_price_action_fibo" -Default $false
        price_action_fibo_diagnostics_only = Get-CasePropertyValue -Case $Case -Name "price_action_fibo_diagnostics_only" -Default $true
        paf_use_pending_orders = Get-CasePropertyValue -Case $Case -Name "paf_use_pending_orders" -Default $false
        paf_max_pending_orders = Get-CasePropertyValue -Case $Case -Name "paf_max_pending_orders" -Default 0
        paf_log_only_on_new_bar = Get-CasePropertyValue -Case $Case -Name "paf_log_only_on_new_bar" -Default $true
        manage_existing_positions = Get-CasePropertyValue -Case $Case -Name "manage_existing_positions" -Default $true
    }
    $caseRecord | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $caseDir "case.json") -Encoding UTF8

    $safeCaseId = ($caseId -replace "[^A-Za-z0-9_]+", "_")
    $eaLogFile = "ForexAiTrade_${RunId}_${safeCaseId}.log"
    $exitTelemetryFile = "ForexAiTrade_ExitTelemetry_${RunId}_${safeCaseId}.csv"
    $caseReportBasePath = Join-Path $caseDir "mt5_report"
    $reportRequestPath = $caseReportBasePath
    $reportSearchBasePath = $caseReportBasePath
    if (-not [string]::IsNullOrWhiteSpace($TerminalDataFolder)) {
        $relativeReportBase = Join-Path (Join-Path "ForexAiTradeResearch" $RunId) (Join-Path $safeCaseId "mt5_report")
        $terminalReportBase = Join-Path $TerminalDataFolder $relativeReportBase
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $terminalReportBase) | Out-Null
        $reportRequestPath = $relativeReportBase
        $reportSearchBasePath = $terminalReportBase
    }
    $reportSearchLocations = @($reportSearchBasePath)
    if (-not $reportSearchBasePath.Equals($caseReportBasePath, [System.StringComparison]::OrdinalIgnoreCase)) {
        $reportSearchLocations += $caseReportBasePath
    }

    $reportPreflightMarkerPath = ""
    $reportPreflightMarkerTimestamp = ""
    $reportPreflightMarkerError = ""
    if (-not [string]::IsNullOrWhiteSpace($TerminalDataFolder)) {
        $reportPreflightMarkerTimestamp = (Get-Date).ToString("o")
        $reportPreflightMarkerPath = Join-Path (Split-Path -Parent $reportSearchBasePath) "report_preflight_marker.txt"
        try {
            @(
                "run_id=$RunId",
                "case_id=$caseId",
                "safe_case_id=$safeCaseId",
                "report_request_path=$reportRequestPath",
                "terminal_report_base_path=$reportSearchBasePath",
                "created_at=$reportPreflightMarkerTimestamp"
            ) | Set-Content -LiteralPath $reportPreflightMarkerPath -Encoding UTF8
        }
        catch {
            $reportPreflightMarkerError = $_.Exception.Message
        }
    }
    $generated = New-TesterConfig -Case $Case -Phase $Phase -Period $Period -RunId $RunId -CaseId $caseId -CaseDir $caseDir -ReportBasePath $reportRequestPath -EaLogFile $eaLogFile -ExitTelemetryFile $exitTelemetryFile

    $processInfoPath = Join-Path $caseDir "process_info.json"
    $status = @{
        execution_status = "FAILED"
        message = ""
        run_id = $RunId
        case_id = $caseId
        report_path = $caseReportBasePath
        report_request_path = $reportRequestPath
        report_search_base_path = $reportSearchBasePath
        report_search_locations = $reportSearchLocations
        terminal_report_base_path = $reportSearchBasePath
        terminal_report_path = $null
        copied_report_path = $null
        report_artifact_status = "PENDING"
        report_companion_files = @()
        report_preflight_marker_path = $reportPreflightMarkerPath
        report_preflight_marker_timestamp = $reportPreflightMarkerTimestamp
        report_preflight_marker_error = $reportPreflightMarkerError
        report_found_after_run_start = $false
        stale_report_detected = $false
        stale_report_paths = @()
    }

    Write-RunnerLog -Path $runnerLog -Message "WARNING: This runner starts and controls only its own MT5 process. It will never bulk-kill terminal64 processes."
    Write-RunnerLog -Path $runnerLog -Message "Case start: $caseId"
    if (-not [string]::IsNullOrWhiteSpace($reportPreflightMarkerError)) {
        $status.execution_status = "PROCESS_ERROR"
        $status.message = "Report preflight marker could not be written: $reportPreflightMarkerError"
        Write-Status -Path $statusPath -Status $status
        return [pscustomobject]$status
    }

    $args = @("/config:`"$($generated.IniPath)`"")
    if ($UsePortableMode) {
        $args += "/portable"
    }

    $startTime = Get-Date
    $preExistingReportArtifacts = @(Resolve-ReportArtifacts -BasePath $reportSearchBasePath)
    $staleReportArtifacts = @($preExistingReportArtifacts | Where-Object { $_.LastWriteTime -lt $startTime })
    $status.stale_report_detected = [bool]($staleReportArtifacts.Count -gt 0)
    $status.stale_report_paths = @($staleReportArtifacts | ForEach-Object { $_.FullName })
    $process = $null
    try {
        $process = Start-Process -FilePath $TerminalExe -ArgumentList $args -WindowStyle Hidden -PassThru
        if ($null -eq $process -or $process.Id -le 0) {
            throw "Start-Process did not return a dedicated process."
        }

        @{
            process_id = $process.Id
            terminal_exe = $TerminalExe
            use_portable_mode = [bool]$UsePortableMode
            start_time = $startTime.ToString("o")
        } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $processInfoPath -Encoding UTF8

        Write-RunnerLog -Path $runnerLog -Message "Spawned MT5 PID $($process.Id)"
    }
    catch {
        $status.execution_status = "PROCESS_ERROR"
        $status.message = $_.Exception.Message
        Write-Status -Path $statusPath -Status $status
        return [pscustomobject]$status
    }

    $deadline = (Get-Date).AddMinutes($CaseTimeoutMinutes)
    $completedByLog = $false
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds $PollIntervalSeconds
        try {
            $process.Refresh()
            if ($process.HasExited) {
                Write-RunnerLog -Path $runnerLog -Message "Process exited with code $($process.ExitCode)"
                break
            }
        }
        catch {
            Write-RunnerLog -Path $runnerLog -Message "Unable to refresh process: $($_.Exception.Message)"
            break
        }

        $logRoots = @()
        if ($TerminalDataFolder) { $logRoots += (Join-Path $TerminalDataFolder "logs") }
        if ($TesterRootFolder) { $logRoots += $TesterRootFolder }
        $logRoots += (Join-Path $env:APPDATA "MetaQuotes\Tester")
        $candidateLogs = Find-UpdatedLogs -Roots $logRoots -Since $startTime
        foreach ($log in $candidateLogs | Select-Object -First 5) {
            $tail = Read-TextFileSafe -Path $log.FullName | Select-Object -Last 200
            $joined = $tail -join "`n"
            if ($joined -match "test Experts\\(?:ForexAiTrade\\)?ForexAiTrade\.ex5 on $([regex]::Escape($Case.actual_symbol)),$($Case.timeframe) thread finished" -or
                $joined -match "Test passed") {
                $completedByLog = $true
                break
            }
        }
        if ($completedByLog) {
            Write-RunnerLog -Path $runnerLog -Message "Tester completion detected in updated log."
            break
        }
    }

    $timedOut = (Get-Date) -ge $deadline
    if ($timedOut) {
        $status.execution_status = "TIMEOUT"
        $status.message = "Case timed out after $CaseTimeoutMinutes minute(s)."
        Write-RunnerLog -Path $runnerLog -Message $status.message
        try {
            $process.Refresh()
            if (-not $process.HasExited) {
                Write-RunnerLog -Path $runnerLog -Message "Stopping only spawned PID $($process.Id)."
                Stop-Process -Id $process.Id -Force
            }
        }
        catch {
            Write-RunnerLog -Path $runnerLog -Message "Failed stopping spawned PID only: $($_.Exception.Message)"
        }
    }
    elseif (-not $KeepTerminalOpen) {
        try {
            $process.Refresh()
            if (-not $process.HasExited) {
                $preCloseReport = Wait-ReportPath -BasePath $reportSearchBasePath -TimeoutSeconds ([Math]::Max(30, $PollIntervalSeconds * 15)) -PollIntervalSeconds $PollIntervalSeconds -NotBefore $startTime
                if ($preCloseReport) {
                    Write-RunnerLog -Path $runnerLog -Message "Report detected before closing spawned PID $($process.Id)."
                }
                else {
                    Write-RunnerLog -Path $runnerLog -Message "Report not detected before close wait; closing only spawned PID $($process.Id)."
                }
                Write-RunnerLog -Path $runnerLog -Message "Closing only spawned PID $($process.Id)."
                $null = $process.CloseMainWindow()
            }
        }
        catch {
            Write-RunnerLog -Path $runnerLog -Message "CloseMainWindow failed for spawned PID: $($_.Exception.Message)"
        }
    }

    $updatedLogs = Find-UpdatedLogs -Roots @(
        $(if ($TerminalDataFolder) { Join-Path $TerminalDataFolder "logs" }),
        $(if ($TesterRootFolder) { $TesterRootFolder }),
        (Join-Path $env:APPDATA "MetaQuotes\Tester")
    ) -Since $startTime
    $excerptPath = Join-Path $caseDir "tester_log_excerpt.log"
    $excerpt = @()
    foreach ($log in $updatedLogs | Select-Object -First 3) {
        $excerpt += "===== $($log.FullName) ====="
        $excerpt += Read-TextFileSafe -Path $log.FullName | Select-Object -Last 400
    }
    $excerpt | Set-Content -LiteralPath $excerptPath -Encoding UTF8

    $commonEaLog = Join-Path (Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files") $eaLogFile
    $caseEaLog = Join-Path $caseDir "ea_mirror.log"
    if (Test-Path -LiteralPath $commonEaLog -PathType Leaf) {
        Copy-Item -LiteralPath $commonEaLog -Destination $caseEaLog -Force
    }

    $commonExitTelemetry = Join-Path (Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files") $exitTelemetryFile
    $caseExitTelemetry = Join-Path $caseDir "exit_telemetry.csv"
    if (Test-Path -LiteralPath $commonExitTelemetry -PathType Leaf) {
        Copy-Item -LiteralPath $commonExitTelemetry -Destination $caseExitTelemetry -Force
    }

    if ($status.execution_status -eq "TIMEOUT") {
        Write-Status -Path $statusPath -Status $status
        return [pscustomobject]$status
    }

    $reportPath = Wait-ReportPath -BasePath $reportSearchBasePath -TimeoutSeconds ([Math]::Max(10, $PollIntervalSeconds * 10)) -PollIntervalSeconds $PollIntervalSeconds -NotBefore $startTime
    if (-not $reportPath) {
        if ($completedByLog -or (Test-Path -LiteralPath $caseEaLog -PathType Leaf)) {
            $status.execution_status = "PARTIAL_TESTER_PASS_REPORT_MISSING"
            $status.message = "Tester or EA log artifact was produced, but MT5 report file was not created after run start."
            $status.report_artifact_status = "MISSING_AFTER_TESTER_LOG"
        }
        else {
            $status.execution_status = "FAILED_NO_TESTER_ARTIFACTS"
            $status.message = "MT5 report file was not created and no tester/EA artifact confirmed execution."
            $status.report_artifact_status = "MISSING_NO_TESTER_ARTIFACTS"
        }
        Write-Status -Path $statusPath -Status $status
        return [pscustomobject]$status
    }
    $status.terminal_report_path = $reportPath
    $status.report_found_after_run_start = $true
    $status.report_artifact_status = "FOUND"
    $reportArtifacts = @(Resolve-ReportArtifacts -BasePath $reportSearchBasePath -NotBefore $startTime)
    $copiedArtifacts = @()
    if ($reportPath -ne $caseReportBasePath -and -not $reportPath.StartsWith($caseDir, [System.StringComparison]::OrdinalIgnoreCase)) {
        $copiedArtifacts = @(Copy-ReportArtifacts -SourceBasePath $reportSearchBasePath -TargetBasePath $caseReportBasePath -NotBefore $startTime)
        $suffix = ""
        if ($reportPath.StartsWith($reportSearchBasePath, [System.StringComparison]::OrdinalIgnoreCase)) {
            $suffix = $reportPath.Substring($reportSearchBasePath.Length)
        }
        if ([string]::IsNullOrWhiteSpace($suffix)) {
            $suffix = [System.IO.Path]::GetExtension($reportPath)
        }
        $targetReport = "$caseReportBasePath$suffix"
        if (Test-Path -LiteralPath $targetReport -PathType Leaf) {
            $reportPath = $targetReport
        }
    }
    else {
        $copiedArtifacts = @($reportArtifacts | ForEach-Object { $_.FullName })
    }
    $status.report_path = $reportPath
    $status.copied_report_path = $reportPath
    $status.report_companion_files = @($copiedArtifacts | Where-Object { $_ -ne $reportPath })

    if (-not (Test-FileStable -Path $reportPath -Polls 3 -Seconds $PollIntervalSeconds)) {
        $status.execution_status = "FAILED"
        $status.message = "Report did not become stable."
        Write-Status -Path $statusPath -Status $status
        return [pscustomobject]$status
    }

    $parsedPath = Join-Path $caseDir "parsed_result.json"
    $parser = Join-Path $repoRoot "tools\research_report_parser.py"
    $caseJson = Join-Path $caseDir "case.json"
    $parseResult = & python $parser --report $reportPath --case $caseJson --output $parsedPath 2>&1
    if ($LASTEXITCODE -ne 0) {
        $status.execution_status = "PARSE_ERROR"
        $status.message = ($parseResult -join "`n")
        Write-Status -Path $statusPath -Status $status
        return [pscustomobject]$status
    }

    $parsed = Get-Content -LiteralPath $parsedPath -Raw | ConvertFrom-Json
    if ($parsed.metadata_match -eq $false) {
        $status.execution_status = "CONFIG_MISMATCH"
        $status.message = "Report metadata does not match requested case."
    }
    else {
        $status.execution_status = "PASS"
        $status.message = "Completed with parseable report."
    }

    Invoke-PafDiagnosticsParser -CaseDir $caseDir -Status $status -Case $Case

    Write-Status -Path $statusPath -Status $status
    return [pscustomobject]$status
}

if (-not (Test-Path -LiteralPath $matrixPath -PathType Leaf)) {
    throw "Research matrix not found: $matrixPath"
}
if (-not (Test-Path -LiteralPath $TerminalExe -PathType Leaf)) {
    throw "TerminalExe not found: $TerminalExe"
}

Write-Host "STRONG WARNING:" -ForegroundColor Yellow
Write-Host "Use a dedicated MT5 research installation or portable terminal. Do not use a terminal connected to live trading." -ForegroundColor Yellow
Write-Host "This runner controls only PIDs it starts and will fail safely if it cannot identify a spawned process." -ForegroundColor Yellow

$matrix = Get-Content -LiteralPath $matrixPath -Raw | ConvertFrom-Json
$runId = "run_" + (Get-Date -Format "yyyyMMdd_HHmmss")
$runRoot = Join-Path $outputRootPath $runId
New-Item -ItemType Directory -Force -Path $runRoot | Out-Null

$periodNames = @("train", "validation", "out_of_sample")
$selectedCases = @($matrix.cases | Where-Object { $_.enabled -ne $false })
if ($IntegrationOnly) {
    $ids = @($matrix.integration_cases)
    $selectedCases = @($selectedCases | Where-Object { $ids -contains $_.case_id })
    $periodNames = @("out_of_sample")
}
$requestedCaseIds = @()
if (-not [string]::IsNullOrWhiteSpace($CaseId)) {
    $requestedCaseIds += $CaseId
}
$requestedCaseIds += $CaseIds
$requestedCaseIds = Normalize-PhaseList -Values $requestedCaseIds
if ($requestedCaseIds.Count -gt 0) {
    $selectedCases = @($selectedCases | Where-Object { $requestedCaseIds -contains $_.case_id })
    if ($selectedCases.Count -eq 0) {
        throw "No requested CaseId values were found or enabled in research matrix: $($requestedCaseIds -join ',')"
    }
    $foundCaseIds = @($selectedCases | ForEach-Object { $_.case_id })
    $missingCaseIds = @($requestedCaseIds | Where-Object { $foundCaseIds -notcontains $_ })
    if ($missingCaseIds.Count -gt 0) {
        throw "Requested CaseId values were not found or are disabled in research matrix: $($missingCaseIds -join ',')"
    }
}
$requestedPhases = Normalize-PhaseList -Values $Phases
if ($requestedPhases.Count -gt 0) {
    $periodNames = @($requestedPhases)
}
foreach ($phaseName in $periodNames) {
    if ($null -eq $matrix.periods.$phaseName) {
        throw "Phase not found in research matrix periods: $phaseName"
    }
}

$statuses = @()
foreach ($case in $selectedCases) {
    foreach ($phase in $periodNames) {
        $period = $matrix.periods.$phase
        $attempt = 0
        do {
            $status = Invoke-Case -Case $case -Phase $phase -Period $period -RunId $runId -RunRoot $runRoot
            $statuses += $status
            $infraRetry = @("TIMEOUT", "NO_REPORT", "PARTIAL_TESTER_PASS_REPORT_MISSING", "FAILED_NO_TESTER_ARTIFACTS", "PARSE_ERROR", "PROCESS_ERROR") -contains $status.execution_status
            $attempt++
        } while ($infraRetry -and $attempt -le $RetryCount)
    }
}

$statuses | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $runRoot "run_status.json") -Encoding UTF8

$pafSummaryTool = Join-Path $repoRoot "tools\paf_diagnostic_parser.py"
if (Test-Path -LiteralPath $pafSummaryTool -PathType Leaf) {
    $pafCases = @($selectedCases | Where-Object {
        [System.Convert]::ToBoolean((Get-CasePropertyValue -Case $_ -Name "enable_price_action_fibo" -Default $false)) -and
        [System.Convert]::ToBoolean((Get-CasePropertyValue -Case $_ -Name "price_action_fibo_diagnostics_only" -Default $true))
    })
    if ($pafCases.Count -gt 0) {
        $pafSummaryResult = & python $pafSummaryTool --runs-root $outputRootPath --results-root (Join-Path $repoRoot "research\results") --run-id $runId 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to generate PAF diagnostic summary: $($pafSummaryResult -join "`n")"
        }
    }
}

$summaryPath = Join-Path $runRoot "research_summary_for_run.md"
$summaryTool = Join-Path $repoRoot "tools\generate_research_summary.py"
if (Test-Path -LiteralPath $summaryTool -PathType Leaf) {
    $summaryResult = & python $summaryTool --runs-root $outputRootPath --results-root (Join-Path $repoRoot "research\results") --run-id $runId --summary-output $summaryPath 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Failed to generate run summary: $($summaryResult -join "`n")"
    }
}

if ($IntegrationOnly) {
    $summary = @()
    $summary += "# Integration Test Summary"
    $summary += ""
    $summary += "RunId: $runId"
    $summary += ""
    $summary += "| Case | Status | Message |"
    $summary += "|---|---|---|"
    foreach ($s in $statuses) {
        $summary += "| $($s.case_id) | $($s.execution_status) | $($s.message -replace '\|', '/') |"
    }
    $summary += ""
    $summary += "This integration test validates runner isolation and artifact creation only. It is not profitability proof."
    $summary | Set-Content -LiteralPath (Join-Path $runRoot "integration_test_summary.md") -Encoding UTF8
}

Write-Host "Run root: $runRoot" -ForegroundColor Green
