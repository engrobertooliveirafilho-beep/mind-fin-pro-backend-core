#property script_show_inputs
#property strict

input int InpBarsM15 = 5000;
input int InpBarsM30 = 5000;
input int InpBarsH1  = 5000;
input int InpBarsH4  = 3000;
input int InpBarsD1  = 1500;

string Symbols[] = {
   "EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","NZDUSD","USDCAD",
   "XAUUSD","US100","US500","GER40","UK100","JP225"
};

ENUM_TIMEFRAMES Tfs[] = {
   PERIOD_M15, PERIOD_M30, PERIOD_H1, PERIOD_H4, PERIOD_D1
};

string TfName(ENUM_TIMEFRAMES tf)
{
   if(tf==PERIOD_M15) return "M15";
   if(tf==PERIOD_M30) return "M30";
   if(tf==PERIOD_H1)  return "H1";
   if(tf==PERIOD_H4)  return "H4";
   if(tf==PERIOD_D1)  return "D1";
   return "UNK";
}

int BarsWanted(ENUM_TIMEFRAMES tf)
{
   if(tf==PERIOD_M15) return InpBarsM15;
   if(tf==PERIOD_M30) return InpBarsM30;
   if(tf==PERIOD_H1)  return InpBarsH1;
   if(tf==PERIOD_H4)  return InpBarsH4;
   if(tf==PERIOD_D1)  return InpBarsD1;
   return 1000;
}

void WriteManifestLine(int h,string symbol,string tf,string status,int rows,string file,int err)
{
   FileWrite(h,symbol,tf,status,rows,file,err,TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS));
}

void OnStart()
{
   string folder = "mind_ftmo_export";
   FolderCreate(folder,FILE_COMMON);

   string manifest = folder + "\\p2279b_export_manifest.csv";
   int mh = FileOpen(manifest,FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI);

   if(mh==INVALID_HANDLE)
   {
      Print("[P2279B] MANIFEST_OPEN_FAILED err=",GetLastError());
      return;
   }

   FileWrite(mh,"symbol","timeframe","status","rows","file","error","exported_at");

   for(int s=0; s<ArraySize(Symbols); s++)
   {
      string sym = Symbols[s];

      bool selected = SymbolSelect(sym,true);

      if(!selected)
      {
         WriteManifestLine(mh,sym,"ALL","SYMBOL_SELECT_FAILED",0,"",GetLastError());
         continue;
      }

      for(int t=0; t<ArraySize(Tfs); t++)
      {
         ENUM_TIMEFRAMES tf = Tfs[t];
         string tfname = TfName(tf);
         int want = BarsWanted(tf);

         MqlRates rates[];
         ArraySetAsSeries(rates,false);

         ResetLastError();
         int copied = CopyRates(sym,tf,0,want,rates);

         if(copied<=0)
         {
            WriteManifestLine(mh,sym,tfname,"NO_DATA",0,"",GetLastError());
            continue;
         }

         string file = folder + "\\MT5_" + sym + "_" + tfname + "_raw.csv";
         int h = FileOpen(file,FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI);

         if(h==INVALID_HANDLE)
         {
            WriteManifestLine(mh,sym,tfname,"FILE_OPEN_FAILED",0,file,GetLastError());
            continue;
         }

         FileWrite(h,"time","open","high","low","close","tick_volume","spread","real_volume");

         for(int i=0; i<copied; i++)
         {
            FileWrite(
               h,
               TimeToString(rates[i].time,TIME_DATE|TIME_MINUTES),
               DoubleToString(rates[i].open,_Digits),
               DoubleToString(rates[i].high,_Digits),
               DoubleToString(rates[i].low,_Digits),
               DoubleToString(rates[i].close,_Digits),
               rates[i].tick_volume,
               rates[i].spread,
               rates[i].real_volume
            );
         }

         FileClose(h);
         WriteManifestLine(mh,sym,tfname,"RAW_SAVED",copied,file,0);
         Print("[P2279B] RAW_SAVED ",sym," ",tfname," rows=",copied);
      }
   }

   FileClose(mh);
   Print("[P2279B] COMPLETE manifest=",manifest);
}
