#ifndef FOREX_AI_TRADE_EXIT_TELEMETRY_MQH
#define FOREX_AI_TRADE_EXIT_TELEMETRY_MQH

struct SExitTelemetryPending
{
   bool   active;
   string actualSymbol;
   string canonicalSymbol;
   string timeframe;
   string strategy;
   string regime;
   string direction;
   double entryPrice;
   double initialSl;
   double initialTp;
   double slDistancePoints;
   double tpDistancePoints;
   double initialRiskMoney;
   double lotSize;
   double spreadAtEntry;
   double atr;
   double rTarget;
   datetime signalTime;
};

struct SExitTelemetryPosition
{
   bool     active;
   ulong    positionId;
   string   actualSymbol;
   string   canonicalSymbol;
   string   timeframe;
   string   strategy;
   string   regime;
   string   direction;
   double   entryPrice;
   double   initialSl;
   double   initialTp;
   double   lastSl;
   double   lastTp;
   double   lastLoggedModifySl;
   double   lastLoggedModifyTp;
   double   slDistancePoints;
   double   tpDistancePoints;
   double   initialRiskMoney;
   double   lotSize;
   double   spreadAtEntry;
   double   atr;
   double   rTarget;
   datetime openTime;
};

class CExitTelemetry
{
private:
   bool   m_enabled;
   bool   m_useCommonFolder;
   string m_fileName;
   string m_locationHint;
   int    m_handle;
   string m_runId;
   string m_presetFile;
   double m_point;
   SExitTelemetryPending m_pending;
   SExitTelemetryPosition m_positions[];

   string Sanitize(string value) const
   {
      StringReplace(value, "#", "HASH");
      StringReplace(value, ".", "_");
      StringReplace(value, " ", "_");
      StringReplace(value, ":", "");
      StringReplace(value, "\\", "_");
      StringReplace(value, "/", "_");
      return value;
   }

   string BuildDefaultFileName(const string symbol, const string timeframe) const
   {
      return "ForexAiTrade_ExitTelemetry_" + Sanitize(symbol) + "_" + Sanitize(timeframe) + "_" +
             IntegerToString((int)InpMagicNumber) + ".csv";
   }

   void WriteHeader()
   {
      FileWrite(m_handle,
                "event", "timestamp", "run_id", "preset_file", "ticket", "position_id", "deal_id",
                "actual_symbol", "canonical_symbol", "timeframe", "strategy", "regime", "direction",
                "entry_price", "initial_sl", "initial_tp", "current_price", "close_price",
                "old_sl", "new_sl", "old_tp", "new_tp", "sl_distance_points", "tp_distance_points",
                "initial_risk_money", "lot_size", "spread_at_entry", "atr", "r_target",
                "unrealized_r", "profit", "duration_seconds", "final_sl", "final_tp",
                "realized_r", "exit_comment", "exit_classification", "classification_reason");
      FileFlush(m_handle);
   }

   int FindPositionIndex(const ulong positionId) const
   {
      for(int i = 0; i < ArraySize(m_positions); ++i)
      {
         if(m_positions[i].active && m_positions[i].positionId == positionId)
            return i;
      }
      return -1;
   }

   int AddOrUpdatePosition(const SExitTelemetryPosition &position)
   {
      int index = FindPositionIndex(position.positionId);
      if(index >= 0)
      {
         m_positions[index] = position;
         return index;
      }

      int size = ArraySize(m_positions);
      ArrayResize(m_positions, size + 1);
      m_positions[size] = position;
      return size;
   }

   string TimeStamp(const datetime value) const
   {
      return TimeToString(value, TIME_DATE | TIME_SECONDS);
   }

   double SafeR(const double money, const double riskMoney) const
   {
      if(riskMoney <= 0.0)
         return 0.0;
      return money / riskMoney;
   }

   bool StartsWith(const string value, const string prefix) const
   {
      return StringFind(value, prefix) == 0;
   }

   bool CloseEnough(const double a, const double b) const
   {
      if(a <= 0.0 || b <= 0.0)
         return false;
      double tolerance = MathMax(m_point * 5.0, 0.0000001);
      return MathAbs(a - b) <= tolerance;
   }

