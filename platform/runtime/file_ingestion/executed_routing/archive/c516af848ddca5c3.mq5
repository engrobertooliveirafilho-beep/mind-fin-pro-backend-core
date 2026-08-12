//+------------------------------------------------------------------+
//| MIND_OpenCharts_P2271.mq5                                        |
//| Abre gráficos dos ativos do portfolio paper                       |
//+------------------------------------------------------------------+
#property strict
#property script_show_inputs

input string InpSymbols = "GBPUSD";
input ENUM_TIMEFRAMES InpTimeframe = PERIOD_H1;

void OnStart()
{
   string symbols[];
   int n = StringSplit(InpSymbols, ',', symbols);

   for(int i=0; i<n; i++)
   {
      string s = symbols[i];
      StringTrimLeft(s);
      StringTrimRight(s);

      if(s == "") continue;

      if(!SymbolSelect(s, true))
      {
         Print("[MIND_OPEN_CHARTS] SYMBOL_SELECT_FAILED ", s);
         continue;
      }

      long chartId = ChartOpen(s, InpTimeframe);

      if(chartId > 0)
         Print("[MIND_OPEN_CHARTS] OPENED ", s);
      else
         Print("[MIND_OPEN_CHARTS] FAILED ", s, " err=", GetLastError());
   }

   Print("[MIND_OPEN_CHARTS] COMPLETE");
}
