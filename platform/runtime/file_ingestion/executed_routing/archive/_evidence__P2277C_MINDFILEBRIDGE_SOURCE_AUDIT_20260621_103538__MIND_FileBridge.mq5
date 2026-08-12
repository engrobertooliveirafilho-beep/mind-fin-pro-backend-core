//+------------------------------------------------------------------+
//| P2260_MIND_FTMO_PROP_DESK_OS.mq5                                 |
//| FileBridge + Profit Boleta + Trade Manager + FTMO Guardian        |
//| Risk Engine + Analytics + Journal + Prop Firm OS                  |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
CTrade trade;

// ===================== INPUTS =====================
input string InpSignalFile       = "mt5_order.txt";
input bool   InpExecuteSim       = true;
input bool   InpDryRun           = false;
input bool   InpAllowRealAccount = false;

input long   InpMagicNumber      = 96682260;
input double InpManualLot        = 0.01;
input bool   InpUseAutoLot       = false;

input int    InpCooldownSeconds  = 10;
input int    InpMaxTradesDay     = 10;
input double InpMaxExposureLots  = 1.00;
input int    InpMaxConsecLosses  = 3;

input double InpMaxDailyLoss     = 200.0;
input double InpMaxTotalLoss     = 500.0;
input double InpDailyTarget      = 300.0;
input double InpChallengeTarget  = 10000.0;
input int    InpMinTradingDays   = 4;

input int    InpSLPoints         = 300;
input int    InpTPPoints         = 600;
input double InpRiskPercent      = 1.0;

input int    InpTrailingPoints   = 200;
input int    InpBreakEvenPlusPts = 20;

input bool   InpUseSessionFilter = false;
input int    InpSessionStartHour = 8;
input int    InpSessionEndHour   = 18;

input bool   InpUseNewsLock      = false;
input string InpNewsLockFile     = "mind_news_lock.txt";

input string InpStrategyMode     = "SCALP";

// ===================== STATE =====================
string   lastSignalId       = "";
string   lastRawSignal      = "";
string   lastStatus         = "INIT";
string   lastError          = "";
string   lastAction         = "";
double   lastLot            = 0.0;
datetime lastTradeTime      = 0;
datetime lastMissingLogTime = 0;

int      tradesToday        = 0;
int      tradingDays        = 0;
double   startBalance       = 0.0;
double   dayStartBalance    = 0.0;

double openPnL       = 0.0;
double dailyPnL      = 0.0;
double dailyLoss     = 0.0;
double totalLoss     = 0.0;
double exposureLots  = 0.0;
double marginUsed    = 0.0;
double marginFree    = 0.0;
double drawdownPct   = 0.0;

int    openPositions = 0;
int    consecutiveLosses = 0;
ulong  lastTicket    = 0;
string lastExecInfo  = "";
string ftmoStatus    = "OK";
string blockReason   = "";
bool   killSwitch     = false;
bool   trailingEnabled = false;

// Analytics
int    histTrades = 0;
int    wins = 0;
int    losses = 0;
double grossProfit = 0.0;
double grossLoss   = 0.0;
double netProfit   = 0.0;
double winRate     = 0.0;
double payoff      = 0.0;
double profitFactor = 0.0;
double expectancy  = 0.0;

// ===================== UI =====================
string HUD_NAME    = "MIND_HUD_P2260";
string BTN_BUY     = "MIND_BTN_BUY";
string BTN_SELL    = "MIND_BTN_SELL";
string BTN_CLOSE   = "MIND_BTN_CLOSE_ALL";
string BTN_BE      = "MIND_BTN_BE";
string BTN_P25     = "MIND_BTN_P25";
string BTN_P50     = "MIND_BTN_P50";
string BTN_P75     = "MIND_BTN_P75";
string BTN_TRAIL   = "MIND_BTN_TRAIL";
string BTN_REPORT  = "MIND_BTN_REPORT";
string BTN_KILL    = "MIND_BTN_KILL";
string BTN_REVERSE = "MIND_BTN_REVERSE";
string PANEL_TITLE = "MIND_PANEL_TITLE";
string PANEL_INFO  = "MIND_PANEL_INFO";
string PANEL_PNL   = "MIND_PANEL_PNL";
string PANEL_OS    = "MIND_PANEL_OS";

// ===================== UTILS =====================
void Log(string msg){ Print("[MIND_P2260] ", msg); }

