#ifndef FOREX_AI_TRADE_TYPES_MQH
#define FOREX_AI_TRADE_TYPES_MQH

enum EMarketRegime
{
   REGIME_UNSAFE = 0,
   REGIME_TREND = 1,
   REGIME_BREAKOUT = 2,
   REGIME_SIDEWAY = 3
};

enum ESignalDirection
{
   SIGNAL_NONE = 0,
   SIGNAL_BUY = 1,
   SIGNAL_SELL = -1
};

struct SRegimeState
{
   EMarketRegime regime;
   double adx;
   double atr;
   double atrPercent;
   double emaSlopePoints;
   double bbWidthPercent;
   double spreadPoints;
   string reason;
};

struct STradeSignal
{
   ESignalDirection direction;
   double stopLoss;
   double takeProfit;
   double confidence;
   string comment;
};

void ResetSignal(STradeSignal &signal)
{
   signal.direction = SIGNAL_NONE;
   signal.stopLoss = 0.0;
   signal.takeProfit = 0.0;
   signal.confidence = 0.0;
   signal.comment = "";
}

#endif
