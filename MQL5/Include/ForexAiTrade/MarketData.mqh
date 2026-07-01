#ifndef FOREX_AI_TRADE_MARKET_DATA_MQH
#define FOREX_AI_TRADE_MARKET_DATA_MQH

#include "Inputs.mqh"

class CMarketData
{
private:
   string m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   int m_adxHandle;
   int m_atrHandle;
   int m_fastEmaHandle;
   int m_slowEmaHandle;
   int m_pullbackEmaHandle;
   int m_bandsHandle;
   int m_rsiHandle;

   double BufferValue(const int handle, const int buffer, const int shift) const
   {
      double values[];
      ArraySetAsSeries(values, true);
      if(CopyBuffer(handle, buffer, shift, 1, values) != 1)
         return 0.0;
      return values[0];
   }

public:
   CMarketData() :
      m_symbol(""),
      m_timeframe(PERIOD_H1),
      m_adxHandle(INVALID_HANDLE),
      m_atrHandle(INVALID_HANDLE),
      m_fastEmaHandle(INVALID_HANDLE),
      m_slowEmaHandle(INVALID_HANDLE),
      m_pullbackEmaHandle(INVALID_HANDLE),
      m_bandsHandle(INVALID_HANDLE),
      m_rsiHandle(INVALID_HANDLE)
   {
   }

   bool Init(const string symbol, const ENUM_TIMEFRAMES timeframe)
   {
      m_symbol = symbol;
      m_timeframe = timeframe;
      m_adxHandle = iADX(m_symbol, m_timeframe, InpAdxPeriod);
      m_atrHandle = iATR(m_symbol, m_timeframe, InpAtrPeriod);
      m_fastEmaHandle = iMA(m_symbol, m_timeframe, InpEmaFastPeriod, 0, MODE_EMA, PRICE_CLOSE);
      m_slowEmaHandle = iMA(m_symbol, m_timeframe, InpEmaSlowPeriod, 0, MODE_EMA, PRICE_CLOSE);
      m_pullbackEmaHandle = iMA(m_symbol, m_timeframe, InpTrendPullbackEmaPeriod, 0, MODE_EMA, PRICE_CLOSE);
      m_bandsHandle = iBands(m_symbol, m_timeframe, InpBandsPeriod, 0, InpBandsDeviation, PRICE_CLOSE);
      m_rsiHandle = iRSI(m_symbol, m_timeframe, InpRsiPeriod, PRICE_CLOSE);

      return m_adxHandle != INVALID_HANDLE &&
             m_atrHandle != INVALID_HANDLE &&
             m_fastEmaHandle != INVALID_HANDLE &&
             m_slowEmaHandle != INVALID_HANDLE &&
             m_pullbackEmaHandle != INVALID_HANDLE &&
             m_bandsHandle != INVALID_HANDLE &&
             m_rsiHandle != INVALID_HANDLE;
   }

   void Release()
   {
      if(m_adxHandle != INVALID_HANDLE) IndicatorRelease(m_adxHandle);
      if(m_atrHandle != INVALID_HANDLE) IndicatorRelease(m_atrHandle);
      if(m_fastEmaHandle != INVALID_HANDLE) IndicatorRelease(m_fastEmaHandle);
      if(m_slowEmaHandle != INVALID_HANDLE) IndicatorRelease(m_slowEmaHandle);
      if(m_pullbackEmaHandle != INVALID_HANDLE) IndicatorRelease(m_pullbackEmaHandle);
      if(m_bandsHandle != INVALID_HANDLE) IndicatorRelease(m_bandsHandle);
      if(m_rsiHandle != INVALID_HANDLE) IndicatorRelease(m_rsiHandle);
   }

   double Close(const int shift) const { return iClose(m_symbol, m_timeframe, shift); }
   double Open(const int shift) const { return iOpen(m_symbol, m_timeframe, shift); }
   double High(const int shift) const { return iHigh(m_symbol, m_timeframe, shift); }
   double Low(const int shift) const { return iLow(m_symbol, m_timeframe, shift); }
   double PointValue() const { return SymbolInfoDouble(m_symbol, SYMBOL_POINT); }
   double Adx(const int shift) const { return BufferValue(m_adxHandle, 0, shift); }
   double ATR(const int shift) const { return BufferValue(m_atrHandle, 0, shift); }
   double FastEma(const int shift) const { return BufferValue(m_fastEmaHandle, 0, shift); }
   double SlowEma(const int shift) const { return BufferValue(m_slowEmaHandle, 0, shift); }
   double PullbackEma(const int shift) const { return BufferValue(m_pullbackEmaHandle, 0, shift); }
   double UpperBand(const int shift) const { return BufferValue(m_bandsHandle, 1, shift); }
   double MiddleBand(const int shift) const { return BufferValue(m_bandsHandle, 0, shift); }
   double LowerBand(const int shift) const { return BufferValue(m_bandsHandle, 2, shift); }
   double Rsi(const int shift) const { return BufferValue(m_rsiHandle, 0, shift); }

   double SpreadPoints() const
   {
      long spread = 0;
      if(SymbolInfoInteger(m_symbol, SYMBOL_SPREAD, spread))
         return (double)spread;

      double point = PointValue();
      if(point <= 0.0)
         return 0.0;
      return (SymbolInfoDouble(m_symbol, SYMBOL_ASK) - SymbolInfoDouble(m_symbol, SYMBOL_BID)) / point;
   }

   double HighestHigh(const int startShift, const int bars) const
   {
      double highest = -DBL_MAX;
      for(int i = startShift; i < startShift + bars; ++i)
         highest = MathMax(highest, High(i));
      return highest;
   }

   double LowestLow(const int startShift, const int bars) const
   {
      double lowest = DBL_MAX;
      for(int i = startShift; i < startShift + bars; ++i)
         lowest = MathMin(lowest, Low(i));
      return lowest;
   }
};

#endif