void SetState(string status,string err="")
{
   bool changed=(status!=lastStatus || err!=lastError);
   lastStatus=status;
   lastError=err;
   if(changed)
   {
      if(err!="") Log(status+" | ERROR="+err);
      else Log(status);
   }
}

string TrimStr(string s)
{
   StringTrimLeft(s);
   StringTrimRight(s);
   return s;
}

bool DeleteSignalFile()
{
   ResetLastError();
   if(FileIsExist(InpSignalFile,FILE_COMMON))
   {
      if(!FileDelete(InpSignalFile,FILE_COMMON))
      {
         Log("SIGNAL_DELETE_FAILED | ERROR="+IntegerToString(GetLastError()));
         return false;
      }
      Log("SIGNAL_CONSUMED_AND_DELETED | FILE="+InpSignalFile);
   }
   return true;
}

bool IsRealAccountBlocked()
{
   long mode=AccountInfoInteger(ACCOUNT_TRADE_MODE);
   if(mode==ACCOUNT_TRADE_MODE_REAL && !InpAllowRealAccount)
   {
      SetState("REAL_ACCOUNT_BLOCKED","Conta real bloqueada");
      return true;
   }
   return false;
}

// ===================== FILE BRIDGE =====================
bool ReadSignalFile(string &raw)
{
   ResetLastError();
   int handle=FileOpen(InpSignalFile,FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);

   if(handle==INVALID_HANDLE)
   {
      lastRawSignal="";
      if(TimeCurrent()-lastMissingLogTime>=10)
      {
         lastMissingLogTime=TimeCurrent();
         Log("WAITING_SIGNAL | COMMON_FILE_NOT_FOUND | "+InpSignalFile);
      }
      SetState("WAITING_SIGNAL","Aguardando Common\\Files");
      return false;
   }

   raw=FileReadString(handle);
   FileClose(handle);
   raw=TrimStr(raw);

   if(raw=="")
   {
      SetState("EMPTY_SIGNAL","Arquivo vazio");
      DeleteSignalFile();
      return false;
   }

   lastRawSignal=raw;
   Log("RAW_SIGNAL="+raw);
   return true;
}

bool ParseSignal(string raw,string &symbol,string &action,double &lot,string &signalId,string &stamp)
{
   string parts[];
   int count=StringSplit(raw,',',parts);

   if(count<3)
   {
      SetState("PARSE_FAILED","Esperado SYMBOL,ACTION,LOT,SIGNAL_ID,TIMESTAMP");
      DeleteSignalFile();
      return false;
   }

   symbol=TrimStr(parts[0]);
   action=TrimStr(parts[1]);
   lot=StringToDouble(TrimStr(parts[2]));
   signalId=(count>=4 ? TrimStr(parts[3]) : raw);
   stamp=(count>=5 ? TrimStr(parts[4]) : "");

   if(symbol==""){ SetState("INVALID_SYMBOL","Symbol vazio"); DeleteSignalFile(); return false; }
   if(action!="BUY" && action!="SELL"){ SetState("INVALID_ACTION",action); DeleteSignalFile(); return false; }
   if(lot<=0){ SetState("INVALID_LOT",DoubleToString(lot,2)); DeleteSignalFile(); return false; }

   lastAction=action;
   lastLot=lot;

   Log("PARSE_OK | SYMBOL="+symbol+" | ACTION="+action+" | LOT="+DoubleToString(lot,2)+" | SIGNAL_ID="+signalId);
   return true;
}

// ===================== ANALYTICS =====================
void UpdateAnalytics()
{
   histTrades=0; wins=0; losses=0;
   grossProfit=0.0; grossLoss=0.0; netProfit=0.0;

   datetime from = TimeCurrent() - 86400 * 30;
   datetime to   = TimeCurrent();

   HistorySelect(from,to);

   int deals=HistoryDealsTotal();

   for(int i=0;i<deals;i++)
   {
      ulong deal=HistoryDealGetTicket(i);
      if(deal==0) continue;

      long entry=HistoryDealGetInteger(deal,DEAL_ENTRY);
      if(entry!=DEAL_ENTRY_OUT) continue;

      double profit=HistoryDealGetDouble(deal,DEAL_PROFIT);
      double commission=HistoryDealGetDouble(deal,DEAL_COMMISSION);
      double swap=HistoryDealGetDouble(deal,DEAL_SWAP);
      double result=profit+commission+swap;

      histTrades++;
      netProfit+=result;

      if(result>0){ wins++; grossProfit+=result; }
      if(result<0){ losses++; grossLoss+=MathAbs(result); }
   }

   winRate = (histTrades>0 ? ((double)wins/(double)histTrades)*100.0 : 0.0);

   double avgWin  = (wins>0 ? grossProfit/(double)wins : 0.0);
   double avgLoss = (losses>0 ? grossLoss/(double)losses : 0.0);

   payoff = (avgLoss>0 ? avgWin/avgLoss : 0.0);
   profitFactor = (grossLoss>0 ? grossProfit/grossLoss : 0.0);
   expectancy = (histTrades>0 ? netProfit/(double)histTrades : 0.0);
}

