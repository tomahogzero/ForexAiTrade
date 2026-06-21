#ifndef FOREX_AI_TRADE_TREND_FOLLOWING_MQH
#define FOREX_AI_TRADE_TREND_FOLLOWING_MQH

#include "../Inputs.mqh"
#include "../Types.mqh"
#include "../MarketData.mqh"

class CTrendFollowing
{
private:
   CMarketData *m_market;

public:
   CTrendFollowing() : m_market(NULL) {}
   void Init(CMarketData *market) { m_market = market; }

   STradeSignal Evaluate(const SRegimeState &regime)
   {
      STradeSignal signal;
      ResetSignal(signal);

      double close = m_market.Close(1);
      double fast = m_market.FastEma(1);
      double slow = m_market.SlowEma(1);
      double pullback = m_market.PullbackEma(1);
      double atr = regime.atr;

      if(close <= 0.0 || atr <= 0.0)
         return signal;

      if(fast > slow && close > fast && m_market.Low(1) <= pullback)
      {
         signal.direction = SIGNAL_BUY;
         signal.stopLoss = NormalizeDouble(close - atr * InpTrendAtrStop, _Digits);
         signal.takeProfit = NormalizeDouble(close + atr * InpTrendAtrStop * InpTrendRewardRisk, _Digits);
         signal.confidence = 0.65;
         signal.comment = "FAT Trend Buy";
      }
      else if(fast < slow && close < fast && m_market.High(1) >= pullback)
      {
         signal.direction = SIGNAL_SELL;
         signal.stopLoss = NormalizeDouble(close + atr * InpTrendAtrStop, _Digits);
         signal.takeProfit = NormalizeDouble(close - atr * InpTrendAtrStop * InpTrendRewardRisk, _Digits);
         signal.confidence = 0.65;
         signal.comment = "FAT Trend Sell";
      }

      return signal;
   }
};

#endif
