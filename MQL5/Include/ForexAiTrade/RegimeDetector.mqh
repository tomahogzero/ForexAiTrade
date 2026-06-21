#ifndef FOREX_AI_TRADE_REGIME_DETECTOR_MQH
#define FOREX_AI_TRADE_REGIME_DETECTOR_MQH

#include "Inputs.mqh"
#include "Types.mqh"
#include "MarketData.mqh"

class CRegimeDetector
{
private:
   CMarketData *m_market;

public:
   CRegimeDetector() : m_market(NULL) {}

   bool Init(CMarketData *market)
   {
      m_market = market;
      return m_market != NULL;
   }

   SRegimeState Detect()
   {
      SRegimeState state;
      state.regime = REGIME_UNSAFE;
      state.adx = m_market.Adx(1);
      state.atr = m_market.ATR(1);
      double close = m_market.Close(1);
      double point = m_market.PointValue();
      double fastNow = m_market.FastEma(1);
      double fastPast = m_market.FastEma(6);
      double upper = m_market.UpperBand(1);
      double lower = m_market.LowerBand(1);
      double middle = m_market.MiddleBand(1);
      state.spreadPoints = m_market.SpreadPoints();
      state.atrPercent = close > 0.0 ? state.atr / close * 100.0 : 0.0;
      state.emaSlopePoints = point > 0.0 ? (fastNow - fastPast) / point : 0.0;
      state.bbWidthPercent = middle > 0.0 ? (upper - lower) / middle * 100.0 : 0.0;
      state.reason = "";

      if(state.spreadPoints > InpMaxSpreadPoints)
      {
         state.reason = "spread too wide";
         return state;
      }

      if(state.atrPercent < InpMinAtrPercent || state.atrPercent > InpMaxAtrPercent)
      {
         state.reason = "volatility outside allowed range";
         return state;
      }

      if(state.adx >= InpTrendAdxMin &&
         MathAbs(state.emaSlopePoints) >= InpTrendSlopeMinPoints)
      {
         state.regime = REGIME_TREND;
         state.reason = "trend";
         return state;
      }

      if(state.bbWidthPercent >= InpBreakoutBbWidthMinPct &&
         state.adx >= InpSidewayAdxMax)
      {
         state.regime = REGIME_BREAKOUT;
         state.reason = "breakout";
         return state;
      }

      if(state.adx <= InpSidewayAdxMax &&
         state.bbWidthPercent <= InpSidewayBbWidthMaxPct)
      {
         state.regime = REGIME_SIDEWAY;
         state.reason = "sideway";
         return state;
      }

      state.reason = "mixed or low-quality conditions";
      return state;
   }
};

#endif
