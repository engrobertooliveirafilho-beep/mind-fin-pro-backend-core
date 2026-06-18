import time, json
from app.mind.p5_5s_source_expansion_autopilot.autopilot import SourceExpansionAutopilot
from app.mind.p5_6f1_animal_discovery_engine.engine import AnimalDiscoveryEngine
from app.mind.p5_5t_real_fetcher_search_connector.connector import RealFetcherSearchConnector
from app.mind.p5_5u_real_result_claim_extractor.extractor import RealResultClaimExtractor
from app.mind.p5_5w_video_metadata_extractor.extractor import VideoMetadataExtractor
from app.mind.p5_6b5_youtube_url_resolver.resolver import YouTubeURLResolver
from app.mind.p5_6b4_youtube_acquisition_engine.engine import YouTubeAcquisitionEngine
from app.mind.p5_6b5_judge_real_biomechanics_binder.binder import JudgeRealBiomechanicsBinder
from app.mind.p5_6b6_real_valuation_binder.binder import RealValuationBinder
from app.mind.p5_6b8_real_country_ranking_recalculator.recalculator import RealCountryRankingRecalculator

class AutonomousVideoDiscoveryLoop:
    def cycle(self, limit=20):
        report={}
        report["source_expansion"]=SourceExpansionAutopilot().run_once()
        report["real_fetch"]=RealFetcherSearchConnector().run_once(limit)
        report["claim_extract"]=RealResultClaimExtractor().run_once()
        report["video_metadata"]=VideoMetadataExtractor().run_once()
        report["youtube_resolver"]=YouTubeURLResolver().run_once(limit)
        report["video_cv"]=YouTubeAcquisitionEngine().run_once(limit)
        report["judge_bind"]=JudgeRealBiomechanicsBinder().run_once(10000)
        report["valuation"]=RealValuationBinder().run_once()
        report["country"]=RealCountryRankingRecalculator().run_once()
        return {"status":"P5.6F_AUTONOMOUS_VIDEO_DISCOVERY_LOOP_CYCLE_DONE","report":report}

    def run_forever(self, minutes=30, limit=20):
        while True:
            print(json.dumps(self.cycle(limit),ensure_ascii=False,indent=2))
            time.sleep(minutes*60)

