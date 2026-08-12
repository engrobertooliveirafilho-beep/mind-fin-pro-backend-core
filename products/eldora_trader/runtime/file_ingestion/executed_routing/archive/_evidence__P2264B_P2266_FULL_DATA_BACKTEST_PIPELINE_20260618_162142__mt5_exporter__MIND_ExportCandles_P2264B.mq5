//+------------------------------------------------------------------+
//| MIND_ExportCandles_P2264B.mq5                                    |
//| Exporta candles OHLCV para Common\Files\mind_datasets            |
//+------------------------------------------------------------------+
#property strict
#property script_show_inputs

input string InpSymbols = "EURUSD,GBPUSD,USDJPY,USDCHF,USDCAD,AUDUSD,NZDUSD,EURJPY,GBPJPY,EURGBP,EURAUD,EURCAD,AUDJPY,CADJPY,XAUUSD,XAGUSD,USOIL,UKOIL,NGAS,US30,US100,US500,GER40,UK100,FRA40,JPN225,BTCUSD,ETHUSD,LTCUSD,XRPUSD,AAPL,MSFT,NVDA,TSLA,AMZN,META,GOOGL";
input int InpBars = 5000;

ENUM_TIMEFRAMES TFMap(string tf)
{
   if(tf=="M5") return PERIOD_M5;
   if(tf=="M15") return PERIOD_M15;
   if(tf=="M30") return PERIOD_M30;
   if(tf=="H1") return PERIOD_H1;
   if(tf=="H4") return PERIOD_H4;
   if(tf=="D1") return PERIOD_D1;
   return PERIOD_H1;
}

void ExportOne(string symbol,string tf)
{
   ENUM_TIMEFRAMES period = TFMap(tf);

   if(!SymbolSelect(symbol,true))
   {
      Print("[MIND_EXPORT] SYMBOL_SELECT_FAILED ",symbol);
      return;
   }

   MqlRates rates[];
   int copied = CopyRates(symbol,period,0,InpBars,rates);

   if(copied <= 0)
   {
      Print("[MIND_EXPORT] NO_DATA ",symbol," ",tf," err=",GetLastError());
      return;
   }

   string folder = "mind_datasets\\" + symbol;
   FolderCreate(folder,FILE_COMMON);

   string file = folder + "\\" + symbol + "_" + tf + ".csv";

   int h = FileOpen(file,FILE_WRITE|FILE_CSV|FILE_COMMON);

   if(h == INVALID_HANDLE)
   {
      Print("[MIND_EXPORT] FILE_OPEN_FAILED ",file," err=",GetLastError());
      return;
   }

   FileWrite(h,"time","open","high","low","close","volume");

   ArraySetAsSeries(rates,false);

   for(int i=0;i<copied;i++)
   {
      FileWrite(h,
         TimeToString(rates[i].time,TIME_DATE|TIME_MINUTES),
         DoubleToString(rates[i].open,_Digits),
         DoubleToString(rates[i].high,_Digits),
         DoubleToString(rates[i].low,_Digits),
         DoubleToString(rates[i].close,_Digits),
         (long)rates[i].tick_volume
      );
   }

   FileClose(h);

   Print("[MIND_EXPORT] OK ",symbol," ",tf," bars=",copied," file=",file);
}

void OnStart()
{
   string symbols[];
   int n = StringSplit(InpSymbols,',',symbols);

   string tfs[] = {"M5","M15","M30","H1","H4","D1"};

   for(int i=0;i<n;i++)
   {
      string s = symbols[i];
      StringTrimLeft(s);
      StringTrimRight(s);

      for(int j=0;j<ArraySize(tfs);j++)
      {
         ExportOne(s,tfs[j]);
      }
   }

   Print("[MIND_EXPORT] COMPLETE");
}