// ===================== TRACKING / FTMO =====================
void UpdateTradingDays()
{
   tradingDays = 0;

   datetime from = TimeCurrent() - 86400 * 60;
   datetime to   = TimeCurrent();

   HistorySelect(from,to);

   int deals=HistoryDealsTotal();
   string days="";

   for(int i=0;i<deals;i++)
   {
      ulong deal=HistoryDealGetTicket(i);
      if(deal==0) continue;

      long entry=HistoryDealGetInteger(deal,DEAL_ENTRY);
      if(entry!=DEAL_ENTRY_OUT && entry!=DEAL_ENTRY_IN) continue;

      datetime t=(datetime)HistoryDealGetInteger(deal,DEAL_TIME);
      string d=TimeToString(t,TIME_DATE);

      if(StringFind(days,d)<0)
      {
         days += d + "|";
         tradingDays++;
      }
   }
}

void UpdateTracking()
{
   openPnL=0.0; openPositions=0; exposureLots=0.0;

   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket=PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         openPnL+=PositionGetDouble(POSITION_PROFIT);
         exposureLots+=PositionGetDouble(POSITION_VOLUME);
         openPositions++;
      }
   }

   double balance=AccountInfoDouble(ACCOUNT_BALANCE);
   double equity=AccountInfoDouble(ACCOUNT_EQUITY);

   marginUsed=AccountInfoDouble(ACCOUNT_MARGIN);
   marginFree=AccountInfoDouble(ACCOUNT_MARGIN_FREE);

   dailyPnL=equity-dayStartBalance;
   dailyLoss=dayStartBalance-equity;
   totalLoss=startBalance-equity;
   drawdownPct=(balance>0 ? ((balance-equity)/balance)*100.0 : 0.0);

   UpdateAnalytics();
   UpdateTradingDays();

   ftmoStatus="OK";
   blockReason="";

   if(killSwitch){ ftmoStatus="KILL_SWITCH"; blockReason="manual lock"; }
   else if(dailyLoss>=InpMaxDailyLoss){ ftmoStatus="BLOCKED"; blockReason="daily loss"; }
   else if(totalLoss>=InpMaxTotalLoss){ ftmoStatus="BLOCKED"; blockReason="total loss"; }
   else if(tradesToday>=InpMaxTradesDay){ ftmoStatus="BLOCKED"; blockReason="max trades"; }
   else if(exposureLots>=InpMaxExposureLots){ ftmoStatus="BLOCKED"; blockReason="max exposure"; }
   else if(consecutiveLosses>=InpMaxConsecLosses){ ftmoStatus="BLOCKED"; blockReason="consecutive losses"; }
   else if(dailyPnL>=InpDailyTarget){ ftmoStatus="TARGET_HIT"; blockReason="daily target"; }
}

bool IsSessionAllowed()
{
   if(!InpUseSessionFilter) return true;

   MqlDateTime dt;
   TimeToStruct(TimeCurrent(),dt);

   if(dt.hour>=InpSessionStartHour && dt.hour<InpSessionEndHour)
      return true;

   SetState("SESSION_BLOCK","fora da janela permitida");
   return false;
}

bool IsNewsLocked()
{
   if(!InpUseNewsLock) return false;

   if(FileIsExist(InpNewsLockFile,FILE_COMMON))
   {
      SetState("NEWS_LOCK","bloqueio por notícia");
      return true;
   }

   return false;
}

