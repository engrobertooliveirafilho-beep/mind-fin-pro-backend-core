#property strict
#property script_show_inputs
#property version "1.001"

input int MaximumBars = 1000000;
input int MaximumPumpCycles = 30;
input int StableCyclesRequired = 5;
input int DelayBetweenCyclesMs = 1500;
input int FlushEveryBars = 10000;

string CanonicalSymbols[] =
{
   "AUDCAD",
   "AUDCHF",
   "AUDJPY",
   "AUDNZD",
   "AUDUSD",

   "CADCHF",
   "CADJPY",

   "CHFJPY",

   "EURAUD",
   "EURCAD",
   "EURCHF",
   "EURGBP",
   "EURJPY",
   "EURNZD",
   "EURUSD",

   "GBPAUD",
   "GBPCAD",
   "GBPCHF",
   "GBPJPY",
   "GBPNZD",
   "GBPUSD",

   "NZDCAD",
   "NZDCHF",
   "NZDJPY",
   "NZDUSD",

   "USDCAD",
   "USDCHF",
   "USDJPY",

   "AUS200.cash",
   "EU50.cash",
   "GER40.cash",
   "HK50.cash",
   "JP225.cash",
   "UK100.cash",
   "US30.cash",
   "US100.cash",
   "US2000.cash",
   "US500.cash",

   "ADAUSD",
   "BTCUSD",
   "DASHUSD",
   "DOGEUSD",
   "DOTUSD",
   "ETHUSD",
   "LTCUSD",
   "NEOUSD",
   "XMRUSD",
   "XRPUSD",

   "XAGUSD",
   "XAUUSD",
   "XPDUSD",
   "XPTUSD",

   "UKOIL.cash",
   "USOIL.cash",

   "COCOA.c",
   "COFFEE.c",
   "SOYBEAN.c",
   "WHEAT.c"
};

string NormalizeSymbol(string value)
{
   StringToUpper(value);

   StringReplace(value, ".", "");
   StringReplace(value, "_", "");
   StringReplace(value, "-", "");
   StringReplace(value, "/", "");
   StringReplace(value, " ", "");

   return value;
}

string SafeFilename(string value)
{
   StringReplace(value, ".", "_");
   StringReplace(value, "/", "_");
   StringReplace(value, "\\", "_");
   StringReplace(value, ":", "_");
   StringReplace(value, " ", "_");

   return value;
}

bool AccountGate()
{
   long login = AccountInfoInteger(ACCOUNT_LOGIN);
   string server = AccountInfoString(ACCOUNT_SERVER);

   Print(
      "[ACCOUNT] LOGIN=",
      login,
      " SERVER=",
      server
   );

   if(login <= 0)
   {
      Print("[ACCOUNT_GATE_FAIL] LOGIN_NOT_AUTHENTICATED");
      return false;
   }

   if(StringFind(server, "FTMO") < 0)
   {
      Print(
         "[ACCOUNT_GATE_FAIL] NON_FTMO_SERVER=",
         server
      );

      return false;
   }

   Print("[ACCOUNT_GATE_PASS]");
   return true;
}

string ResolveBrokerSymbol(string canonical)
{
   bool isCustomSymbol = false;

   if(SymbolExist(canonical, isCustomSymbol))
      return canonical;

   string normalizedCanonical = NormalizeSymbol(canonical);
   int total = SymbolsTotal(false);

   for(int i = 0; i < total; i++)
   {
      string candidate = SymbolName(i, false);

      if(
         NormalizeSymbol(candidate)
         ==
         normalizedCanonical
      )
      {
         return candidate;
      }
   }

   total = SymbolsTotal(true);

   for(int i = 0; i < total; i++)
   {
      string candidate = SymbolName(i, true);

      if(
         NormalizeSymbol(candidate)
         ==
         normalizedCanonical
      )
      {
         return candidate;
      }
   }

   return "";
}

int PumpM1History(string symbol)
{
   int previousBars = -1;
   int stableCycles = 0;
   int currentBars = 0;

   for(
      int cycle = 1;
      cycle <= MaximumPumpCycles;
      cycle++
   )
   {
      ResetLastError();

      MqlRates rates[];
      ArraySetAsSeries(rates, false);

      currentBars = CopyRates(
         symbol,
         PERIOD_M1,
         0,
         MaximumBars,
         rates
      );

      int errorCode = GetLastError();

      if(currentBars < 0)
         currentBars = 0;

      Print(
         "[PUMP] SYMBOL=",
         symbol,
         " CYCLE=",
         cycle,
         " BARS=",
         currentBars,
         " PREVIOUS=",
         previousBars,
         " STABLE=",
         stableCycles,
         " ERROR=",
         errorCode
      );

      if(
         currentBars > 0
         &&
         currentBars == previousBars
      )
      {
         stableCycles++;
      }
      else
      {
         stableCycles = 0;
      }

      if(
         currentBars > 0
         &&
         stableCycles >= StableCyclesRequired
      )
      {
         Print(
            "[HISTORY_STABLE] SYMBOL=",
            symbol,
            " BARS=",
            currentBars,
            " CYCLE=",
            cycle
         );

         return currentBars;
      }

      previousBars = currentBars;
      Sleep(DelayBetweenCyclesMs);
   }

   Print(
      "[BROKER_LIMIT_OR_TIMEOUT] SYMBOL=",
      symbol,
      " BARS=",
      currentBars
   );

   return currentBars;
}

