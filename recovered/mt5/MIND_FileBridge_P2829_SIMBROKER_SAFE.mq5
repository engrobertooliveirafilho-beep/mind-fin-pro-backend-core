#property strict
#property version "2.829"
input string SignalFileName = "mt5_order.txt";
input string LedgerFileName = "MIND_SIM_BROKER_LEDGER.csv";
input int TimerSeconds = 1;
input int MagicNumber = 2829;
string PREFIX = "[MIND_P2829] ";
string last_raw = "";
int OnInit()
{
   Print(PREFIX+"EA_INITIALIZED MODE=SIM_BROKER REAL_ORDERS=FORBIDDEN");
   if(TimerSeconds < 1) return INIT_PARAMETERS_INCORRECT;
   EnsureLedgerHeader();
   EventSetTimer(TimerSeconds);
   return INIT_SUCCEEDED;
}
void OnDeinit(const int reason) { EventKillTimer(); }
string T(string s) { StringTrimLeft(s); StringTrimRight(s); return s; }
void EnsureLedgerHeader()
{
   if(FileIsExist(LedgerFileName, FILE_COMMON)) return;
   int h=FileOpen(LedgerFileName,FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h==INVALID_HANDLE) { Print(PREFIX+"LEDGER_HEADER_FAIL"); return; }
   FileWriteString(h,"server_time,symbol,side,lot,entry_price,tag,status,mode,magic,raw\n");
   FileClose(h);
}
bool SimAccept(string symbol,string side,double lot,double price,string tag,string raw)
{
   int h=FileOpen(LedgerFileName,FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h==INVALID_HANDLE) { Print(PREFIX+"SIM_LEDGER_OPEN_FAIL"); return false; }
   FileSeek(h,0,SEEK_END);
   string row=TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS)+","+
      symbol+","+side+","+DoubleToString(lot,2)+","+
      DoubleToString(price,(int)SymbolInfoInteger(symbol,SYMBOL_DIGITS))+","+
      tag+",ACCEPTED,SIM_BROKER,"+IntegerToString(MagicNumber)+","+raw+"\n";
   uint written=FileWriteString(h,row);
   FileFlush(h);
   FileClose(h);
   if(written!=StringLen(row)) { Print(PREFIX+"SIM_LEDGER_WRITE_FAIL"); return false; }
   Print(PREFIX+"SIM_LEDGER_WRITTEN symbol="+symbol);
   return true;
}
void OnTimer()
{
   int h=FileOpen(SignalFileName,FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h==INVALID_HANDLE) return;
   string raw="";
   while(!FileIsEnding(h))
   {
      string line=T(FileReadString(h));
      if(line!="") { raw=line; break; }
   }
   FileClose(h);
   if(raw=="" || raw==last_raw) return;
   string p[];
   if(StringSplit(raw,',',p)!=4) { Print(PREFIX+"PARSE_REJECT"); return; }
   string symbol=T(p[0]), side=T(p[1]), lot_raw=T(p[2]), tag=T(p[3]);
   StringToUpper(side);
   if(symbol=="" || tag=="" || (side!="BUY" && side!="SELL"))
   { Print(PREFIX+"FIELDS_REJECT"); return; }
   // Strict lot syntax; StringToDouble alone accepts malformed values as zero.
   if(lot_raw=="" || StringFind(lot_raw,"e")>=0 || StringFind(lot_raw,"E")>=0)
   { Print(PREFIX+"LOT_REJECT"); return; }
   double lot=StringToDouble(lot_raw);
   if(!MathIsValidNumber(lot) || lot<=0.0)
   { Print(PREFIX+"LOT_REJECT"); return; }
   if(!SymbolSelect(symbol,true))
   { Print(PREFIX+"SYMBOL_SELECT_REJECT"); return; }
   double price=SymbolInfoDouble(symbol,side=="BUY"?SYMBOL_ASK:SYMBOL_BID);
   if(!MathIsValidNumber(price) || price<=0.0)
   { Print(PREFIX+"PRICE_UNAVAILABLE_REJECT"); return; }
   if(SimAccept(symbol,side,lot,price,tag,raw)) last_raw=raw;
}
