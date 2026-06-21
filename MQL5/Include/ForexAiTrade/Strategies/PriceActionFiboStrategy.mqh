#ifndef FOREX_AI_TRADE_PRICE_ACTION_FIBO_STRATEGY_MQH
#define FOREX_AI_TRADE_PRICE_ACTION_FIBO_STRATEGY_MQH

#include "../Inputs.mqh"
#include "../Types.mqh"
#include "../MarketData.mqh"

enum EPAFDiagnosticClassification
{
   PAF_NO_SETUP = 0,
   PAF_POSSIBLE_BREAK_RETEST = 1,
   PAF_POSSIBLE_FIBO_PULLBACK = 2,
   PAF_POSSIBLE_ZONE_REJECTION = 3,
   PAF_INSUFFICIENT_DATA = 4
};

struct SPAFDiagnosticState
{
   bool swingHighFound;
   bool swingLowFound;
   bool zoneFound;
   bool fiboZoneFound;
   bool breakoutDetected;
   bool retestDetected;
   bool rejectionCandleDetected;
   bool engulfingCandleDetected;
   double swingHigh;
   double swingLow;
   double supportLow;
   double supportHigh;
   double resistanceLow;
   double resistanceHigh;
   double fiboLow;
   double fiboHigh;
   string fiboLevels;
   string reason;
   EPAFDiagnosticClassification classification;
};

void ResetPAFDiagnosticState(SPAFDiagnosticState &state)
{
   state.swingHighFound = false;
   state.swingLowFound = false;
   state.zoneFound = false;
   state.fiboZoneFound = false;
   state.breakoutDetected = false;
   state.retestDetected = false;
   state.rejectionCandleDetected = false;
   state.engulfingCandleDetected = false;
   state.swingHigh = 0.0;
   state.swingLow = 0.0;
   state.supportLow = 0.0;
   state.supportHigh = 0.0;
   state.resistanceLow = 0.0;
   state.resistanceHigh = 0.0;
   state.fiboLow = 0.0;
   state.fiboHigh = 0.0;
   state.fiboLevels = "";
   state.reason = "not evaluated";
   state.classification = PAF_NO_SETUP;
}

class CPriceActionFiboStrategy
{
private:
   CMarketData *m_market;
   SPAFDiagnosticState m_lastDiagnostic;

   string BoolText(const bool value) const
   {
      return value ? "true" : "false";
   }

   string ClassificationName(const EPAFDiagnosticClassification classification) const
   {
      if(classification == PAF_POSSIBLE_BREAK_RETEST)
         return "POSSIBLE_BREAK_RETEST";
      if(classification == PAF_POSSIBLE_FIBO_PULLBACK)
         return "POSSIBLE_FIBO_PULLBACK";
      if(classification == PAF_POSSIBLE_ZONE_REJECTION)
         return "POSSIBLE_ZONE_REJECTION";
      if(classification == PAF_INSUFFICIENT_DATA)
         return "INSUFFICIENT_DATA";
      return "NO_SETUP";
   }

   bool HasEnoughData(string &reason) const
   {
      if(m_market == NULL)
      {
         reason = "market data not initialized";
         return false;
      }

      if(InpPAFSwingLookbackBars < 3)
      {
         reason = "InpPAFSwingLookbackBars must be at least 3";
         return false;
      }

      if(m_market.Close(InpPAFSwingLookbackBars + 2) <= 0.0 ||
         m_market.High(InpPAFSwingLookbackBars + 2) <= 0.0 ||
         m_market.Low(InpPAFSwingLookbackBars + 2) <= 0.0)
      {
         reason = "insufficient closed bars for configured swing lookback";
         return false;
      }

      reason = "ok";
      return true;
   }

   double BodySize(const int shift) const
   {
      return MathAbs(m_market.Close(shift) - m_market.Open(shift));
   }

   bool DetectSwingHigh(double &swingHigh, int &swingShift, string &reason) const
   {
      swingHigh = -DBL_MAX;
      swingShift = -1;

      for(int i = 2; i < 2 + InpPAFSwingLookbackBars; ++i)
      {
         double high = m_market.High(i);
         if(high <= 0.0)
         {
            reason = "missing high data";
            return false;
         }

         if(high > swingHigh)
         {
            swingHigh = high;
            swingShift = i;
         }
      }

      if(swingShift < 0)
      {
         reason = "swing high not found";
         return false;
      }

      reason = "ok";
      return true;
   }