bool ExportM1(
   string canonical,
   string brokerSymbol,
   int manifestHandle
)
{
   ResetLastError();

   MqlRates rates[];
   ArraySetAsSeries(rates, false);

   int copied = CopyRates(
      brokerSymbol,
      PERIOD_M1,
      0,
      MaximumBars,
      rates
   );

   int copyError = GetLastError();

   if(copied <= 0)
   {
      FileWrite(
         manifestHandle,
         canonical,
         brokerSymbol,
         "NO_DATA",
         0,
         "",
         "",
         copyError
      );

      FileFlush(manifestHandle);
      return false;
   }

   string safe = SafeFilename(canonical);

   string partialFile =
      "TRADER_1_001\\"
      + safe
      + "_M1_WRITING.csv";

   string finalFile =
      "TRADER_1_001\\"
      + safe
      + "_M1.csv";

   int outputHandle = FileOpen(
      partialFile,
      FILE_WRITE
      |
      FILE_CSV
      |
      FILE_ANSI,
      ','
   );

   if(outputHandle == INVALID_HANDLE)
   {
      FileWrite(
         manifestHandle,
         canonical,
         brokerSymbol,
         "FILE_OPEN_FAILED",
         copied,
         "",
         "",
         GetLastError()
      );

      FileFlush(manifestHandle);
      return false;
   }

   int digits = (int)SymbolInfoInteger(
      brokerSymbol,
      SYMBOL_DIGITS
   );

   FileWrite(
      outputHandle,
      "timestamp",
      "canonical_symbol",
      "broker_symbol",
      "timeframe",
      "open",
      "high",
      "low",
      "close",
      "tick_volume",
      "spread",
      "real_volume",
      "source",
      "mode"
   );

   for(int i = 0; i < copied; i++)
   {
      FileWrite(
         outputHandle,
         TimeToString(
            rates[i].time,
            TIME_DATE
            |
            TIME_MINUTES
            |
            TIME_SECONDS
         ),
         canonical,
         brokerSymbol,
         "M1",
         DoubleToString(rates[i].open, digits),
         DoubleToString(rates[i].high, digits),
         DoubleToString(rates[i].low, digits),
         DoubleToString(rates[i].close, digits),
         (long)rates[i].tick_volume,
         rates[i].spread,
         (long)rates[i].real_volume,
         "FTMO_MT5_NATIVE",
         "BACKTEST_PAPER_ONLY"
      );

      if(
         FlushEveryBars > 0
         &&
         i > 0
         &&
         i % FlushEveryBars == 0
      )
      {
         FileFlush(outputHandle);
      }
   }

   FileFlush(outputHandle);
   FileClose(outputHandle);

   ResetLastError();

   bool renamed = FileMove(
      partialFile,
      0,
      finalFile,
      FILE_REWRITE
   );

   if(!renamed)
   {
      FileWrite(
         manifestHandle,
         canonical,
         brokerSymbol,
         "RENAME_FAILED",
         copied,
         "",
         "",
         GetLastError()
      );

      FileFlush(manifestHandle);
      return false;
   }

   string firstTime = TimeToString(
      rates[0].time,
      TIME_DATE
      |
      TIME_MINUTES
      |
      TIME_SECONDS
   );

   string lastTime = TimeToString(
      rates[copied - 1].time,
      TIME_DATE
      |
      TIME_MINUTES
      |
      TIME_SECONDS
   );

   string status = "STABLE_AVAILABLE_HISTORY";

   if(copied >= MaximumBars)
      status = "MAXIMUM_BARS_REACHED";

   FileWrite(
      manifestHandle,
      canonical,
      brokerSymbol,
      status,
      copied,
      firstTime,
      lastTime,
      0
   );

   FileFlush(manifestHandle);
   return true;
}

