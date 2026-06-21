#ifndef FOREX_AI_TRADE_TRADE_LOGGER_MQH
#define FOREX_AI_TRADE_TRADE_LOGGER_MQH

class CTradeLogger
{
private:
   bool   m_enabled;
   bool   m_useCommonFolder;
   string m_fileName;
   int    m_handle;

public:
   CTradeLogger()
   {
      m_enabled = false;
      m_useCommonFolder = true;
      m_fileName = "ForexAiTrade_smoke.log";
      m_handle = INVALID_HANDLE;
   }

   bool Init(const bool enabled, const bool useCommonFolder, const string fileName)
   {
      m_enabled = enabled;
      m_useCommonFolder = useCommonFolder;
      m_fileName = fileName;
      m_handle = INVALID_HANDLE;

      if(!m_enabled)
         return true;

      int flags = FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI;
      if(m_useCommonFolder)
         flags |= FILE_COMMON;

      ResetLastError();
      m_handle = FileOpen(m_fileName, flags);
      if(m_handle == INVALID_HANDLE)
      {
         Print("File log disabled: unable to open ", m_fileName, " error=", GetLastError());
         m_enabled = false;
         return false;
      }

      FileSeek(m_handle, 0, SEEK_END);
      Write("file log started file=" + m_fileName);
      return true;
   }

   void Release()
   {
      if(m_handle != INVALID_HANDLE)
      {
         Write("file log stopped");
         FileClose(m_handle);
      }

      m_handle = INVALID_HANDLE;
   }

   void Write(const string message)
   {
      if(!m_enabled || m_handle == INVALID_HANDLE)
         return;

      string line = TimeToString(TimeCurrent(), TIME_DATE | TIME_SECONDS) + " " + message;
      FileWrite(m_handle, line);
      FileFlush(m_handle);
   }

   string LocationHint() const
   {
      if(!m_enabled)
         return "disabled";

      if(m_useCommonFolder)
         return "Common\\Files\\" + m_fileName;

      return "MQL5\\Files\\" + m_fileName;
   }
};

#endif