   string ClassifyExit(const string comment,
                       const double profit,
                       const double realizedR,
                       const double finalSl,
                       const double initialSl,
                       string &reason) const
   {
      string lower = comment;
      StringToLower(lower);

      if(StartsWith(lower, "tp"))
      {
         reason = "close comment starts with tp";
         return "TP_HIT";
      }

      if(StartsWith(lower, "sl"))
      {
         if(profit > 0.0)
         {
            reason = "sl close with positive profit";
            return "TRAILING_SL_PROFIT";
         }
         if(MathAbs(realizedR) <= 0.10 || MathAbs(profit) <= 1.0)
         {
            reason = "sl close near breakeven";
            return "BREAKEVEN_SL";
         }
         if(CloseEnough(finalSl, initialSl) || profit < 0.0)
         {
            reason = "sl close with negative profit";
            return "INITIAL_SL_LOSS";
         }
         reason = "sl close but unable to distinguish initial/trailing stop";
         return "UNKNOWN";
      }

      if(StringLen(comment) > 0)
      {
         reason = "non sl/tp close comment";
         return "OTHER_CLOSE";
      }

      reason = "missing close comment";
      return "UNKNOWN";
   }

   void WriteEvent(const string eventName,
                   const datetime timestamp,
                   const ulong ticket,
                   const ulong positionId,
                   const ulong dealId,
                   const string actualSymbol,
                   const string canonicalSymbol,
                   const string timeframe,
                   const string strategy,
                   const string regime,
                   const string direction,
                   const double entryPrice,
                   const double initialSl,
                   const double initialTp,
                   const double currentPrice,
                   const double closePrice,
                   const double oldSl,
                   const double newSl,
                   const double oldTp,
                   const double newTp,
                   const double slDistancePoints,
                   const double tpDistancePoints,
                   const double initialRiskMoney,
                   const double lotSize,
                   const double spreadAtEntry,
                   const double atr,
                   const double rTarget,
                   const double unrealizedR,
                   const double profit,
                   const long durationSeconds,
                   const double finalSl,
                   const double finalTp,
                   const double realizedR,
                   const string exitComment,
                   const string exitClassification,
                   const string classificationReason)
   {
      if(!m_enabled || m_handle == INVALID_HANDLE)
         return;

      FileWrite(m_handle,
                eventName, TimeStamp(timestamp), m_runId, m_presetFile,
                (string)ticket, (string)positionId, (string)dealId,
                actualSymbol, canonicalSymbol, timeframe, strategy, regime, direction,
                entryPrice, initialSl, initialTp, currentPrice, closePrice,
                oldSl, newSl, oldTp, newTp, slDistancePoints, tpDistancePoints,
                initialRiskMoney, lotSize, spreadAtEntry, atr, rTarget,
                unrealizedR, profit, durationSeconds, finalSl, finalTp,
                realizedR, exitComment, exitClassification, classificationReason);
      FileFlush(m_handle);
   }

public:
   CExitTelemetry()
   {
      m_enabled = false;
      m_useCommonFolder = true;
      m_fileName = "";
      m_locationHint = "disabled";
      m_handle = INVALID_HANDLE;
      m_runId = "";
      m_presetFile = "";
      m_point = 0.0;
      m_pending.active = false;
   }

   bool Init(const bool enabled,
             const bool useCommonFolder,
             const string fileName,
             const string actualSymbol,
             const string canonicalSymbol,
             const ENUM_TIMEFRAMES timeframe,
             const string presetFile,
             const double point)
   {
      m_enabled = enabled;
      m_useCommonFolder = useCommonFolder;
      m_presetFile = presetFile;
      m_point = point;
      m_fileName = fileName;
      if(m_fileName == "")
         m_fileName = BuildDefaultFileName(actualSymbol, EnumToString(timeframe));
      m_runId = m_fileName;
      StringReplace(m_runId, "ForexAiTrade_ExitTelemetry_", "");
      StringReplace(m_runId, ".csv", "");
      m_locationHint = "disabled";
      m_handle = INVALID_HANDLE;
      m_pending.active = false;
      ArrayResize(m_positions, 0);

      if(!m_enabled)
         return true;

      int flags = FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI;
      if(m_useCommonFolder)
         flags |= FILE_COMMON;

      ResetLastError();
      m_handle = FileOpen(m_fileName, flags, ',');
      if(m_handle == INVALID_HANDLE)
      {
         Print("Exit telemetry disabled: unable to open ", m_fileName, " error=", GetLastError());
         m_enabled = false;
         return false;
      }

      if(FileSize(m_handle) == 0)
         WriteHeader();
      FileSeek(m_handle, 0, SEEK_END);
      m_locationHint = (m_useCommonFolder ? "Common\\Files\\" : "MQL5\\Files\\") + m_fileName;
      return true;
   }

