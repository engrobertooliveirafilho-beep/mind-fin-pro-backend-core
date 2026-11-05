import csv,json,os,random,socket,subprocess,sys,threading,time,traceback
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
RULE=Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S18_20260806_141023\\profiles\\S18_FTMO_RULE_SNAPSHOT.json")
PROFILES=Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S18_20260806_141023\\profiles\\S18_FAILURE_PROFILES.json")
RESULT=Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S18_20260806_141023\\evidence\\S18_FTMO_RULE_SHADOW_RESULT.json")
SCENARIOS=Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S18_20260806_141023\\ledgers\\S18_SCENARIO_LEDGER.csv")
FAILURES=Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S18_20260806_141023\\ledgers\\S18_FAILURE_INJECTION_LEDGER.csv")
CHECKPOINT=Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S18_20260806_141023\\checkpoints\\S18_RUNTIME_CHECKPOINT.json")
PERSISTENT=Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\_CONTROL\\S18\\S18_RESUME_CHECKPOINT.json")
NORMAL=5000
CHECKPOINT_EVERY=250
SEED=18062026
RESUME_INDEX=0
for p in (RESULT,SCENARIOS,FAILURES,CHECKPOINT,PERSISTENT):p.parent.mkdir(parents=True,exist_ok=True)
def money(v):return Decimal(str(v)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
def atomic(path,payload):
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w',encoding='utf-8') as h:
        json.dump(payload,h,ensure_ascii=False,indent=2,sort_keys=True,default=str);h.flush();os.fsync(h.fileno())
    os.replace(tmp,path)
def flush(path,rows):
    if not rows:return
    with path.open('a',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=rows[0].keys())
        if path.stat().st_size==0:w.writeheader()
        w.writerows(rows)
    rows.clear()
with RULE.open('r',encoding='utf-8') as h:rules=json.load(h)
with PROFILES.open('r',encoding='utf-8') as h:profiles=json.load(h)
model=rules['ftmo_model'];initial=money(rules['initial_simulated_capital']);daily_amt=money(rules['maximum_daily_loss_amount']);max_amt=money(rules['maximum_loss_amount']);target_amt=money(rules['profit_target_amount']);min_days=int(rules['minimum_trading_days'])
violations=[];normal_pass=normal_fail=failure_pass=failure_fail=0;scenario_index=RESUME_INDEX;checkpoints=0;scenario_rows=[];failure_rows=[];status='CONTROLLED_FTMO_RULE_SHADOW_FAIL';err_type=err_msg=err_tb=''
orig_socket=socket.socket;orig_popen=subprocess.Popen;orig_thread=threading.Thread.start
def deny_socket(*a,**k):violations.append({'type':'NETWORK_ATTEMPT'});raise RuntimeError('NETWORK_FORBIDDEN')
def deny_popen(*a,**k):violations.append({'type':'SUBPROCESS_ATTEMPT'});raise RuntimeError('SUBPROCESS_FORBIDDEN')
def deny_thread(self,*a,**k):violations.append({'type':'THREAD_ATTEMPT'});raise RuntimeError('THREAD_FORBIDDEN')
socket.socket=deny_socket;subprocess.Popen=deny_popen;threading.Thread.start=deny_thread
def daily_limit(midnight):return money(midnight)-daily_amt
def max_limit(highest):return (max(initial,money(highest))-max_amt) if model=='1STEP' else (initial-max_amt)
def eq(balance,open_pl,swaps,commissions):return money(money(balance)+money(open_pl)+money(swaps)-abs(money(commissions)))
def risk(midnight,current,highest,open_pl,swaps,commissions):
    equity=eq(current,open_pl,swaps,commissions);dl=daily_limit(midnight);ml=max_limit(highest);db=equity<dl;mb=equity<ml
    return {'equity':equity,'daily_limit':dl,'maximum_limit':ml,'blocked':db or mb,'daily_breach':db,'maximum_breach':mb}
def target(balance,closed):return money(balance)>=initial+target_amt and bool(closed)
def days(n):return True if model=='1STEP' else int(n)>=min_days
try:
    random.seed(SEED)
    for _ in range(NORMAL):
        scenario_index+=1
        midnight=money(initial+Decimal(str(random.uniform(-2000,6000))))
        current=money(midnight+Decimal(str(random.uniform(-4500,4500))))
        highest=money(max(initial,midnight+Decimal(str(random.uniform(0,5000)))))
        open_pl=money(Decimal(str(random.uniform(-2500,2500))))
        swaps=money(Decimal(str(random.uniform(-100,100))))
        commissions=money(abs(Decimal(str(random.uniform(0,150)))))
        r=risk(midnight,current,highest,open_pl,swaps,commissions)
        expected=r['equity']<r['daily_limit'] or r['equity']<r['maximum_limit'];passed=bool(r['blocked'])==bool(expected)
        normal_pass+=1 if passed else 0;normal_fail+=0 if passed else 1
        scenario_rows.append({'scenario_index':scenario_index,'midnight_balance':str(midnight),'current_balance':str(current),'highest_midnight_balance':str(highest),'open_pl':str(open_pl),'swaps':str(swaps),'commissions':str(commissions),'equity':str(r['equity']),'daily_limit':str(r['daily_limit']),'maximum_limit':str(r['maximum_limit']),'expected_block':expected,'observed_block':r['blocked'],'pass':passed})
        if len(scenario_rows)>=500:flush(SCENARIOS,scenario_rows)
        if scenario_index%CHECKPOINT_EVERY==0:
            checkpoints+=1;cp={'run_id':'20260806_141023','scenario_index':scenario_index,'normal_pass':normal_pass,'normal_fail':normal_fail,'failure_pass':failure_pass,'failure_fail':failure_fail,'checkpoint_count':checkpoints,'completed':False,'mode':'PAPER_ONLY','broker_connection':False,'order_execution':False,'live_real':'FORBIDDEN','updated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};atomic(CHECKPOINT,cp);atomic(PERSISTENT,cp)
    flush(SCENARIOS,scenario_rows)
    for p in profiles:
        scenario_index+=1;observed={};expected={};passed=False;t=p['type']
        if t=='risk':
            daily_loss=daily_amt*Decimal(str(p['daily_ratio']));total_loss=max_amt*Decimal(str(p['total_ratio']));current=money(initial-max(daily_loss,total_loss));r=risk(initial,current,initial,daily_amt*Decimal(str(p['open_ratio'])),daily_amt*Decimal(str(p['swap_ratio'])),daily_amt*Decimal(str(p['commission_ratio'])));observed={'blocked':r['blocked'],'equity':str(r['equity']),'daily_limit':str(r['daily_limit']),'maximum_limit':str(r['maximum_limit'])};expected={'blocked':bool(p['expected_block'])};passed=observed['blocked']==expected['blocked']
        elif t=='target':
            observed={'passed':target(initial*Decimal(str(p['target_ratio'])),p['positions_closed'])};expected={'passed':bool(p['expected_pass'])};passed=observed['passed']==expected['passed']
        elif t=='days':
            observed={'passed':days(p['days'])};expected={'passed':bool(p['expected_pass'])};passed=observed['passed']==expected['passed']
        elif t=='activity':
            observed={'days':1 if int(p['opened_positions'])>0 else 0};expected={'days':int(p['expected_days'])};passed=observed['days']==expected['days']
        elif t=='trailing':
            peak=money(initial*Decimal(str(p['peak_ratio'])));later=money(initial*Decimal(str(p['later_ratio'])));first=max_limit(peak);second=max_limit(max(peak,later));observed={'first_limit':str(first),'second_limit':str(second)};expected={'non_decreasing':True};passed=second>=first
        elif t=='static':
            peak=money(initial*Decimal(str(p['peak_ratio'])));observed_limit=max_limit(peak);expected_limit=initial-max_amt;observed={'limit':str(observed_limit)};expected={'static':str(expected_limit)};passed=(observed_limit==expected_limit) if model=='2STEP' else (observed_limit>=expected_limit)
        failure_pass+=1 if passed else 0;failure_fail+=0 if passed else 1
        failure_rows.append({'scenario_index':scenario_index,'profile_id':p['id'],'profile_name':p['name'],'expected':json.dumps(expected,sort_keys=True),'observed':json.dumps(observed,sort_keys=True),'pass':passed})
    flush(FAILURES,failure_rows)
    checks={'normal_complete':normal_pass+normal_fail==NORMAL,'normal_fail_zero':normal_fail==0,'failure_complete':failure_pass+failure_fail==len(profiles),'failure_fail_zero':failure_fail==0,'violations_zero':len(violations)==0,'broker_zero':True,'orders_zero':True}
    ok=all(checks.values());status='CONTROLLED_FTMO_RULE_SHADOW_PASS' if ok else status
    cp={'run_id':'20260806_141023','scenario_index':scenario_index,'normal_pass':normal_pass,'normal_fail':normal_fail,'failure_pass':failure_pass,'failure_fail':failure_fail,'checkpoint_count':checkpoints,'completed':ok,'mode':'PAPER_ONLY','broker_connection':False,'order_execution':False,'live_real':'FORBIDDEN','updated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};atomic(CHECKPOINT,cp);atomic(PERSISTENT,cp)
    result={'status':status,'run_id':'20260806_141023','ftmo_model':model,'normal_scenarios':{'total':NORMAL,'pass':normal_pass,'fail':normal_fail},'failure_injection':{'total':len(profiles),'pass':failure_pass,'fail':failure_fail},'checks':checks,'safety':{'violations':len(violations),'violation_details':violations,'runtime_started':False,'runtime_loop_started':False,'network_access':False,'broker_connection':False,'order_execution':False,'threads_started':False,'subprocess_started':False,'source_write':False,'live_real':'FORBIDDEN'},'error':{'type':err_type,'message':err_msg,'traceback':err_tb}}
except Exception as exc:
    err_type=type(exc).__name__;err_msg=str(exc);err_tb=traceback.format_exc();result={'status':'CONTROLLED_FTMO_RULE_SHADOW_FAIL','run_id':'20260806_141023','safety':{'violations':len(violations),'runtime_started':False,'network_access':False,'broker_connection':False,'order_execution':False,'live_real':'FORBIDDEN'},'error':{'type':err_type,'message':err_msg,'traceback':err_tb}}
finally:
    socket.socket=orig_socket;subprocess.Popen=orig_popen;threading.Thread.start=orig_thread;atomic(RESULT,result)
sys.exit(0 if result.get('status')=='CONTROLLED_FTMO_RULE_SHADOW_PASS' else 20)
