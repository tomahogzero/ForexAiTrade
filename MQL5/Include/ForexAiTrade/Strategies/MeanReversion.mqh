#ifndef FOREX_AI_TRADE_MEAN_REVERSION_MQH
#define FOREX_AI_TRADE_MEAN_REVERSION_MQH

#include "../Inputs.mqh"
#include "../Types.mqh"
#include "../MarketData.mqh"

class CMeanReversion
{
private:
   CMarketData *m_market;

public:
   CMeanReversion() : m_market(NULL) {}
   void Init(CMarketData *market) { m_market = market; }

   STradeSignal Evaluate(const SRegimeState &regime)
   {
      STradeSignal signal;
      ResetSignal(signal);

      double close = m_market.Close(1);
      double lower = m_market.LowerBand(1);
      double upper = m_market.UpperBand(1);
      double atr = regime.atr;
      double rsi = m_market.Rsi(1);

      if(close <= 0.0 || atr <= 0.0)
         return signal;

      if(close <= lower && rsi <= InpMeanRevRsiBuyMax)
      {
         signal.direction = SIGNAL_BUY;
         signal.stopLoss = NormalizeDouble(close - atr * InpMeanRevAtrStop, _Digits);
         signal.takeProfit = NormalizeDouble(close + atr * InpMeanRevAtrStop * InpMeanRevRewardRisk, _Digits);
         signal.confidence = 0.55;
         signal.comment = "FAT MeanRev Buy";
      }
      else if(close >= upper && rsi >= InpMeanRevRsiSellMin)
      {
         signal.direction = SIGNAL_SELL;
         signal.stopLoss = NormalizeDouble(close + atr * InpMeanRevAtrStop, _Digits);
         signal.takeProfit = NormalizeDouble(close - atr * InpMeanRevAtrStop * InpMeanRevRewardRisk, _Digits);
         signal.confidence = 0.55;
         signal.comment = "FAT MeanRev Sell";
      }

      return signal;
   }
};

#endif
