#property copyright "ForexAiTrade"
#property version   "1.00"
#property strict

#include <Trade/Trade.mqh>
#include "../../Include/ForexAiTrade/Types.mqh"
#include "../../Include/ForexAiTrade/Inputs.mqh"
#include "../../Include/ForexAiTrade/TradeLogger.mqh"
#include "../../Include/ForexAiTrade/SymbolHelper.mqh"
#include "../../Include/ForexAiTrade/MarketData.mqh"
#include "../../Include/ForexAiTrade/RiskManager.mqh"
#include "../../Include/ForexAiTrade/ExitTelemetry.mqh"
#include "../../Include/ForexAiTrade/RegimeDetector.mqh"
#include "../../Include/ForexAiTrade/Strategies/TrendFollowing.mqh"
#include "../../Include/ForexAiTrade/Strategies/Breakout.mqh"
#include "../../Include/ForexAiTrade/Strategies/MeanReversion.mqh"
#include "../../Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh"

CTrade             g_trade;
CMarketData        g_market;
CRiskManager       g_risk;
CRegimeDetector    g_regime;
CTrendFollowing    g_trend;
CBreakoutStrategy  g_breakout;
CMeanReversion     g_meanReversion;
CPriceActionFiboStrategy g_priceActionFibo;
CTradeLogger       g_logger;
CExitTelemetry     g_exitTelemetry;

datetime g_lastBarTime = 0;

void LogLine(const string message)
{
   Print(message);
   g_logger.Write(message);
}

string RegimeName(const EMarketRegime regime)
{
   if(regime == REGIME_TREND)
      return "trend";
   if(regime == REGIME_BREAKOUT)
      return "breakout";
   if(regime == REGIME_SIDEWAY)
      return "sideway";
   return "unsafe";
}

string DirectionName(const ESignalDirection direction)
{
   if(direction == SIGNAL_BUY)
      return "buy";
   if(direction == SIGNAL_SELL)
      return "sell";
   return "none";
}

string TimeframeName(const ENUM_TIMEFRAMES timeframe)
{
   return EnumToString(timeframe);
}

bool IsNewBar()
{
   datetime currentBar = iTime(_Symbol, InpSignalTimeframe, 0);
   if(currentBar <= 0)
      return false;

   if(currentBar == g_lastBarTime)
      return false;

   g_lastBarTime = currentBar;
   return true;
}

void PrintSymbolDiagnostics(const SSymbolMetadata &metadata)
{
   if(!InpPrintSymbolDiagnostics)
      return;

   LogLine("Symbol diagnostics: actual=" + metadata.actualSymbol +
           " canonical=" + metadata.canonicalSymbol +
           " digits=" + IntegerToString(metadata.digits) +
           " point=" + DoubleToString(metadata.point, 10) +
           " tick_size=" + DoubleToString(metadata.tickSize, 10) +
           " tick_value=" + DoubleToString(metadata.tickValue, 5) +
           " contract_size=" + DoubleToString(metadata.contractSize, 2) +
           " min_lot=" + DoubleToString(metadata.volumeMin, 2) +
           " max_lot=" + DoubleToString(metadata.volumeMax, 2) +
           " lot_step=" + DoubleToString(metadata.volumeStep, 2) +
           " stops_level=" + IntegerToString(metadata.stopsLevel) +
           " freeze_level=" + IntegerToString(metadata.freezeLevel) +
           " trade_mode=" + IntegerToString(metadata.tradeMode) +
           " spread=" + DoubleToString(metadata.spreadPoints, 1) +
           " valid=" + (metadata.valid ? "true" : "false") +
           " reason=" + metadata.reason);
}

bool HasOpenPositionForThisEA()
{
   for(int i = PositionsTotal() - 1; i >= 0; --i)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;

      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         (long)PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
      {
         return true;
      }
   }

   return false;
}

string NormalizedRiskGateMode()
{
   string mode = InpRiskGateMode;
   StringToUpper(mode);
   return mode;
}

bool IsDiagnosticRiskGateMode()
{
   return StringFind(NormalizedRiskGateMode(), "DIAGNOSTIC_") == 0;
}