   void Release()
   {
      if(m_handle != INVALID_HANDLE)
         FileClose(m_handle);
      m_handle = INVALID_HANDLE;
   }

   string LocationHint() const
   {
      return m_locationHint;
   }

   void ClearPending()
   {
      m_pending.active = false;
   }

   void SetPendingOpen(const string actualSymbol,
                       const string canonicalSymbol,
                       const string timeframe,
                       const string strategy,
                       const string regime,
                       const string direction,
                       const double entryPrice,
                       const double initialSl,
                       const double initialTp,
                       const double slDistancePoints,
                       const double tpDistancePoints,
                       const double initialRiskMoney,
                       const double lotSize,
                       const double spreadAtEntry,
                       const double atr,
                       const double rTarget)
   {
      if(!m_enabled)
         return;

      m_pending.active = true;
      m_pending.actualSymbol = actualSymbol;
      m_pending.canonicalSymbol = canonicalSymbol;
      m_pending.timeframe = timeframe;
      m_pending.strategy = strategy;
      m_pending.regime = regime;
      m_pending.direction = direction;
      m_pending.entryPrice = entryPrice;
      m_pending.initialSl = initialSl;
      m_pending.initialTp = initialTp;
      m_pending.slDistancePoints = slDistancePoints;
      m_pending.tpDistancePoints = tpDistancePoints;
      m_pending.initialRiskMoney = initialRiskMoney;
      m_pending.lotSize = lotSize;
      m_pending.spreadAtEntry = spreadAtEntry;
      m_pending.atr = atr;
      m_pending.rTarget = rTarget;
      m_pending.signalTime = TimeCurrent();
   }

   double UnrealizedR(const ulong positionId, const double currentPrice) const
   {
      int index = FindPositionIndex(positionId);
      if(index < 0 || m_positions[index].initialRiskMoney <= 0.0 || m_positions[index].lotSize <= 0.0)
         return 0.0;

      double directionSign = m_positions[index].direction == "buy" ? 1.0 : -1.0;
      double priceMove = (currentPrice - m_positions[index].entryPrice) * directionSign;
      double initialDistance = MathAbs(m_positions[index].entryPrice - m_positions[index].initialSl);
      if(initialDistance <= 0.0)
         return 0.0;
      return priceMove / initialDistance;
   }