bool RiskGuard()
{
   UpdateTracking();

   if(!IsSessionAllowed()) return false;
   if(IsNewsLocked()) return false;

   if(ftmoStatus!="OK" && ftmoStatus!="TARGET_HIT")
   {
      SetState("FTMO_BLOCK",blockReason);
      return false;
   }

   if(ftmoStatus=="TARGET_HIT")
   {
      SetState("TARGET_BLOCK","meta diária atingida");
      return false;
   }

   return true;
}

// ===================== RISK ENGINE =====================
double CalculateLotByRisk(string symbol,int slPoints,double riskPct)
{
   double balance=AccountInfoDouble(ACCOUNT_BALANCE);
   double riskMoney=balance*(riskPct/100.0);

   double tickValue=SymbolInfoDouble(symbol,SYMBOL_TRADE_TICK_VALUE);
   double tickSize=SymbolInfoDouble(symbol,SYMBOL_TRADE_TICK_SIZE);
   double point=SymbolInfoDouble(symbol,SYMBOL_POINT);

   if(tickValue<=0 || tickSize<=0 || point<=0 || slPoints<=0)
      return InpManualLot;

   double moneyPerLot=(slPoints*point/tickSize)*tickValue;
   if(moneyPerLot<=0) return InpManualLot;

   double lot=riskMoney/moneyPerLot;

   double minLot=SymbolInfoDouble(symbol,SYMBOL_VOLUME_MIN);
   double maxLot=SymbolInfoDouble(symbol,SYMBOL_VOLUME_MAX);
   double step=SymbolInfoDouble(symbol,SYMBOL_VOLUME_STEP);

   lot=MathMax(minLot,MathMin(maxLot,lot));
   lot=MathFloor(lot/step)*step;

   return NormalizeDouble(lot,2);
}

// ===================== VISUAL MARKERS =====================
void DrawTradeMarker(string action,double price,double lot,ulong ticket)
{
   string suffix=IntegerToString((int)TimeCurrent())+"_"+IntegerToString((int)ticket);
   string arrowName="MIND_"+action+"_ARROW_"+suffix;
   string labelName="MIND_"+action+"_LABEL_"+suffix;

   int arrowCode=233;
   color c=clrLime;

   if(action=="SELL"){ arrowCode=234; c=clrRed; }

   ObjectCreate(0,arrowName,OBJ_ARROW,0,TimeCurrent(),price);
   ObjectSetInteger(0,arrowName,OBJPROP_ARROWCODE,arrowCode);
   ObjectSetInteger(0,arrowName,OBJPROP_COLOR,c);
   ObjectSetInteger(0,arrowName,OBJPROP_WIDTH,2);

   string label=action+" "+DoubleToString(lot,2)+" @ "+DoubleToString(price,_Digits);
   ObjectCreate(0,labelName,OBJ_TEXT,0,TimeCurrent(),price);
   ObjectSetString(0,labelName,OBJPROP_TEXT,label);
   ObjectSetInteger(0,labelName,OBJPROP_COLOR,c);
   ObjectSetInteger(0,labelName,OBJPROP_FONTSIZE,9);

   Log("MARKER_DRAWN | "+label);
}

