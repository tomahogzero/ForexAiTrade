#ifndef FOREX_AI_TRADE_SYMBOL_HELPER_MQH
#define FOREX_AI_TRADE_SYMBOL_HELPER_MQH

#include "Inputs.mqh"

struct SSymbolMetadata
{
   string actualSymbol;
   string canonicalSymbol;
   int digits;
   double point;
   double tickSize;
   double tickValue;
   double contractSize;
   double volumeMin;
   double volumeMax;
   double volumeStep;
   int stopsLevel;
   int freezeLevel;
   long tradeMode;
   double spreadPoints;
   bool valid;
   string reason;
};

class CSymbolHelper
{
public:
   static string Clean(const string value)
   {
      string result = value;
      StringReplace(result, " ", "");
      StringReplace(result, "\t", "");
      StringReplace(result, "\r", "");
      StringReplace(result, "\n", "");
      return result;
   }

   static string Upper(const string value)
   {
      string result = value;
      StringToUpper(result);
      return result;
   }

   static bool EndsWith(const string value, const string suffix)
   {
      int valueLength = StringLen(value);
      int suffixLength = StringLen(suffix);
      if(suffixLength <= 0 || valueLength < suffixLength)
         return false;

      return StringSubstr(value, valueLength - suffixLength, suffixLength) == suffix;
   }

   static string RemoveTrailingBrokerMarks(const string value)
   {
      string result = value;
      while(StringLen(result) > 0)
      {
         string last = StringSubstr(result, StringLen(result) - 1, 1);
         if(last == "#" || last == "." || last == "m")
            result = StringSubstr(result, 0, StringLen(result) - 1);
         else
            break;
      }
      return result;
   }

   static bool IsSixLetterFx(const string value)
   {
      if(StringLen(value) != 6)
         return false;

      string upper = Upper(value);
      for(int i = 0; i < 6; ++i)
      {
         int ch = StringGetCharacter(upper, i);
         if(ch < 'A' || ch > 'Z')
            return false;
      }
      return true;
   }

   static string CanonicalSymbol(const string actualSymbol)
   {
      string overrideName = Upper(Clean(InpCanonicalSymbolName));
      if(overrideName != "")
         return overrideName;

      string actual = Clean(actualSymbol);
      string upperActual = Upper(actual);
      string configuredGold = Upper(Clean(InpBrokerGoldSymbolName));

      if(configuredGold != "" && upperActual == configuredGold)
         return "GOLD";

      if(StringFind(upperActual, "GOLD") == 0 || StringFind(upperActual, "XAU") == 0)
         return "GOLD";

      string base = Upper(RemoveTrailingBrokerMarks(actual));
      if(IsSixLetterFx(base))
         return base;

      return upperActual;
   }

   static double SpreadPoints(const string symbol)
   {
      double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
      double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
      double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
      if(point <= 0.0 || ask <= 0.0 || bid <= 0.0)
         return 0.0;
      return (ask - bid) / point;
   }

   static void LoadMetadata(const string symbol, SSymbolMetadata &metadata)
   {
      metadata.actualSymbol = symbol;
      metadata.canonicalSymbol = CanonicalSymbol(symbol);
      metadata.digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
      metadata.point = SymbolInfoDouble(symbol, SYMBOL_POINT);
      metadata.tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
      metadata.tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
      metadata.contractSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE);
      metadata.volumeMin = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
      metadata.volumeMax = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
      metadata.volumeStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
      metadata.stopsLevel = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL);
      metadata.freezeLevel = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_FREEZE_LEVEL);
      metadata.tradeMode = SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE);
      metadata.spreadPoints = SpreadPoints(symbol);
      ValidateMetadata(metadata);
   }

   static void ValidateMetadata(SSymbolMetadata &metadata)
   {
      metadata.valid = false;
      metadata.reason = "";

      if(metadata.actualSymbol == "")
      {
         metadata.reason = "actual symbol is empty";
         return;
      }

      if(metadata.point <= 0.0)
      {
         metadata.reason = "SYMBOL_POINT is invalid";
         return;
      }

      if(metadata.tickSize <= 0.0)
      {
         metadata.reason = "SYMBOL_TRADE_TICK_SIZE is invalid";
         return;
      }

      if(metadata.tickValue <= 0.0)
      {
         metadata.reason = "SYMBOL_TRADE_TICK_VALUE is invalid";
         return;
      }

      if(metadata.contractSize <= 0.0)
      {
         metadata.reason = "SYMBOL_TRADE_CONTRACT_SIZE is invalid";
         return;
      }

      if(metadata.volumeMin <= 0.0 || metadata.volumeMax <= 0.0 || metadata.volumeStep <= 0.0)
      {
         metadata.reason = "symbol volume min/max/step is invalid";
         return;
      }

      if(metadata.volumeMin > metadata.volumeMax)
      {
         metadata.reason = "SYMBOL_VOLUME_MIN exceeds SYMBOL_VOLUME_MAX";
         return;
      }

      if(metadata.stopsLevel < 0 || metadata.freezeLevel < 0)
      {
         metadata.reason = "stops or freeze level is invalid";
         return;
      }

      metadata.valid = true;
      metadata.reason = "ok";
   }

   static bool IsAllowed(const string actualSymbol, const string canonicalSymbol)
   {
      string csv = Clean(InpAllowedSymbolsCsv);
      if(csv == "")
         return true;

      string parts[];
      int count = StringSplit(csv, ',', parts);
      string actualUpper = Upper(actualSymbol);
      string canonicalUpper = Upper(canonicalSymbol);

      for(int i = 0; i < count; ++i)
      {
         string token = Upper(Clean(parts[i]));
         if(token == actualUpper || token == canonicalUpper)
            return true;
      }

      return false;
   }
};

#endif