   void LogPositionModify(const ulong ticket,
                          const ulong positionId,
                          const string reason,
                          const double oldSl,
                          const double newSl,
                          const double oldTp,
                          const double newTp,
                          const double currentPrice)
   {
      if(!m_enabled || !InpLogPositionModifyEvents)
         return;

      int index = FindPositionIndex(positionId);
      string actualSymbol = "";
      string canonicalSymbol = "";
      string timeframe = "";
      string strategy = "";
      string regime = "";
      string direction = "";
      double entryPrice = 0.0;
      double initialSl = 0.0;
      double initialTp = 0.0;
      double slDistancePoints = 0.0;
      double tpDistancePoints = 0.0;
      double initialRiskMoney = 0.0;
      double lotSize = 0.0;
      double spreadAtEntry = 0.0;
      double atr = 0.0;
      double rTarget = 0.0;

      if(index >= 0)
      {
         bool shouldLogModify = true;
         if(InpExitTelemetryMinModifyStepPoints > 0.0 && m_point > 0.0)
         {
            double minStep = InpExitTelemetryMinModifyStepPoints * m_point;
            bool slChangedEnough = (m_positions[index].lastLoggedModifySl <= 0.0 ||
                                    MathAbs(newSl - m_positions[index].lastLoggedModifySl) >= minStep);
            bool tpChangedEnough = (m_positions[index].lastLoggedModifyTp <= 0.0 ||
                                    MathAbs(newTp - m_positions[index].lastLoggedModifyTp) >= minStep);
            shouldLogModify = slChangedEnough || tpChangedEnough;
         }
         m_positions[index].lastSl = newSl;
         m_positions[index].lastTp = newTp;
         if(!shouldLogModify)
            return;
         m_positions[index].lastLoggedModifySl = newSl;
         m_positions[index].lastLoggedModifyTp = newTp;
         actualSymbol = m_positions[index].actualSymbol;
         canonicalSymbol = m_positions[index].canonicalSymbol;
         timeframe = m_positions[index].timeframe;
         strategy = m_positions[index].strategy;
         regime = m_positions[index].regime;
         direction = m_positions[index].direction;
         entryPrice = m_positions[index].entryPrice;
         initialSl = m_positions[index].initialSl;
         initialTp = m_positions[index].initialTp;
         slDistancePoints = m_positions[index].slDistancePoints;
         tpDistancePoints = m_positions[index].tpDistancePoints;
         initialRiskMoney = m_positions[index].initialRiskMoney;
         lotSize = m_positions[index].lotSize;
         spreadAtEntry = m_positions[index].spreadAtEntry;
         atr = m_positions[index].atr;
         rTarget = m_positions[index].rTarget;
      }

      WriteEvent("MODIFY", TimeCurrent(), ticket, positionId, 0,
                 actualSymbol, canonicalSymbol, timeframe, strategy, regime, direction,
                 entryPrice, initialSl, initialTp, currentPrice, 0.0,
                 oldSl, newSl, oldTp, newTp, slDistancePoints, tpDistancePoints,
                 initialRiskMoney, lotSize, spreadAtEntry, atr, rTarget,
                 UnrealizedR(positionId, currentPrice), 0.0, 0, newSl, newTp,
                 0.0, "", "", reason);
   }

   void OnTradeTransaction(const MqlTradeTransaction &trans)
   {
      if(!m_enabled || trans.type != TRADE_TRANSACTION_DEAL_ADD || trans.deal == 0)
         return;

      if(!HistoryDealSelect(trans.deal))
         return;

      string symbol = HistoryDealGetString(trans.deal, DEAL_SYMBOL);
      long magic = (long)HistoryDealGetInteger(trans.deal, DEAL_MAGIC);
      if(magic != InpMagicNumber)
         return;

      ENUM_DEAL_ENTRY entry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(trans.deal, DEAL_ENTRY);
      ulong positionId = (ulong)HistoryDealGetInteger(trans.deal, DEAL_POSITION_ID);
      ulong orderId = (ulong)HistoryDealGetInteger(trans.deal, DEAL_ORDER);
      ENUM_DEAL_TYPE dealType = (ENUM_DEAL_TYPE)HistoryDealGetInteger(trans.deal, DEAL_TYPE);
      datetime dealTime = (datetime)HistoryDealGetInteger(trans.deal, DEAL_TIME);
      double dealPrice = HistoryDealGetDouble(trans.deal, DEAL_PRICE);
      double volume = HistoryDealGetDouble(trans.deal, DEAL_VOLUME);
      string direction = dealType == DEAL_TYPE_BUY ? "buy" : (dealType == DEAL_TYPE_SELL ? "sell" : "");

      if(entry == DEAL_ENTRY_IN)
      {
         SExitTelemetryPosition position;
         position.active = true;
         position.positionId = positionId;
         position.actualSymbol = m_pending.active ? m_pending.actualSymbol : symbol;
         position.canonicalSymbol = m_pending.active ? m_pending.canonicalSymbol : symbol;
         position.timeframe = m_pending.active ? m_pending.timeframe : "";
         position.strategy = m_pending.active ? m_pending.strategy : HistoryDealGetString(trans.deal, DEAL_COMMENT);
         position.regime = m_pending.active ? m_pending.regime : "";
         position.direction = m_pending.active ? m_pending.direction : direction;
         position.entryPrice = dealPrice > 0.0 ? dealPrice : m_pending.entryPrice;
         position.initialSl = m_pending.active ? m_pending.initialSl : 0.0;
         position.initialTp = m_pending.active ? m_pending.initialTp : 0.0;
         position.lastSl = position.initialSl;
         position.lastTp = position.initialTp;
         position.lastLoggedModifySl = 0.0;
         position.lastLoggedModifyTp = 0.0;
         position.slDistancePoints = m_pending.active ? m_pending.slDistancePoints : 0.0;
         position.tpDistancePoints = m_pending.active ? m_pending.tpDistancePoints : 0.0;
         position.initialRiskMoney = m_pending.active ? m_pending.initialRiskMoney : 0.0;
         position.lotSize = volume;
         position.spreadAtEntry = m_pending.active ? m_pending.spreadAtEntry : 0.0;
         position.atr = m_pending.active ? m_pending.atr : 0.0;
         position.rTarget = m_pending.active ? m_pending.rTarget : 0.0;
         position.openTime = dealTime;
         AddOrUpdatePosition(position);

         WriteEvent("OPEN", dealTime, orderId, positionId, trans.deal,
                    position.actualSymbol, position.canonicalSymbol, position.timeframe,
                    position.strategy, position.regime, position.direction,
                    position.entryPrice, position.initialSl, position.initialTp,
                    position.entryPrice, 0.0, 0.0, position.initialSl, 0.0, position.initialTp,
                    position.slDistancePoints, position.tpDistancePoints, position.initialRiskMoney,
                    position.lotSize, position.spreadAtEntry, position.atr, position.rTarget,
                    0.0, 0.0, 0, position.initialSl, position.initialTp, 0.0,
                    "", "", "open deal");
         ClearPending();
         return;
      }

      if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY)
         return;