bool CanModifyExistingPosition(const SSymbolMetadata &metadata, string &reason)
{
   if(IsDiagnosticRiskGateMode() && !MQLInfoInteger(MQL_TESTER))
   {
      reason = "diagnostic risk gate mode requires Strategy Tester";
      return false;
   }

   if(InpRequireStrategyTester && !MQLInfoInteger(MQL_TESTER))
   {
      reason = "strategy tester required by preset";
      return false;
   }

   if(!InpManageExistingPositions)
   {
      reason = "InpManageExistingPositions=false";
      return false;
   }

   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED))
   {
      reason = "TERMINAL_TRADE_ALLOWED is false";
      return false;
   }

   if(!MQLInfoInteger(MQL_TRADE_ALLOWED))
   {
      reason = "MQL_TRADE_ALLOWED is false";
      return false;
   }

   if(!AccountInfoInteger(ACCOUNT_TRADE_ALLOWED))
   {
      reason = "ACCOUNT_TRADE_ALLOWED is false";
      return false;
   }

   if(!metadata.valid)
   {
      reason = "invalid symbol metadata: " + metadata.reason;
      return false;
   }

   if(metadata.tradeMode == SYMBOL_TRADE_MODE_DISABLED)
   {
      reason = "SYMBOL_TRADE_MODE is disabled";
      return false;
   }

   reason = "ok";
   return true;
}

void ManageOpenPositions(const SSymbolMetadata &metadata)
{
   string modifyReason = "";
   if(!CanModifyExistingPosition(metadata, modifyReason))
   {
      LogLine("Position management block: " + modifyReason);
      return;
   }

   if(!InpUseTrailingStop)
      return;

   double atr = g_market.ATR(1);
   if(atr <= 0.0)
      return;

   for(int i = PositionsTotal() - 1; i >= 0; --i)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;

      if(PositionGetString(POSITION_SYMBOL) != _Symbol ||
         (long)PositionGetInteger(POSITION_MAGIC) != InpMagicNumber)
      {
         continue;
      }

      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double currentSl = PositionGetDouble(POSITION_SL);
      double currentTp = PositionGetDouble(POSITION_TP);
      double bid = SymbolInfoDouble(metadata.actualSymbol, SYMBOL_BID);
      double ask = SymbolInfoDouble(metadata.actualSymbol, SYMBOL_ASK);
      double trailDistance = atr * InpTrailingAtrMultiplier;

      if(type == POSITION_TYPE_BUY)
      {
         double newSl = NormalizeDouble(bid - trailDistance, metadata.digits);
         double minDistance = MathMax(metadata.stopsLevel, metadata.freezeLevel) * metadata.point;
         if(newSl > openPrice && (currentSl == 0.0 || newSl > currentSl) &&
            (minDistance <= 0.0 || MathAbs(bid - newSl) >= minDistance))
         {
            if(g_trade.PositionModify(ticket, newSl, currentTp))
            {
               ulong positionId = (ulong)PositionGetInteger(POSITION_IDENTIFIER);
               g_exitTelemetry.LogPositionModify(ticket, positionId, "trailing", currentSl, newSl, currentTp, currentTp, bid);
            }
         }
      }
      else if(type == POSITION_TYPE_SELL)
      {
         double newSl = NormalizeDouble(ask + trailDistance, metadata.digits);
         double minDistance = MathMax(metadata.stopsLevel, metadata.freezeLevel) * metadata.point;
         if(newSl < openPrice && (currentSl == 0.0 || newSl < currentSl) &&
            (minDistance <= 0.0 || MathAbs(ask - newSl) >= minDistance))
         {
            if(g_trade.PositionModify(ticket, newSl, currentTp))
            {
               ulong positionId = (ulong)PositionGetInteger(POSITION_IDENTIFIER);
               g_exitTelemetry.LogPositionModify(ticket, positionId, "trailing", currentSl, newSl, currentTp, currentTp, ask);
            }
         }
      }
   }
}

