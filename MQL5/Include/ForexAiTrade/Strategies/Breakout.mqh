#ifndef FOREX_AI_TRADE_BREAKOUT_MQH
#define FOREX_AI_TRADE_BREAKOUT_MQH

#include "../Inputs.mqh"
#include "../Types.mqh"
#include "../MarketData.mqh"

class CBreakoutStrategy
{
private:
   CMarketData *m_market;

public:
   CBreakoutStrategy() : m_market(NULL) {}
   void Init(CMarketData *market) { m_market = market; }

   STradeSignal Evaluate(const SRegimeState &regime)
   {
      STradeSignal signal;
      ResetSignal(signal);

      double close = m_market.Close(1);
      double atr = regime.atr;
      if(close <= 0.0 || atr <= 0.0)
         return signal;

      double high = m_market.HighestHigh(2, InpBreakoutLookbackBars);
      double low = m_market.LowestLow(2, InpBreakoutLookbackBars);
      double buffer = atr * InpBreakoutAtrBuffer;

      if(close > high + buffer)
      {
         signal.direction = SIGNAL_BUY;
         signal.stopLoss = NormalizeDouble(close - atr * InpBreakoutAtrStop, _Digits);
         signal.takeProfit = NormalizeDouble(close + atr * InpBreakoutAtrStop * InpBreakoutRewardRisk, _Digits);
         signal.confidence = 0.60;
         signal.comment = "FAT Breakout Buy";
      }
      else if(close < low - buffer)
      {
         signal.direction = SIGNAL_SELL;
         signal.stopLoss = NormalizeDouble(close + atr * InpBreakoutAtrStop, _Digits);
         signal.takeProfit = NormalizeDouble(close - atr * InpBreakoutAtrStop * InpBreakoutRewardRisk, _Digits);
         signal.confidence = 0.60;
         signal.comment = "FAT Breakout Sell";
      }

      return signal;
   }
};

#endif