      int index = FindPositionIndex(positionId);
      SExitTelemetryPosition position;
      position.active = false;
      position.positionId = positionId;
      position.actualSymbol = symbol;
      position.canonicalSymbol = symbol;
      position.timeframe = "";
      position.strategy = "";
      position.regime = "";
      position.direction = direction;
      position.entryPrice = 0.0;
      position.initialSl = 0.0;
      position.initialTp = 0.0;
      position.lastSl = 0.0;
      position.lastTp = 0.0;
      position.lastLoggedModifySl = 0.0;
      position.lastLoggedModifyTp = 0.0;
      position.slDistancePoints = 0.0;
      position.tpDistancePoints = 0.0;
      position.initialRiskMoney = 0.0;
      position.lotSize = volume;
      position.spreadAtEntry = 0.0;
      position.atr = 0.0;
      position.rTarget = 0.0;
      position.openTime = 0;

      if(index >= 0)
         position = m_positions[index];

      double profit = HistoryDealGetDouble(trans.deal, DEAL_PROFIT) +
                      HistoryDealGetDouble(trans.deal, DEAL_SWAP) +
                      HistoryDealGetDouble(trans.deal, DEAL_COMMISSION);
      long duration = 0;
      if(position.openTime > 0 && dealTime >= position.openTime)
         duration = (long)(dealTime - position.openTime);

      double realizedR = InpLogRMultipleOnClose ? SafeR(profit, position.initialRiskMoney) : 0.0;
      string comment = HistoryDealGetString(trans.deal, DEAL_COMMENT);
      string classificationReason = "";
      string classification = ClassifyExit(comment, profit, realizedR, position.lastSl, position.initialSl, classificationReason);

      WriteEvent("CLOSE", dealTime, orderId, positionId, trans.deal,
                 position.actualSymbol, position.canonicalSymbol, position.timeframe,
                 position.strategy, position.regime, position.direction,
                 position.entryPrice, position.initialSl, position.initialTp,
                 dealPrice, dealPrice, 0.0, 0.0, 0.0, 0.0,
                 position.slDistancePoints, position.tpDistancePoints, position.initialRiskMoney,
                 position.lotSize, position.spreadAtEntry, position.atr, position.rTarget,
                 0.0, profit, duration, position.lastSl, position.lastTp, realizedR,
                 comment, classification, classificationReason);

      if(index >= 0)
         m_positions[index].active = false;
   }
};

#endif
