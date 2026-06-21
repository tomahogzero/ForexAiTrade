#ifndef FOREX_AI_TRADE_RISK_MANAGER_MQH
#define FOREX_AI_TRADE_RISK_MANAGER_MQH

#include "Inputs.mqh"
#include "Types.mqh"
#include "SymbolHelper.mqh"

struct SPositionSizeResult
{
   bool valid;
   double lots;
   double rawLots;
   double riskMoney;
   double actualRiskMoney;
   string reason;
};

class CRiskManager
{
private:
   datetime m_losingStreakCooldownUntil;
   bool     m_losingStreakCooldownActive;
   int      m_losingStreakTriggerDealCount;

   string NormalizedRiskGateMode() const
   {
      string mode = InpRiskGateMode;
      StringToUpper(mode);
      return mode;
   }

   bool IsDiagnosticRiskGateMode() const
   {
      return StringFind(NormalizedRiskGateMode(), "DIAGNOSTIC_") == 0;
   }

   int SignalTimeframeSeconds() const
   {
      int seconds = PeriodSeconds(InpSignalTimeframe);
      if(seconds <= 0)
         seconds = 3600;
      return seconds;
   }

   datetime NextBrokerDay(const datetime value) const
   {
      return DayStamp(value) + 86400;
   }

   datetime DayStamp(const datetime value) const
   {
      MqlDateTime t;
      TimeToStruct(value, t);
      t.hour = 0;
      t.min = 0;
      t.sec = 0;
      return StructToTime(t);
   }

   datetime WeekStamp(const datetime value) const
   {
      MqlDateTime t;
      TimeToStruct(value, t);
      int offset = t.day_of_week == 0 ? 6 : t.day_of_week - 1;
      return DayStamp(value) - offset * 86400;
   }

   double ClosedDealPnl(const datetime fromTime) const
   {
      if(!HistorySelect(fromTime, TimeCurrent()))
         return 0.0;

      double pnl = 0.0;
      for(int i = HistoryDealsTotal() - 1; i >= 0; --i)
      {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket == 0)
            continue;

         if(HistoryDealGetString(ticket, DEAL_SYMBOL) != _Symbol ||
            (long)HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber)
         {
            continue;
         }

         ENUM_DEAL_ENTRY entry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket, DEAL_ENTRY);
         if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY)
            continue;

         pnl += HistoryDealGetDouble(ticket, DEAL_PROFIT) +
                HistoryDealGetDouble(ticket, DEAL_SWAP) +
                HistoryDealGetDouble(ticket, DEAL_COMMISSION);
      }

      return pnl;
   }

   int ConsecutiveLosses() const
   {
      if(!HistorySelect(0, TimeCurrent()))
         return 0;

      int streak = 0;
      for(int i = HistoryDealsTotal() - 1; i >= 0; --i)
      {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket == 0)
            continue;

         if(HistoryDealGetString(ticket, DEAL_SYMBOL) != _Symbol ||
            (long)HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber)
         {
            continue;
         }

         ENUM_DEAL_ENTRY entry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket, DEAL_ENTRY);
         if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY)
            continue;

         double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT) +
                         HistoryDealGetDouble(ticket, DEAL_SWAP) +
                         HistoryDealGetDouble(ticket, DEAL_COMMISSION);

         if(profit < 0.0)
            ++streak;
         else if(profit > 0.0)
            break;
      }

      return streak;
   }

   int CountOpenOrders() const
   {
      int count = 0;
      for(int i = PositionsTotal() - 1; i >= 0; --i)
      {
         ulong ticket = PositionGetTicket(i);
         if(ticket == 0 || !PositionSelectByTicket(ticket))
            continue;

         if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
            (long)PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            ++count;
         }
      }

      for(int i = OrdersTotal() - 1; i >= 0; --i)
      {
         ulong ticket = OrderGetTicket(i);
         if(ticket == 0 || !OrderSelect(ticket))
            continue;

         if(OrderGetString(ORDER_SYMBOL) == _Symbol &&
            (long)OrderGetInteger(ORDER_MAGIC) == InpMagicNumber)
         {
            ++count;
         }
      }

      return count;
   }

   int CountClosedDeals() const
   {
      if(!HistorySelect(0, TimeCurrent()))
         return 0;

      int count = 0;
      for(int i = HistoryDealsTotal() - 1; i >= 0; --i)
      {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket == 0)
            continue;

         if(HistoryDealGetString(ticket, DEAL_SYMBOL) != _Symbol ||
            (long)HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber)
         {
            continue;
         }

         ENUM_DEAL_ENTRY entry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket, DEAL_ENTRY);
         if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_OUT_BY)
            ++count;
      }
      return count;
   }

   double NormalizeVolumeDown(const double rawLots, const double minLot, const double maxLot, const double step) const
   {
      double clipped = MathMin(rawLots, maxLot);
      double steps = MathFloor(clipped / step);
      double normalized = steps * step;
      if(normalized < minLot)
         return 0.0;
      return NormalizeDouble(normalized, 2);
   }