// ===================== EXECUTION =====================
bool ExecuteSignal(string symbol,string action,double lot,string signalId)
{
   if(IsRealAccountBlocked()){ DeleteSignalFile(); return false; }

   if(signalId==lastSignalId)
   {
      SetState("DUPLICATE_BLOCKED","Signal já executado: "+signalId);
      DeleteSignalFile();
      return false;
   }

   if(TimeCurrent()-lastTradeTime<InpCooldownSeconds)
   {
      SetState("COOLDOWN_BLOCKED","Cooldown ativo");
      return false;
   }

   if(!SymbolSelect(symbol,true))
   {
      SetState("SYMBOL_SELECT_FAILED",symbol);
      DeleteSignalFile();
      return false;
   }

   if(!RiskGuard()) return false;

   if(InpUseAutoLot)
      lot=CalculateLotByRisk(symbol,InpSLPoints,InpRiskPercent);

   if(InpDryRun || !InpExecuteSim)
   {
      lastSignalId=signalId;
      lastTradeTime=TimeCurrent();
      tradesToday++;
      lastExecInfo="DRY_RUN | SIGNAL_ID="+signalId;
      DeleteSignalFile();
      SetState("DRY_RUN_OK","Sinal validado sem execução");
      return true;
   }

   trade.SetExpertMagicNumber(InpMagicNumber);

   double price=(action=="BUY" ? SymbolInfoDouble(symbol,SYMBOL_ASK) : SymbolInfoDouble(symbol,SYMBOL_BID));
   double sl=0.0,tp=0.0;
   double point=SymbolInfoDouble(symbol,SYMBOL_POINT);

   if(action=="BUY")
   {
      sl=price-(InpSLPoints*point);
      tp=price+(InpTPPoints*point);
   }
   else
   {
      sl=price+(InpSLPoints*point);
      tp=price-(InpTPPoints*point);
   }

   ResetLastError();
   bool ok=false;

   if(action=="BUY") ok=trade.Buy(lot,symbol,0.0,sl,tp,"MIND_BUY");
   if(action=="SELL") ok=trade.Sell(lot,symbol,0.0,sl,tp,"MIND_SELL");

   if(!ok)
   {
      int err=GetLastError();
      lastExecInfo="FAILED | Retcode="+IntegerToString((int)trade.ResultRetcode())+" | LastError="+IntegerToString(err);
      SetState("EXECUTION_FAILED",lastExecInfo);
      return false;
   }

   ulong ticket=trade.ResultOrder();
   lastTicket=ticket;
   lastExecInfo="Ticket="+IntegerToString((int)ticket)+" | Retcode="+IntegerToString((int)trade.ResultRetcode());
   lastSignalId=signalId;
   lastTradeTime=TimeCurrent();
   tradesToday++;
   lastLot=lot;

   DrawTradeMarker(action,price,lot,ticket);
   DeleteSignalFile();
   SetState("EXECUTION_OK",lastExecInfo);
   return true;
}

// ===================== TRADE MANAGER =====================
bool CloseAllPositions()
{
   bool any=false;

   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket=PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         string sym=PositionGetString(POSITION_SYMBOL);
         if(trade.PositionClose(sym))
         {
            any=true;
            Log("POSITION_CLOSED | SYMBOL="+sym);
         }
      }
   }

   if(any) SetState("POSITIONS_CLOSED","Fechamento manual");
   else SetState("NO_POSITION_TO_CLOSE","Nenhuma posição aberta");

   return any;
}

void PartialClose(double ratio)
{
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket=PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         string sym=PositionGetString(POSITION_SYMBOL);
         double vol=PositionGetDouble(POSITION_VOLUME);
         double step=SymbolInfoDouble(sym,SYMBOL_VOLUME_STEP);
         double minLot=SymbolInfoDouble(sym,SYMBOL_VOLUME_MIN);

         double closeVol=NormalizeDouble(MathFloor((vol*ratio)/step)*step,2);

         if(closeVol>=minLot && closeVol<vol)
         {
            if(trade.PositionClosePartial(sym,closeVol))
               SetState("PARTIAL_CLOSE_OK","Volume="+DoubleToString(closeVol,2));
            else
               SetState("PARTIAL_CLOSE_FAIL","Retcode="+IntegerToString((int)trade.ResultRetcode()));
         }
      }
   }
}

void MoveToBreakeven()
{
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket=PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         string sym=PositionGetString(POSITION_SYMBOL);
         long type=PositionGetInteger(POSITION_TYPE);
         double open=PositionGetDouble(POSITION_PRICE_OPEN);
         double tp=PositionGetDouble(POSITION_TP);
         double point=SymbolInfoDouble(sym,SYMBOL_POINT);

         double newSL=open;
         if(type==POSITION_TYPE_BUY) newSL=open+(InpBreakEvenPlusPts*point);
         if(type==POSITION_TYPE_SELL) newSL=open-(InpBreakEvenPlusPts*point);

         if(trade.PositionModify(sym,newSL,tp))
            SetState("BREAKEVEN_OK","SL="+DoubleToString(newSL,_Digits));
         else
            SetState("BREAKEVEN_FAIL","Retcode="+IntegerToString((int)trade.ResultRetcode()));
      }
   }
}

