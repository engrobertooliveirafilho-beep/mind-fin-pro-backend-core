import tempfile,unittest
from pathlib import Path
import pandas as pd
from mind_trader.research.build_m15_features import build_features

class FeatureBuilderTests(unittest.TestCase):
    def make_csv(self,path,count=230):
        rows=[]
        for i in range(count):
            p=100+i*.1
            rows.append({"time":f"2026-01-{1+i//24:02d} {i%24:02d}:00:00","open":p,"high":p+1,"low":p-1,"close":p+.2,"spread":2})
        pd.DataFrame(rows).to_csv(path,index=False)
    def test_sma_warmup_and_feature_columns(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/"in.csv"; out=Path(d)/"out.csv"; self.make_csv(src)
            result=build_features(src,out); df=pd.read_csv(out)
            self.assertEqual(result["rows"],230); self.assertEqual(result["valid_sma200"],31)
            self.assertTrue(pd.isna(df.loc[198,"sma_200"])); self.assertEqual(df.loc[199,"trend_21_55"],"UP")
            self.assertTrue((df["session"]=="UNKNOWN").all())
    def test_no_lookahead_prefix_invariance(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/"in.csv"; full=Path(d)/"full.csv"; prefix=Path(d)/"prefix.csv"
            self.make_csv(src,230); pd.read_csv(src).iloc[:220].to_csv(prefix,index=False)
            build_features(src,full); build_features(prefix,Path(d)/"prefix_out.csv")
            pd.testing.assert_frame_equal(pd.read_csv(full).iloc[:220].reset_index(drop=True),
                pd.read_csv(Path(d)/"prefix_out.csv").reset_index(drop=True),check_dtype=False)
    def test_duplicate_timestamps_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/"in.csv"; self.make_csv(src,10); df=pd.read_csv(src)
            df.loc[1,"time"]=df.loc[0,"time"]; df.to_csv(src,index=False)
            with self.assertRaisesRegex(ValueError,"TIME_ORDER_INVALID"): build_features(src,Path(d)/"out.csv")
if __name__=="__main__": unittest.main(verbosity=2)