void OnStart()
{
   Print("==================================================");
   Print("TRADER.1.001 FTMO M1 SATURATION START");
   Print("MODE=BACKTEST_PAPER_ONLY");
   Print("LIVE_REAL=FORBIDDEN");
   Print("==================================================");

   if(!AccountGate())
   {
      Alert(
         "Trader.1.001 bloqueado: "
         "abra uma conta FTMO autenticada."
      );

      return;
   }

   FolderCreate("TRADER_1_001");

   string manifestPartial =
      "TRADER_1_001\\"
      "TRADER_1_001_M1_MANIFEST_WRITING.csv";

   string manifestFinal =
      "TRADER_1_001\\"
      "TRADER_1_001_M1_MANIFEST.csv";

   int manifest = FileOpen(
      manifestPartial,
      FILE_WRITE
      |
      FILE_CSV
      |
      FILE_ANSI,
      ','
   );

   if(manifest == INVALID_HANDLE)
   {
      Print(
         "[MANIFEST_OPEN_FAILED] ERROR=",
         GetLastError()
      );

      return;
   }

   FileWrite(
      manifest,
      "canonical_symbol",
      "broker_symbol",
      "status",
      "bars_m1",
      "first_timestamp",
      "last_timestamp",
      "error"
   );

   int total = ArraySize(CanonicalSymbols);
   int resolved = 0;
   int exported = 0;
   int unavailable = 0;

   for(int i = 0; i < total; i++)
   {
      string canonical = CanonicalSymbols[i];

      Comment(
         "TRADER.1.001",
         "\nAtivo: ",
         i + 1,
         "/",
         total,
         "\nCanônico: ",
         canonical,
         "\nExportados: ",
         exported,
         "\nBACKTEST/PAPER_ONLY"
      );

      string brokerSymbol = ResolveBrokerSymbol(
         canonical
      );

      if(brokerSymbol == "")
      {
         unavailable++;

         FileWrite(
            manifest,
            canonical,
            "",
            "SYMBOL_NOT_AVAILABLE",
            0,
            "",
            "",
            4301
         );

         FileFlush(manifest);

         Print(
            "[SYMBOL_NOT_AVAILABLE] CANONICAL=",
            canonical
         );

         continue;
      }

      resolved++;

      if(!SymbolSelect(brokerSymbol, true))
      {
         FileWrite(
            manifest,
            canonical,
            brokerSymbol,
            "SYMBOL_SELECT_FAILED",
            0,
            "",
            "",
            GetLastError()
         );

         FileFlush(manifest);
         continue;
      }

      PumpM1History(brokerSymbol);

      if(
         ExportM1(
            canonical,
            brokerSymbol,
            manifest
         )
      )
      {
         exported++;
      }

      Print(
         "[GLOBAL] CURRENT=",
         i + 1,
         "/",
         total,
         " RESOLVED=",
         resolved,
         " EXPORTED=",
         exported,
         " UNAVAILABLE=",
         unavailable
      );
   }

   FileFlush(manifest);
   FileClose(manifest);

   bool manifestRenamed = FileMove(
      manifestPartial,
      0,
      manifestFinal,
      FILE_REWRITE
   );

   bool exportRunComplete = (exported == total && unavailable == 0 && manifestRenamed);

   int marker = FileOpen(
      "TRADER_1_001\\"
      "TRADER_1_001_M1_COMPLETE.txt",
      FILE_WRITE
      |
      FILE_TXT
      |
      FILE_ANSI
   );

   if(marker != INVALID_HANDLE)
   {
      FileWrite(marker, "STATUS=" + (exportRunComplete ? "EXPORT_RUN_COMPLETE" : "EXPORT_RUN_INCOMPLETE"));
      FileWrite(
         marker,
         "CANONICAL_ASSETS="
         + IntegerToString(total)
      );

      FileWrite(
         marker,
         "RESOLVED="
         + IntegerToString(resolved)
      );

      FileWrite(
         marker,
         "EXPORTED="
         + IntegerToString(exported)
      );

      FileWrite(
         marker,
         "UNAVAILABLE="
         + IntegerToString(unavailable)
      );

      FileWrite(
         marker,
         "MANIFEST_RENAMED="
         + (
            manifestRenamed
            ? "TRUE"
            : "FALSE"
         )
      );

      FileWrite(
         marker,
         "MODE=BACKTEST_PAPER_ONLY"
      );

      FileWrite(
         marker,
         "LIVE_REAL=FORBIDDEN"
      );

      FileClose(marker);
   }

   Comment("");

   Print("==================================================");
   Print("TRADER.1.001 FTMO M1 SATURATION FINISHED");
   Print("CANONICAL_ASSETS=", total);
   Print("RESOLVED=", resolved);
   Print("EXPORTED=", exported);
   Print("UNAVAILABLE=", unavailable);
   Print("EXPORT_RUN_STATUS=", exportRunComplete ? "COMPLETE" : "INCOMPLETE");
   Print("MANIFEST_RENAMED=", manifestRenamed ? "TRUE" : "FALSE");
   Print("LIVE_REAL=FORBIDDEN");
   Print("==================================================");

   Alert(
      "Trader.1.001 ",
      exportRunComplete ? "COMPLETO" : "INCOMPLETO",
      ". Exportados: ",
      exported,
      "/",
      total
   );
}