public:
   void Init()
   {
      m_losingStreakCooldownUntil = 0;
      m_losingStreakCooldownActive = false;
      m_losingStreakTriggerDealCount = 0;
      Print("RiskManager initialized. RiskGateMode=" + NormalizedRiskGateMode() +
            " Daily/weekly limits use closed deal history; floating drawdown uses current balance/equity.");
   }

   void Update()
   {
   }

   bool CanOpenNewTrade(const SRegimeState &regime, const SSymbolMetadata &metadata, string &reason)
   {
      string riskGateMode = NormalizedRiskGateMode();
      if(IsDiagnosticRiskGateMode() && !MQLInfoInteger(MQL_TESTER))
      {
         reason = "diagnostic risk gate mode requires Strategy Tester";
         return false;
      }

      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      if(equity <= 0.0 || balance <= 0.0)
      {
         reason = "invalid balance or equity";
         return false;
      }

      if(!metadata.valid)
      {
         reason = "invalid symbol metadata: " + metadata.reason;
         return false;
      }

      if(!CSymbolHelper::IsAllowed(metadata.actualSymbol, metadata.canonicalSymbol))
      {
         reason = "symbol not allowed by InpAllowedSymbolsCsv: actual=" + metadata.actualSymbol +
                  " canonical=" + metadata.canonicalSymbol;
         return false;
      }

      if(regime.spreadPoints > InpMaxSpreadPoints)
      {
         reason = "spread above maximum";
         return false;
      }

      if(CountOpenOrders() >= InpMaxOpenOrders)
      {
         reason = "max open orders reached";
         return false;
      }

      datetime now = TimeCurrent();
      double dailyPnl = ClosedDealPnl(DayStamp(now));
      double weeklyPnl = ClosedDealPnl(WeekStamp(now));
      double dailyLossPct = dailyPnl < 0.0 ? -dailyPnl / balance * 100.0 : 0.0;
      double weeklyLossPct = weeklyPnl < 0.0 ? -weeklyPnl / balance * 100.0 : 0.0;
      double floatingDdPct = balance > 0.0 ? MathMax(0.0, (balance - equity) / balance * 100.0) : 0.0;

      if(dailyLossPct >= InpMaxDailyLossPercent)
      {
         reason = StringFormat("max daily loss reached from closed deal history: %.2f%%", dailyLossPct);
         return false;
      }

      if(weeklyLossPct >= InpMaxWeeklyLossPercent)
      {
         reason = StringFormat("max weekly loss reached from closed deal history: %.2f%%", weeklyLossPct);
         return false;
      }

      if(floatingDdPct >= InpMaxTotalDrawdownPercent)
      {
         reason = StringFormat("max floating drawdown reached from balance/equity: %.2f%%", floatingDdPct);
         return false;
      }

      if(floatingDdPct >= InpEquityKillSwitchPercent)
      {
         reason = StringFormat("equity kill switch reached from balance/equity: %.2f%%", floatingDdPct);
         return false;
      }

      int losingStreak = ConsecutiveLosses();
      if(losingStreak >= InpMaxLosingStreak)
      {
         int closedDealCount = CountClosedDeals();
         if(riskGateMode == "DIAGNOSTIC_NO_LOSING_STREAK_GATE")
         {
            reason = StringFormat("diagnostic mode ignored losing streak gate: %d", losingStreak);
            return true;
         }

         if(riskGateMode == "DIAGNOSTIC_FIXED_COOLDOWN")
         {
            datetime nowForCooldown = TimeCurrent();
            if(m_losingStreakCooldownActive && m_losingStreakCooldownUntil > nowForCooldown)
            {
               reason = StringFormat("losing streak fixed cooldown active until %s; streak=%d",
                                     TimeToString(m_losingStreakCooldownUntil, TIME_DATE | TIME_SECONDS),
                                     losingStreak);
               return false;
            }

            if(m_losingStreakCooldownActive && m_losingStreakCooldownUntil <= nowForCooldown)
            {
               m_losingStreakCooldownActive = false;
               if(closedDealCount == m_losingStreakTriggerDealCount)
               {
                  reason = StringFormat("losing streak fixed cooldown ended at %s; diagnostic reevaluation allowed; streak=%d",
                                        TimeToString(nowForCooldown, TIME_DATE | TIME_SECONDS),
                                        losingStreak);
                  return true;
               }
            }

            m_losingStreakCooldownUntil = nowForCooldown + MathMax(1, InpLosingStreakCooldownBars) * SignalTimeframeSeconds();
            m_losingStreakCooldownActive = true;
            m_losingStreakTriggerDealCount = closedDealCount;
            reason = StringFormat("losing streak trigger; fixed cooldown starts until %s; streak=%d",
                                  TimeToString(m_losingStreakCooldownUntil, TIME_DATE | TIME_SECONDS),
                                  losingStreak);
            return false;
         }

         if(riskGateMode == "DIAGNOSTIC_NEXT_DAY_RESET")
         {
            datetime nowForReset = TimeCurrent();
            if(m_losingStreakCooldownActive && m_losingStreakCooldownUntil > nowForReset)
            {
               reason = StringFormat("losing streak next-day reset active until %s; streak=%d",
                                     TimeToString(m_losingStreakCooldownUntil, TIME_DATE | TIME_SECONDS),
                                     losingStreak);
               return false;
            }

            if(m_losingStreakCooldownActive && m_losingStreakCooldownUntil <= nowForReset)
            {
               m_losingStreakCooldownActive = false;
               if(closedDealCount == m_losingStreakTriggerDealCount)
               {
                  reason = StringFormat("losing streak next-day reset allowed trading again at %s; streak=%d",
                                        TimeToString(nowForReset, TIME_DATE | TIME_SECONDS),
                                        losingStreak);
                  return true;
               }
            }

            m_losingStreakCooldownUntil = NextBrokerDay(nowForReset);
            m_losingStreakCooldownActive = true;
            m_losingStreakTriggerDealCount = closedDealCount;
            reason = StringFormat("losing streak trigger; next-day reset blocks until %s; streak=%d",
                                  TimeToString(m_losingStreakCooldownUntil, TIME_DATE | TIME_SECONDS),
                                  losingStreak);
            return false;
         }

         reason = StringFormat("normal losing streak limit reached from deal history: %d", losingStreak);
         return false;
      }

      reason = StringFormat("ok; risk_gate_mode=%s daily/weekly risk from closed deals daily=%.2f weekly=%.2f floating_dd=%.2f%%",
                            riskGateMode, dailyPnl, weeklyPnl, floatingDdPct);
      return true;
   }

   bool CalculatePositionSize(const double entryPrice, const double stopLossPrice, const SSymbolMetadata &metadata, SPositionSizeResult &result) const
   {
      result.valid = false;
      result.lots = 0.0;
      result.rawLots = 0.0;
      result.riskMoney = 0.0;
      result.actualRiskMoney = 0.0;
      result.reason = "";

      if(!metadata.valid)
      {
         result.reason = "invalid symbol metadata: " + metadata.reason;
         return false;
      }

      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double riskMoney = equity * InpRiskPercentPerTrade / 100.0;
      double stopDistance = MathAbs(entryPrice - stopLossPrice);
      if(riskMoney <= 0.0 || stopDistance <= 0.0)
      {
         result.reason = "invalid risk money or stop-loss distance";
         return false;
      }

      double brokerMin = metadata.volumeMin;
      double brokerMax = metadata.volumeMax;
      double configuredMax = MathMin(InpMaxLot, brokerMax);
      double moneyPerLot = (stopDistance / metadata.tickSize) * metadata.tickValue;
      if(moneyPerLot <= 0.0)
      {
         result.reason = "invalid money risk per lot";
         return false;
      }

      double rawLots = riskMoney / moneyPerLot;
      result.rawLots = rawLots;
      result.riskMoney = riskMoney;

      if(rawLots < brokerMin)
      {
         result.reason = "broker minimum lot exceeds configured risk budget";
         return false;
      }

      double normalizedLots = NormalizeVolumeDown(rawLots, brokerMin, configuredMax, metadata.volumeStep);
      if(normalizedLots <= 0.0)
      {
         result.reason = "normalized lot is below broker minimum after risk-safe rounding";
         return false;
      }

      double actualRisk = normalizedLots * moneyPerLot;
      result.actualRiskMoney = actualRisk;
      double tolerance = MathMax(0.01, riskMoney * 0.001);
      if(actualRisk > riskMoney + tolerance)
      {
         result.reason = "normalized lot would exceed configured risk budget";
         return false;
      }

      result.valid = true;
      result.lots = normalizedLots;
      result.reason = StringFormat("risk-safe lot accepted raw=%.4f normalized=%.2f risk=%.2f actual=%.2f",
                                   rawLots, normalizedLots, riskMoney, actualRisk);
      return true;
   }

   bool ValidateExecutionSafety(const ESignalDirection direction,
                                const double volume,
                                const double entryPrice,
                                const double stopLoss,
                                const double takeProfit,
                                const SSymbolMetadata &metadata,
                                string &reason) const
   {
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

      if(metadata.tradeMode == SYMBOL_TRADE_MODE_DISABLED || metadata.tradeMode == SYMBOL_TRADE_MODE_CLOSEONLY)
      {
         reason = "SYMBOL_TRADE_MODE does not allow new entries";
         return false;
      }

      if(volume < metadata.volumeMin || volume > metadata.volumeMax)
      {
         reason = "volume outside broker limits";
         return false;
      }

      double minStopDistance = metadata.stopsLevel * metadata.point;
      if(minStopDistance > 0.0)
      {
         if(MathAbs(entryPrice - stopLoss) < minStopDistance ||
            MathAbs(entryPrice - takeProfit) < minStopDistance)
         {
            reason = "SL/TP distance violates SYMBOL_TRADE_STOPS_LEVEL";
            return false;
         }
      }

      double freezeDistance = metadata.freezeLevel * metadata.point;
      if(freezeDistance > 0.0)
      {
         if(MathAbs(entryPrice - stopLoss) < freezeDistance ||
            MathAbs(entryPrice - takeProfit) < freezeDistance)
         {
            reason = "SL/TP distance violates SYMBOL_TRADE_FREEZE_LEVEL";
            return false;
         }
      }

      ENUM_ORDER_TYPE orderType = direction == SIGNAL_BUY ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
      double requiredMargin = 0.0;
      if(!OrderCalcMargin(orderType, _Symbol, volume, entryPrice, requiredMargin))
      {
         reason = "OrderCalcMargin failed";
         return false;
      }

      if(requiredMargin <= 0.0)
      {
         reason = "OrderCalcMargin returned invalid margin";
         return false;
      }

      double freeMargin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
      if(freeMargin <= requiredMargin)
      {
         reason = StringFormat("free margin %.2f is not enough for required margin %.2f", freeMargin, requiredMargin);
         return false;
      }

      reason = "execution safety checks passed";
      return true;
   }
};

#endif