   bool DetectSwingLow(double &swingLow, int &swingShift, string &reason) const
   {
      swingLow = DBL_MAX;
      swingShift = -1;

      for(int i = 2; i < 2 + InpPAFSwingLookbackBars; ++i)
      {
         double low = m_market.Low(i);
         if(low <= 0.0)
         {
            reason = "missing low data";
            return false;
         }

         if(low < swingLow)
         {
            swingLow = low;
            swingShift = i;
         }
      }

      if(swingShift < 0)
      {
         reason = "swing low not found";
         return false;
      }

      reason = "ok";
      return true;
   }

   bool DetectSupportResistanceZone(SPAFDiagnosticState &state, const double atr, string &reason) const
   {
      if(!state.swingHighFound || !state.swingLowFound)
      {
         reason = "swing high/low required before zone detection";
         return false;
      }

      double point = m_market.PointValue();
      if(point <= 0.0 || atr <= 0.0)
      {
         reason = "invalid point or ATR for zone detection";
         return false;
      }

      double swingDistancePoints = MathAbs(state.swingHigh - state.swingLow) / point;
      if(swingDistancePoints < InpPAFMinSwingDistancePoints)
      {
         reason = "swing distance below minimum points";
         return false;
      }

      double width = atr * InpPAFZoneAtrMultiplier;
      if(width <= 0.0)
      {
         reason = "zone width is zero";
         return false;
      }

      state.supportLow = state.swingLow - width;
      state.supportHigh = state.swingLow + width;
      state.resistanceLow = state.swingHigh - width;
      state.resistanceHigh = state.swingHigh + width;
      reason = "ok";
      return true;
   }

   bool CalculateFiboZone(SPAFDiagnosticState &state, string &reason) const
   {
      if(!state.swingHighFound || !state.swingLowFound || state.swingHigh <= state.swingLow)
      {
         reason = "valid swing range required before fibo calculation";
         return false;
      }

      string parts[];
      int count = StringSplit(InpPAFFiboLevelsCsv, ',', parts);
      if(count <= 0)
      {
         reason = "fibo levels csv is empty";
         return false;
      }

      double range = state.swingHigh - state.swingLow;
      double fiboMin = DBL_MAX;
      double fiboMax = -DBL_MAX;
      string levels = "";

      for(int i = 0; i < count; ++i)
      {
         string token = parts[i];
         StringTrimLeft(token);
         StringTrimRight(token);
         double level = StringToDouble(token);
         if(level <= 0.0 || level >= 100.0)
            continue;

         double price = state.swingHigh - range * (level / 100.0);
         fiboMin = MathMin(fiboMin, price);
         fiboMax = MathMax(fiboMax, price);
         if(levels != "")
            levels += ",";
         levels += DoubleToString(level, 1);
      }

      if(fiboMin == DBL_MAX || fiboMax == -DBL_MAX)
      {
         reason = "no valid fibo levels between 0 and 100";
         return false;
      }

      state.fiboLow = fiboMin;
      state.fiboHigh = fiboMax;
      state.fiboLevels = levels;
      reason = "ok";
      return true;
   }

   bool DetectBreakout(const SPAFDiagnosticState &state, const double atr, string &reason) const
   {
      if(!state.swingHighFound || !state.swingLowFound || atr <= 0.0)
      {
         reason = "swing range and ATR required before breakout detection";
         return false;
      }

      double close = m_market.Close(1);
      double buffer = atr * InpPAFBreakoutCloseBufferAtr;
      if(close > state.swingHigh + buffer || close < state.swingLow - buffer)
      {
         reason = "close outside swing range with ATR buffer";
         return true;
      }

      reason = "close remains inside swing range";
      return false;
   }

   bool DetectRetest(const SPAFDiagnosticState &state, const double atr, string &reason) const
   {
      if(!state.swingHighFound || !state.swingLowFound || atr <= 0.0)
      {
         reason = "swing range and ATR required before retest detection";
         return false;
      }

      double close = m_market.Close(1);
      double high = m_market.High(1);
      double low = m_market.Low(1);
      double maxDistance = atr * InpPAFRetestMaxDistanceAtr;

      if(close > state.swingHigh && MathAbs(low - state.swingHigh) <= maxDistance)
      {
         reason = "bullish retest near prior swing high";
         return true;
      }

      if(close < state.swingLow && MathAbs(high - state.swingLow) <= maxDistance)
      {
         reason = "bearish retest near prior swing low";
         return true;
      }

      reason = "no retest within ATR distance";
      return false;
   }