void PrintSignalLog(const string stage,
                    const STradeSignal &signal,
                    const SRegimeState &regime,
                    const SSymbolMetadata &metadata,
                    const double entry,
                    const SPositionSizeResult &size,
                    const string reason)
{
   LogLine("Signal " + stage +
           ": actual=" + metadata.actualSymbol +
           " canonical=" + metadata.canonicalSymbol +
           " timeframe=" + TimeframeName(InpSignalTimeframe) +
           " regime=" + RegimeName(regime.regime) +
           " direction=" + DirectionName(signal.direction) +
           " entry=" + DoubleToString(entry, metadata.digits) +
           " sl=" + DoubleToString(signal.stopLoss, metadata.digits) +
           " tp=" + DoubleToString(signal.takeProfit, metadata.digits) +
           " raw_lot=" + DoubleToString(size.rawLots, 4) +
           " normalized_lot=" + DoubleToString(size.lots, 2) +
           " risk_money=" + DoubleToString(size.riskMoney, 2) +
           " actual_risk_money=" + DoubleToString(size.actualRiskMoney, 2) +
           " reason=" + reason);
}

void PrintNoTradeLog(const string reason, const SRegimeState &regime, const SSymbolMetadata &metadata)
{
   LogLine("No trade: actual=" + metadata.actualSymbol +
           " canonical=" + metadata.canonicalSymbol +
           " timeframe=" + TimeframeName(InpSignalTimeframe) +
           " regime=" + RegimeName(regime.regime) +
           " spread=" + DoubleToString(metadata.spreadPoints, 1) +
           " reason=" + reason);
}

void ExecuteSignal(const STradeSignal &signal, const SRegimeState &regime, const SSymbolMetadata &metadata)
{
   if(signal.direction == SIGNAL_NONE)
      return;

   SPositionSizeResult emptySize;
   emptySize.valid = false;
   emptySize.lots = 0.0;
   emptySize.rawLots = 0.0;
   emptySize.riskMoney = 0.0;
   emptySize.actualRiskMoney = 0.0;
   emptySize.reason = "";

   if(InpRequireStrategyTester && !MQLInfoInteger(MQL_TESTER))
   {
      PrintSignalLog("blocked", signal, regime, metadata, 0.0, emptySize, "strategy tester required by preset");
      return;
   }

   if(IsDiagnosticRiskGateMode() && !MQLInfoInteger(MQL_TESTER))
   {
      PrintSignalLog("blocked", signal, regime, metadata, 0.0, emptySize, "diagnostic risk gate mode requires Strategy Tester");
      return;
   }

   if(InpDemoSafeMode && AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL)
   {
      PrintSignalLog("blocked", signal, regime, metadata, 0.0, emptySize, "demo safe mode blocks trading on real accounts");
      return;
   }

   if(HasOpenPositionForThisEA())
   {
      PrintSignalLog("blocked", signal, regime, metadata, 0.0, emptySize, "max open orders reached");
      return;
   }

   string riskReason = "";
   if(!g_risk.CanOpenNewTrade(regime, metadata, riskReason))
   {
      PrintSignalLog("blocked", signal, regime, metadata, 0.0, emptySize, riskReason);
      return;
   }

   double entry = signal.direction == SIGNAL_BUY ? SymbolInfoDouble(metadata.actualSymbol, SYMBOL_ASK)
                                                 : SymbolInfoDouble(metadata.actualSymbol, SYMBOL_BID);
   if(entry <= 0.0 || signal.stopLoss <= 0.0 || signal.takeProfit <= 0.0)
   {
      PrintSignalLog("blocked", signal, regime, metadata, entry, emptySize, "invalid entry, SL, or TP");
      return;
   }

   SPositionSizeResult size;
   if(!g_risk.CalculatePositionSize(entry, signal.stopLoss, metadata, size))
   {
      PrintSignalLog("blocked", signal, regime, metadata, entry, size, size.reason);
      return;
   }

   string executionReason = "";
   if(!g_risk.ValidateExecutionSafety(signal.direction, size.lots, entry, signal.stopLoss, signal.takeProfit, metadata, executionReason))
   {
      PrintSignalLog("blocked", signal, regime, metadata, entry, size, executionReason);
      return;
   }

   PrintSignalLog("accepted", signal, regime, metadata, entry, size, executionReason);
   double slDistancePoints = metadata.point > 0.0 ? MathAbs(entry - signal.stopLoss) / metadata.point : 0.0;
   double tpDistancePoints = metadata.point > 0.0 ? MathAbs(signal.takeProfit - entry) / metadata.point : 0.0;
   double rTarget = slDistancePoints > 0.0 ? tpDistancePoints / slDistancePoints : 0.0;
   g_exitTelemetry.SetPendingOpen(metadata.actualSymbol,
                                  metadata.canonicalSymbol,
                                  TimeframeName(InpSignalTimeframe),
                                  signal.comment,
                                  RegimeName(regime.regime),
                                  DirectionName(signal.direction),
                                  entry,
                                  signal.stopLoss,
                                  signal.takeProfit,
                                  slDistancePoints,
                                  tpDistancePoints,
                                  size.actualRiskMoney,
                                  size.lots,
                                  metadata.spreadPoints,
                                  regime.atr,
                                  rTarget);

   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetDeviationInPoints(InpSlippagePoints);
   g_trade.SetTypeFillingBySymbol(metadata.actualSymbol);

   bool ok = false;
   if(signal.direction == SIGNAL_BUY)
      ok = g_trade.Buy(size.lots, metadata.actualSymbol, 0.0, signal.stopLoss, signal.takeProfit, signal.comment);
   else if(signal.direction == SIGNAL_SELL)
      ok = g_trade.Sell(size.lots, metadata.actualSymbol, 0.0, signal.stopLoss, signal.takeProfit, signal.comment);

   if(!ok)
   {
      g_exitTelemetry.ClearPending();
      LogLine("Order failed. Retcode=" + IntegerToString((int)g_trade.ResultRetcode()) + " " + g_trade.ResultRetcodeDescription());
   }
}

