#ifndef FOREX_AI_TRADE_INPUTS_MQH
#define FOREX_AI_TRADE_INPUTS_MQH

input group "Safety"
input bool   InpLiveTradingEnabled       = false;
input bool   InpDemoSafeMode             = true;
input long   InpMagicNumber              = 26061901;
input int    InpSlippagePoints           = 20;
input bool   InpTradeOnlyOnNewBar        = true;
input bool   InpManageExistingPositions  = false;
input bool   InpRequireStrategyTester    = false;

input group "Broker Symbol Handling"
input string InpAllowedSymbolsCsv        = "";
input string InpCanonicalSymbolName      = "";
input string InpBrokerGoldSymbolName     = "GOLDm#";
input bool   InpPrintSymbolDiagnostics   = true;

input group "Logging"
input bool   InpMirrorLogsToFile         = false;
input bool   InpMirrorLogsUseCommonFolder = true;
input string InpMirrorLogFileName        = "ForexAiTrade_smoke.log";
input bool   InpEnableExitTelemetry      = false;
input string InpExitTelemetryFileName    = "";
input bool   InpLogPositionModifyEvents  = false;
input bool   InpLogRMultipleOnClose      = true;
input double InpExitTelemetryMinModifyStepPoints = 0.0;

input group "Timeframes"
input ENUM_TIMEFRAMES InpSignalTimeframe = PERIOD_H1;

input group "Risk"
input double InpRiskPercentPerTrade      = 0.50;
input double InpMaxDailyLossPercent      = 2.00;
input double InpMaxWeeklyLossPercent     = 5.00;
input double InpMaxTotalDrawdownPercent  = 20.00;
input int    InpMaxOpenOrders            = 1;
input int    InpMaxSpreadPoints          = 25;
input int    InpMaxLosingStreak          = 4;
input string InpRiskGateMode             = "NORMAL";
input int    InpLosingStreakCooldownBars = 24;
input double InpEquityKillSwitchPercent  = 30.00;
input double InpMinLot                   = 0.01;
input double InpMaxLot                   = 2.00;

input group "Regime Detector"
input int    InpAdxPeriod                = 14;
input double InpTrendAdxMin              = 22.0;
input double InpSidewayAdxMax            = 18.0;
input int    InpAtrPeriod                = 14;
input double InpMinAtrPercent            = 0.03;
input double InpMaxAtrPercent            = 0.80;
input int    InpEmaFastPeriod            = 50;
input int    InpEmaSlowPeriod            = 200;
input double InpTrendSlopeMinPoints      = 8.0;
input int    InpBandsPeriod              = 20;
input double InpBandsDeviation           = 2.0;
input double InpBreakoutBbWidthMinPct    = 0.20;
input double InpSidewayBbWidthMaxPct     = 0.18;

input group "Trend Following"
input double InpTrendAtrStop             = 2.0;
input double InpTrendRewardRisk          = 2.0;
input int    InpTrendPullbackEmaPeriod   = 20;

input group "Breakout"
input int    InpBreakoutLookbackBars     = 24;
input double InpBreakoutAtrBuffer        = 0.15;
input double InpBreakoutAtrStop          = 1.8;
input double InpBreakoutRewardRisk       = 1.8;

input group "Mean Reversion"
input double InpMeanRevAtrStop           = 1.5;
input double InpMeanRevRewardRisk        = 1.2;
input double InpMeanRevRsiBuyMax         = 35.0;
input double InpMeanRevRsiSellMin        = 65.0;
input int    InpRsiPeriod                = 14;

input group "Price Action / Fibo Skeleton"
input bool   InpEnablePriceActionFibo    = false;
input bool   InpPriceActionFiboDiagnosticsOnly = true;
input ENUM_TIMEFRAMES InpPAFEntryTimeframe = PERIOD_H1;
input ENUM_TIMEFRAMES InpPAFHigherTimeframe = PERIOD_H1;
input bool   InpPAFUsePendingOrders      = false;
input int    InpPAFMaxPendingOrders      = 0;
input int    InpPAFMaxOpenOrders         = 1;

input group "Position Management"
input bool   InpUseTrailingStop          = true;
input bool   InpManagePositionsOnlyOnNewBar = false;
input double InpTrailingAtrMultiplier    = 1.5;

#endif