   bool DetectRejectionCandle(string &reason) const
   {
      double open = m_market.Open(1);
      double close = m_market.Close(1);
      double high = m_market.High(1);
      double low = m_market.Low(1);
      if(open <= 0.0 || close <= 0.0 || high <= 0.0 || low <= 0.0)
      {
         reason = "missing candle data";
         return false;
      }

      double body = MathMax(BodySize(1), m_market.PointValue());
      double upperWick = high - MathMax(open, close);
      double lowerWick = MathMin(open, close) - low;
      double ratio = InpPAFRejectionWickBodyRatio;

      if(upperWick >= body * ratio || lowerWick >= body * ratio)
      {
         reason = "wick/body ratio threshold met";
         return true;
      }

      reason = "wick/body ratio below threshold";
      return false;
   }

   bool DetectEngulfingCandle(string &reason) const
   {
      double open1 = m_market.Open(1);
      double close1 = m_market.Close(1);
      double open2 = m_market.Open(2);
      double close2 = m_market.Close(2);
      if(open1 <= 0.0 || close1 <= 0.0 || open2 <= 0.0 || close2 <= 0.0)
      {
         reason = "missing candle body data";
         return false;
      }

      double body1 = BodySize(1);
      double body2 = BodySize(2);
      if(body1 <= 0.0 || body2 <= 0.0 || body1 < body2 * InpPAFEngulfingMinBodyRatio)
      {
         reason = "body ratio below engulfing threshold";
         return false;
      }

      bool bullish = close1 > open1 && close2 < open2 && open1 <= close2 && close1 >= open2;
      bool bearish = close1 < open1 && close2 > open2 && open1 >= close2 && close1 <= open2;
      if(bullish || bearish)
      {
         reason = "engulfing body threshold met";
         return true;
      }

      reason = "no engulfing body overlap";
      return false;
   }

   void EvaluateDiagnostics(const SRegimeState &regime)
   {
      ResetPAFDiagnosticState(m_lastDiagnostic);

      if(!InpPAFDiagnosticsEnabled)
      {
         m_lastDiagnostic.reason = "diagnostics disabled";
         return;
      }

      string reason = "";
      if(!HasEnoughData(reason))
      {
         m_lastDiagnostic.reason = reason;
         m_lastDiagnostic.classification = PAF_INSUFFICIENT_DATA;
         return;
      }

      int swingHighShift = -1;
      int swingLowShift = -1;
      m_lastDiagnostic.swingHighFound = DetectSwingHigh(m_lastDiagnostic.swingHigh, swingHighShift, reason);
      if(!m_lastDiagnostic.swingHighFound)
      {
         m_lastDiagnostic.reason = reason;
         m_lastDiagnostic.classification = PAF_INSUFFICIENT_DATA;
         return;
      }

      m_lastDiagnostic.swingLowFound = DetectSwingLow(m_lastDiagnostic.swingLow, swingLowShift, reason);
      if(!m_lastDiagnostic.swingLowFound)
      {
         m_lastDiagnostic.reason = reason;
         m_lastDiagnostic.classification = PAF_INSUFFICIENT_DATA;
         return;
      }

      double atr = regime.atr > 0.0 ? regime.atr : m_market.ATR(1);
      m_lastDiagnostic.zoneFound = DetectSupportResistanceZone(m_lastDiagnostic, atr, reason);
      if(!m_lastDiagnostic.zoneFound)
      {
         m_lastDiagnostic.reason = reason;
         m_lastDiagnostic.classification = PAF_NO_SETUP;
         return;
      }

      m_lastDiagnostic.fiboZoneFound = CalculateFiboZone(m_lastDiagnostic, reason);
      if(!m_lastDiagnostic.fiboZoneFound)
      {
         m_lastDiagnostic.reason = reason;
         m_lastDiagnostic.classification = PAF_NO_SETUP;
         return;
      }

      string breakoutReason = "";
      string retestReason = "";
      string rejectionReason = "";
      string engulfingReason = "";
      m_lastDiagnostic.breakoutDetected = DetectBreakout(m_lastDiagnostic, atr, breakoutReason);
      m_lastDiagnostic.retestDetected = DetectRetest(m_lastDiagnostic, atr, retestReason);
      m_lastDiagnostic.rejectionCandleDetected = DetectRejectionCandle(rejectionReason);
      m_lastDiagnostic.engulfingCandleDetected = DetectEngulfingCandle(engulfingReason);

      double close = m_market.Close(1);
      bool inFiboZone = close >= m_lastDiagnostic.fiboLow && close <= m_lastDiagnostic.fiboHigh;
      bool nearSupport = close >= m_lastDiagnostic.supportLow && close <= m_lastDiagnostic.supportHigh;
      bool nearResistance = close >= m_lastDiagnostic.resistanceLow && close <= m_lastDiagnostic.resistanceHigh;
      bool candleConfirmation = m_lastDiagnostic.rejectionCandleDetected || m_lastDiagnostic.engulfingCandleDetected;

      if(m_lastDiagnostic.breakoutDetected && m_lastDiagnostic.retestDetected)
         m_lastDiagnostic.classification = PAF_POSSIBLE_BREAK_RETEST;
      else if(inFiboZone && candleConfirmation)
         m_lastDiagnostic.classification = PAF_POSSIBLE_FIBO_PULLBACK;
      else if((nearSupport || nearResistance) && candleConfirmation)
         m_lastDiagnostic.classification = PAF_POSSIBLE_ZONE_REJECTION;
      else
         m_lastDiagnostic.classification = PAF_NO_SETUP;

      if(m_lastDiagnostic.classification == PAF_NO_SETUP)
         m_lastDiagnostic.reason = breakoutReason + "; " + retestReason + "; " + rejectionReason + "; " + engulfingReason;
      else
         m_lastDiagnostic.reason = "diagnostic setup detected; no trade signal emitted";
   }

public:
   CPriceActionFiboStrategy() : m_market(NULL)
   {
      ResetPAFDiagnosticState(m_lastDiagnostic);
   }