void ApplyTrailing()
{
   if(!trailingEnabled) return;

   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket=PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         string sym=PositionGetString(POSITION_SYMBOL);
         long type=PositionGetInteger(POSITION_TYPE);
         double sl=PositionGetDouble(POSITION_SL);
         double tp=PositionGetDouble(POSITION_TP);
         double point=SymbolInfoDouble(sym,SYMBOL_POINT);
         double bid=SymbolInfoDouble(sym,SYMBOL_BID);
         double ask=SymbolInfoDouble(sym,SYMBOL_ASK);

         double newSL=sl;

         if(type==POSITION_TYPE_BUY)
         {
            newSL=bid-(InpTrailingPoints*point);
            if(newSL>sl) trade.PositionModify(sym,newSL,tp);
         }

         if(type==POSITION_TYPE_SELL)
         {
            newSL=ask+(InpTrailingPoints*point);
            if(sl==0 || newSL<sl) trade.PositionModify(sym,newSL,tp);
         }
      }
   }
}

void ReversePosition()
{
   int currentType=-1;
   double vol=0.0;

   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket=PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         if(PositionGetString(POSITION_SYMBOL)==_Symbol)
         {
            currentType=(int)PositionGetInteger(POSITION_TYPE);
            vol+=PositionGetDouble(POSITION_VOLUME);
         }
      }
   }

   if(vol<=0)
   {
      SetState("REVERSE_FAIL","sem posição");
      return;
   }

   CloseAllPositions();

   string sid="REVERSE_"+IntegerToString((int)TimeCurrent());

   if(currentType==POSITION_TYPE_BUY)
      ExecuteSignal(_Symbol,"SELL",vol,sid);
   else if(currentType==POSITION_TYPE_SELL)
      ExecuteSignal(_Symbol,"BUY",vol,sid);
}

// ===================== REPORTING =====================
void ExportReport()
{
   UpdateTracking();

   int h=FileOpen("mind_daily_report.csv",FILE_WRITE|FILE_CSV|FILE_COMMON);

   if(h!=INVALID_HANDLE)
   {
      FileWrite(h,"time","balance","equity","dailyPnL","openPnL","tradesToday","openPositions","exposureLots","winRate","payoff","profitFactor","expectancy","ftmoStatus");
      FileWrite(h,TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),
                AccountInfoDouble(ACCOUNT_BALANCE),
                AccountInfoDouble(ACCOUNT_EQUITY),
                dailyPnL,openPnL,tradesToday,openPositions,exposureLots,winRate,payoff,profitFactor,expectancy,ftmoStatus);
      FileClose(h);
      SetState("REPORT_EXPORTED","mind_daily_report.csv");
   }
   else SetState("REPORT_FAILED","CSV FileOpen failed");

   int j=FileOpen("mind_daily_report.json",FILE_WRITE|FILE_TXT|FILE_COMMON);
   if(j!=INVALID_HANDLE)
   {
      string json="{";
      json+="\"time\":\""+TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS)+"\",";
      json+="\"balance\":"+DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE),2)+",";
      json+="\"equity\":"+DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY),2)+",";
      json+="\"dailyPnL\":"+DoubleToString(dailyPnL,2)+",";
      json+="\"openPnL\":"+DoubleToString(openPnL,2)+",";
      json+="\"winRate\":"+DoubleToString(winRate,2)+",";
      json+="\"profitFactor\":"+DoubleToString(profitFactor,2)+",";
      json+="\"ftmoStatus\":\""+ftmoStatus+"\"";
      json+="}";
      FileWriteString(j,json);
      FileClose(j);
   }
}

// ===================== HUD / BOLETA =====================
void CreateLabel(string name,int x,int y,string text,int fontSize,color c)
{
   if(ObjectFind(0,name)<0)
   {
      ObjectCreate(0,name,OBJ_LABEL,0,0,0);
      ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
      ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x);
      ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y);
      ObjectSetInteger(0,name,OBJPROP_FONTSIZE,fontSize);
      ObjectSetInteger(0,name,OBJPROP_COLOR,c);
   }
   ObjectSetString(0,name,OBJPROP_TEXT,text);
}

void CreateButton(string name,int x,int y,int w,int h,string text,color bg,color fg)
{
   if(ObjectFind(0,name)<0)
   {
      ObjectCreate(0,name,OBJ_BUTTON,0,0,0);
      ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
      ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x);
      ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y);
      ObjectSetInteger(0,name,OBJPROP_XSIZE,w);
      ObjectSetInteger(0,name,OBJPROP_YSIZE,h);
      ObjectSetInteger(0,name,OBJPROP_BGCOLOR,bg);
      ObjectSetInteger(0,name,OBJPROP_COLOR,fg);
      ObjectSetInteger(0,name,OBJPROP_FONTSIZE,8);
   }
   ObjectSetString(0,name,OBJPROP_TEXT,text);
}

