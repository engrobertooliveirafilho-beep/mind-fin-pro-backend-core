import csv
import pytest
from app.runtime.p2296c_real_exit_engine import load

COLUMNS=["time","open","high","low","close","atr_14","body_pct","session","volatility_state","spread_state","trend_21_55"]

def write_csv(path, rows):
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

def valid_row():
    return dict(time="2026-06-22T11:00:00",open="100",high="102",low="98",
                close="101",atr_14="1",body_pct="0.5",session="LONDON",
                volatility_state="HIGH",spread_state="NORMAL",trend_21_55="UP")

def test_valid_row_loads(tmp_path):
    path=tmp_path/"features.csv"
    write_csv(path,[valid_row()])
    assert len(load(path))==1

@pytest.mark.parametrize("bad",["NaN?","missing",""])
def test_corrupt_row_not_silently_dropped(tmp_path,bad):
    path=tmp_path/"features.csv"
    rows=[valid_row(),valid_row()]
    rows[1]["open"]=bad
    write_csv(path,rows)
    with pytest.raises(ValueError,match="P2296C_INVALID_FEATURE_ROW_3"):
        load(path)