int OnInit()
{
   if(!g_market.Init(_Symbol, InpSignalTimeframe))
      return INIT_FAILED;

   if(!g_regime.Init(&g_market))
      return INIT_FAILED;

   g_risk.Init();
   g_logger.Init(InpMirrorLogsToFile, InpMirrorLogsUseCommonFolder, InpMirrorLogFileName);
   g_trend.Init(&g_market);
   g_breakout.Init(&g_market);
   g_meanReversion.Init(&g_market);
   g_priceActionFibo.Init(&g_market);

   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_lastBarTime = iTime(_Symbol, InpSignalTimeframe, 0);

   SSymbolMetadata metadata;
   CSymbolHelper::LoadMetadata(_Symbol, metadata);
   g_exitTelemetry.Init(InpEnableExitTelemetry,
                        InpMirrorLogsUseCommonFolder,
                        InpExitTelemetryFileName,
                        metadata.actualSymbol,
                        metadata.canonicalSymbol,
                        InpSignalTimeframe,
                        InpMirrorLogFileName,
                        metadata.point);
   PrintSymbolDiagnostics(metadata);
   if(!metadata.valid)
      LogLine("Symbol metadata block: " + metadata.reason);

   LogLine("ForexAiTrade initialized. DemoSafeMode=" + (InpDemoSafeMode ? "true" : "false") +
           " LiveTradingEnabled=" + (InpLiveTradingEnabled ? "true" : "false") +
           " RequireStrategyTester=" + (InpRequireStrategyTester ? "true" : "false") +
           " RiskGateMode=" + NormalizedRiskGateMode() +
           " FileLog=" + g_logger.LocationHint() +
           " ExitTelemetry=" + g_exitTelemetry.LocationHint());
   if(InpEnablePriceActionFibo)
   {
      LogLine("PriceActionFibo module loaded. DiagnosticsOnly=" +
              (InpPriceActionFiboDiagnosticsOnly ? "true" : "false") +
              " PendingOrdersEnabled=" + (InpPAFUsePendingOrders ? "true" : "false") +
              " EntryTimeframe=" + TimeframeName(InpPAFEntryTimeframe) +
              " HigherTimeframe=" + TimeframeName(InpPAFHigherTimeframe));
      if(InpPriceActionFiboDiagnosticsOnly)
         LogLine("PriceActionFibo diagnostics-only mode active. DiagnosticsEnabled=" +
                 (InpPAFDiagnosticsEnabled ? "true" : "false") +
                 " LogOnlyOnNewBar=" + (InpPAFLogOnlyOnNewBar ? "true" : "false"));
      LogLine("PriceActionFibo safety: skeleton placeholder only; no market orders, pending orders, or position modifications are active.");
   }
   if(InpRequireStrategyTester && !MQLInfoInteger(MQL_TESTER))
      LogLine("Safety block: strategy tester required by preset");
   if(IsDiagnosticRiskGateMode() && !MQLInfoInteger(MQL_TESTER))
      LogLine("Safety block: diagnostic risk gate mode requires Strategy Tester");
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   LogLine("ForexAiTrade deinitialized. reason=" + IntegerToString(reason));
   g_exitTelemetry.Release();
   g_logger.Release();
   g_market.Release();
}