void DrawHUD()
{
   UpdateTracking();

   double balance=AccountInfoDouble(ACCOUNT_BALANCE);
   double equity=AccountInfoDouble(ACCOUNT_EQUITY);

   int tradesLeft=InpMaxTradesDay-tradesToday;
   if(tradesLeft<0) tradesLeft=0;

   double targetProgress = (InpChallengeTarget>0 ? (netProfit/InpChallengeTarget)*100.0 : 0.0);

   string text=
      "MIND PROP FIRM OS P2260\n"+
      "STATUS: "+lastStatus+"\n"+
      "MODE: "+(InpDryRun?"DRY_RUN":"EXECUTE_SIM")+"\n"+
      "FTMO: "+ftmoStatus+" "+blockReason+"\n"+
      "STRATEGY: "+InpStrategyMode+"\n\n"+
      "BALANCE: "+DoubleToString(balance,2)+"\n"+
      "EQUITY: "+DoubleToString(equity,2)+"\n"+
      "OPEN PNL: "+DoubleToString(openPnL,2)+"\n"+
      "DAILY PNL: "+DoubleToString(dailyPnL,2)+"\n"+
      "NET 30D: "+DoubleToString(netProfit,2)+"\n"+
      "TARGET %: "+DoubleToString(targetProgress,2)+"\n\n"+
      "DAILY LOSS: "+DoubleToString(dailyLoss,2)+"/"+DoubleToString(InpMaxDailyLoss,2)+"\n"+
      "TOTAL LOSS: "+DoubleToString(totalLoss,2)+"/"+DoubleToString(InpMaxTotalLoss,2)+"\n"+
      "DD %: "+DoubleToString(drawdownPct,2)+"\n\n"+
      "TRADES: "+IntegerToString(tradesToday)+"/"+IntegerToString(InpMaxTradesDay)+" | LEFT "+IntegerToString(tradesLeft)+"\n"+
      "POSITIONS: "+IntegerToString(openPositions)+" | LOTS "+DoubleToString(exposureLots,2)+"\n"+
      "MARGIN: "+DoubleToString(marginUsed,2)+" | FREE "+DoubleToString(marginFree,2)+"\n\n"+
      "WIN RATE: "+DoubleToString(winRate,2)+"%\n"+
      "PAYOFF: "+DoubleToString(payoff,2)+"\n"+
      "PF: "+DoubleToString(profitFactor,2)+"\n"+
      "EXPECT: "+DoubleToString(expectancy,2)+"\n"+
      "TRADING DAYS: "+IntegerToString(tradingDays)+"/"+IntegerToString(InpMinTradingDays)+"\n\n"+
      "LAST: "+lastAction+" LOT "+DoubleToString(lastLot,2)+"\n"+
      "TICKET: "+IntegerToString((int)lastTicket)+"\n"+
      "EXEC: "+lastExecInfo+"\n"+
      "ERROR: "+lastError;

   CreateLabel(HUD_NAME,15,20,text,8,clrRed);
}