   void Init(CMarketData *market) { m_market = market; }

   bool DiagnosticsOnly() const
   {
      return InpPriceActionFiboDiagnosticsOnly;
   }

   string PlaceholderReason() const
   {
      return "PriceActionFibo diagnostic-only: no trade signal generated";
   }

   string DiagnosticSummary(const string actualSymbol,
                            const string canonicalSymbol,
                            const string timeframeName,
                            const string regimeName,
                            const int digits) const
   {
      return "PriceActionFibo diagnostic: actual=" + actualSymbol +
             " canonical=" + canonicalSymbol +
             " timeframe=" + timeframeName +
             " regime=" + regimeName +
             " swing_high_found=" + BoolText(m_lastDiagnostic.swingHighFound) +
             " swing_high=" + DoubleToString(m_lastDiagnostic.swingHigh, digits) +
             " swing_low_found=" + BoolText(m_lastDiagnostic.swingLowFound) +
             " swing_low=" + DoubleToString(m_lastDiagnostic.swingLow, digits) +
             " zone_found=" + BoolText(m_lastDiagnostic.zoneFound) +
             " support_zone=" + DoubleToString(m_lastDiagnostic.supportLow, digits) + "-" + DoubleToString(m_lastDiagnostic.supportHigh, digits) +
             " resistance_zone=" + DoubleToString(m_lastDiagnostic.resistanceLow, digits) + "-" + DoubleToString(m_lastDiagnostic.resistanceHigh, digits) +
             " fibo_zone_found=" + BoolText(m_lastDiagnostic.fiboZoneFound) +
             " fibo_levels=" + m_lastDiagnostic.fiboLevels +
             " fibo_zone=" + DoubleToString(m_lastDiagnostic.fiboLow, digits) + "-" + DoubleToString(m_lastDiagnostic.fiboHigh, digits) +
             " breakout=" + BoolText(m_lastDiagnostic.breakoutDetected) +
             " retest=" + BoolText(m_lastDiagnostic.retestDetected) +
             " rejection_candle=" + BoolText(m_lastDiagnostic.rejectionCandleDetected) +
             " engulfing_candle=" + BoolText(m_lastDiagnostic.engulfingCandleDetected) +
             " classification=" + ClassificationName(m_lastDiagnostic.classification) +
             " reason=" + m_lastDiagnostic.reason;
   }

   STradeSignal Evaluate(const SRegimeState &regime)
   {
      STradeSignal signal;
      ResetSignal(signal);

      // Checkpoint N diagnostics only. This module must not open market orders,
      // place pending orders, modify positions, or emit real entry signals.
      // Future implementation TODOs:
      // - risk/R-multiple integration
      // - setup quality scoring
      // - train/validation/out-of-sample telemetry comparison
      //
      // Symbol profile safety:
      // - EURUSD H1 is the first research baseline.
      // - Other forex pairs require separate train/validation/OOS validation.
      // - GOLD# / GOLDm# require separate broker-specific risk-budget review.
      // - Do not reuse EURUSD parameters automatically for Gold or other pairs.
      if(m_market == NULL || !InpEnablePriceActionFibo || regime.regime == REGIME_UNSAFE)
      {
         ResetPAFDiagnosticState(m_lastDiagnostic);
         m_lastDiagnostic.classification = PAF_INSUFFICIENT_DATA;
         m_lastDiagnostic.reason = "module disabled, market data missing, or unsafe regime";
         return signal;
      }

      EvaluateDiagnostics(regime);

      return signal;
   }
};

#endif