void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
   g_exitTelemetry.OnTradeTransaction(trans);
}

void OnTick()
{
   g_risk.Update();

   SSymbolMetadata metadata;
   CSymbolHelper::LoadMetadata(_Symbol, metadata);

   SRegimeState regime;
   regime.regime = REGIME_UNSAFE;
   regime.adx = 0.0;
   regime.atr = 0.0;
   regime.atrPercent = 0.0;
   regime.emaSlopePoints = 0.0;
   regime.bbWidthPercent = 0.0;
   regime.spreadPoints = metadata.spreadPoints;
   regime.reason = "safety gate";

   if(InpDemoSafeMode && AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL)
   {
      PrintNoTradeLog("demo safe mode blocks all open/modify actions on real accounts", regime, metadata);
      return;
   }

   if(InpRequireStrategyTester && !MQLInfoInteger(MQL_TESTER))
   {
      PrintNoTradeLog("strategy tester required by preset", regime, metadata);
      return;
   }

   if(IsDiagnosticRiskGateMode() && !MQLInfoInteger(MQL_TESTER))
   {
      PrintNoTradeLog("diagnostic risk gate mode requires Strategy Tester", regime, metadata);
      return;
   }

   if(!InpLiveTradingEnabled && !InpManageExistingPositions)
   {
      PrintNoTradeLog("live trading disabled and position management disabled", regime, metadata);
      return;
   }

   bool isNewSignalBar = IsNewBar();

   if(InpManageExistingPositions && (!InpManagePositionsOnlyOnNewBar || isNewSignalBar))
      ManageOpenPositions(metadata);

   if(!InpLiveTradingEnabled)
   {
      PrintNoTradeLog("live trading disabled", regime, metadata);
      return;
   }

   if(InpTradeOnlyOnNewBar && !isNewSignalBar)
      return;

   regime = g_regime.Detect();

   if(regime.regime == REGIME_UNSAFE)
   {
      PrintNoTradeLog("unsafe regime: " + regime.reason, regime, metadata);
      return;
   }

   STradeSignal signal;
   ResetSignal(signal);

   if(InpEnablePriceActionFibo)
   {
      signal = g_priceActionFibo.Evaluate(regime);
      if(!InpPAFLogOnlyOnNewBar || isNewSignalBar)
      {
         LogLine(g_priceActionFibo.DiagnosticSummary(metadata.actualSymbol,
                                                     metadata.canonicalSymbol,
                                                     TimeframeName(InpSignalTimeframe),
                                                     RegimeName(regime.regime),
                                                     metadata.digits));
         PrintNoTradeLog(g_priceActionFibo.PlaceholderReason(), regime, metadata);
      }
      return;
   }
   else if(regime.regime == REGIME_TREND)
      signal = g_trend.Evaluate(regime);
   else if(regime.regime == REGIME_BREAKOUT)
      signal = g_breakout.Evaluate(regime);
   else if(regime.regime == REGIME_SIDEWAY)
      signal = g_meanReversion.Evaluate(regime);

   if(signal.direction == SIGNAL_NONE)
   {
      PrintNoTradeLog("no strategy signal", regime, metadata);
      return;
   }

   ExecuteSignal(signal, regime, metadata);
}