void DrawProfitBoleta()
{
   UpdateTracking();

   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   double ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   int spread=(int)SymbolInfoInteger(_Symbol,SYMBOL_SPREAD);

   double autoLot=CalculateLotByRisk(_Symbol,InpSLPoints,InpRiskPercent);
   double rr=(InpSLPoints>0 ? ((double)InpTPPoints/(double)InpSLPoints) : 0.0);

   CreateLabel(PANEL_TITLE,15,360,"MIND BOLETA PRO P2260",10,clrWhite);

   string info=_Symbol+
      " | MAN "+DoubleToString(InpManualLot,2)+
      " | AUTO "+DoubleToString(autoLot,2)+
      " | BID "+DoubleToString(bid,_Digits)+
      " | ASK "+DoubleToString(ask,_Digits)+
      " | SPR "+IntegerToString(spread);

   CreateLabel(PANEL_INFO,15,382,info,8,clrWhite);

   CreateButton(BTN_SELL,15,405,90,28,"SELL",clrRed,clrWhite);
   CreateButton(BTN_BUY,115,405,90,28,"BUY",clrBlue,clrWhite);
   CreateButton(BTN_CLOSE,15,438,190,24,"ZERAR",clrDarkOrange,clrWhite);

   CreateButton(BTN_BE,15,468,90,22,"BREAKEVEN",clrDarkSlateGray,clrWhite);
   CreateButton(BTN_P25,115,468,90,22,"PARCIAL 25",clrDarkSlateGray,clrWhite);
   CreateButton(BTN_P50,15,496,90,22,"PARCIAL 50",clrDarkSlateGray,clrWhite);
   CreateButton(BTN_P75,115,496,90,22,"PARCIAL 75",clrDarkSlateGray,clrWhite);

   CreateButton(BTN_TRAIL,15,524,90,22,(trailingEnabled?"TRAIL ON":"TRAIL OFF"),clrPurple,clrWhite);
   CreateButton(BTN_REVERSE,115,524,90,22,"REVERSAO",clrDarkViolet,clrWhite);

   CreateButton(BTN_REPORT,15,552,90,22,"REPORT",clrDarkGreen,clrWhite);
   CreateButton(BTN_KILL,115,552,90,22,(killSwitch?"LOCKED":"KILL"),clrMaroon,clrWhite);

   string pnlText=
      "OPEN "+DoubleToString(openPnL,2)+
      " | DAY "+DoubleToString(dailyPnL,2)+
      " | POS "+IntegerToString(openPositions)+
      " | R:R "+DoubleToString(rr,2)+
      " | FTMO "+ftmoStatus;

   CreateLabel(PANEL_PNL,15,580,pnlText,8,clrWhite);
}

// ===================== PIPELINE =====================
void ProcessPipeline()
{
   string raw,symbol,action,signalId,stamp;
   double lot=0.0;

   if(!ReadSignalFile(raw)) return;
   if(!ParseSignal(raw,symbol,action,lot,signalId,stamp)) return;

   ExecuteSignal(symbol,action,lot,signalId);
}

// ===================== EVENTS =====================
int OnInit()
{
   startBalance=AccountInfoDouble(ACCOUNT_BALANCE);
   dayStartBalance=startBalance;

   SetState("EA_INITIALIZED");
   EventSetTimer(1);

   DrawHUD();
   DrawProfitBoleta();

   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   EventKillTimer();

   string objs[]={HUD_NAME,BTN_BUY,BTN_SELL,BTN_CLOSE,BTN_BE,BTN_P25,BTN_P50,BTN_P75,BTN_TRAIL,BTN_REPORT,BTN_KILL,BTN_REVERSE,PANEL_TITLE,PANEL_INFO,PANEL_PNL};

   for(int i=0;i<ArraySize(objs);i++)
      ObjectDelete(0,objs[i]);

   Log("EA_DEINIT | reason="+IntegerToString(reason));
}

void OnTick()
{
   ProcessPipeline();
   ApplyTrailing();
   DrawHUD();
   DrawProfitBoleta();
}

void OnTimer()
{
   ProcessPipeline();
   ApplyTrailing();
   DrawHUD();
   DrawProfitBoleta();
}

void OnChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam)
{
   if(id!=CHARTEVENT_OBJECT_CLICK) return;

   if(sparam==BTN_BUY)
   {
      string sid="MANUAL_BUY_"+IntegerToString((int)TimeCurrent());
      ExecuteSignal(_Symbol,"BUY",InpManualLot,sid);
   }
   else if(sparam==BTN_SELL)
   {
      string sid="MANUAL_SELL_"+IntegerToString((int)TimeCurrent());
      ExecuteSignal(_Symbol,"SELL",InpManualLot,sid);
   }
   else if(sparam==BTN_CLOSE)
      CloseAllPositions();
   else if(sparam==BTN_BE)
      MoveToBreakeven();
   else if(sparam==BTN_P25)
      PartialClose(0.25);
   else if(sparam==BTN_P50)
      PartialClose(0.50);
   else if(sparam==BTN_P75)
      PartialClose(0.75);
   else if(sparam==BTN_TRAIL)
   {
      trailingEnabled=!trailingEnabled;
      SetState("TRAILING_CHANGED",(trailingEnabled?"ON":"OFF"));
   }
   else if(sparam==BTN_REPORT)
      ExportReport();
   else if(sparam==BTN_KILL)
   {
      killSwitch=!killSwitch;
      SetState("KILL_SWITCH",(killSwitch?"LOCKED":"UNLOCKED"));
   }
   else if(sparam==BTN_REVERSE)
      ReversePosition();

   DrawHUD();
   DrawProfitBoleta();
}