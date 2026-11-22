from app.runtime.p2303_p2305_paper_chain import reconcile_paper_chain

def test_historical_p2303_p2305_chain_not_certified():
    signal="P2302_5ed23464b49d"
    mt5={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
         "consumption_status":"PENDING_MT5_CONSUMPTION","exists_now":True,
         "selected_signal_id":signal,"selected_symbol":"GER40","selected_action":"BUY",
         "selected_lot":"0.01","content_now":f"GER40,BUY,0.01,{signal},2026-06-22T12:39:41"}
    ps={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
        "trades_sent":"1","trades_consumed":"0","open_or_pending":"1"}
    ledger=[{"signal_id":signal,"mode":"PAPER_ONLY","real_orders":"FORBIDDEN",
             "ftmo_real":"FORBIDDEN","trade_status":"NOT_CONSUMED_YET",
             "consumption_status":"PENDING_MT5_CONSUMPTION","pnl":"0","pnl_pct":"0"}]
    risk=[{"metric":"trades_consumed","value":"0"},
          {"metric":"real_orders","value":"FORBIDDEN"},{"metric":"ftmo_real","value":"FORBIDDEN"}]
    twin={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
          "ftmo_twin_status":"FTMO_TWIN_PASS","trades_consumed":"0",
          "trades_day":"1","daily_loss_pct":"0","total_loss_pct":"0"}
    state={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
           "status":"FTMO_TWIN_PASS","trades_consumed":"0","trades_day":"1"}
    rules={"daily_loss_limit_pct":"1.0","total_loss_limit_pct":"5.0",
           "max_trades_day":"6","max_trades_edge_day":"2","max_exposure_lots":"0.01",
           "default_lot":"0.01","risk_block_only":"TRUE",
           "real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN"}
    result=reconcile_paper_chain(mt5,[{"contains_signal_id":"False"}],ps,ledger,risk,twin,state,rules)
    assert result["status"]=="PAPER_EVIDENCE_CHAIN_RECONCILED_NOT_CERTIFIED"
    assert not result["ftmo_challenge_certified"] and not result["e2e_certified"]
    assert result["orders_authorized"]==0
