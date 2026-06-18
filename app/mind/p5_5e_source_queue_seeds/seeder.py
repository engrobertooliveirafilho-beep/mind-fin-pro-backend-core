from app.mind.p5_5d_deduplicated_evidence_writer.writer import DeduplicatedEvidenceWriter

REAL_SOURCE_SEEDS = [
 {"source_url":"https://pbr.com/athletes/bulls","source_type":"PBR","title":"PBR Bulls Directory","platform":"web","raw_payload":{"mission":"P5.5E","category":"bull_directory"}},
 {"source_url":"https://americanbuckingbull.com","source_type":"ABBI","title":"American Bucking Bull Inc","platform":"web","raw_payload":{"mission":"P5.5E","category":"registry"}},
 {"source_url":"https://prorodeo.com","source_type":"PRCA","title":"Professional Rodeo Cowboys Association","platform":"web","raw_payload":{"mission":"P5.5E","category":"rodeo_authority"}},
 {"source_url":"https://www.youtube.com/results?search_query=PBR+bull+ride+official+score","source_type":"YOUTUBE","title":"YouTube PBR bull ride official score search","platform":"youtube","raw_payload":{"mission":"P5.5E","category":"video_search"}},
 {"source_url":"https://pbrbrazil.com.br","source_type":"PBR_BRASIL","title":"PBR Brazil","platform":"web","raw_payload":{"mission":"P5.5E","category":"brazil_source"}},
 {"source_url":"https://nfrexperience.com","source_type":"NFR","title":"NFR Experience","platform":"web","raw_payload":{"mission":"P5.5E","category":"event_history"}}
]

class SourceQueueSeeder:
    def __init__(self):
        self.writer=DeduplicatedEvidenceWriter()

    def seed(self):
        inserted=[]
        for item in REAL_SOURCE_SEEDS:
            payload=dict(item)
            payload.setdefault("confidence_score",85)
            payload.setdefault("validation_status","reliable")
            inserted.append(self.writer.upsert_source(payload)[0])
        return inserted

    def audit(self, rows):
        return {
            "status":"P5.5E_SOURCE_QUEUE_SEEDED",
            "total":len(rows),
            "unique_hashes":len(set(r.get("evidence_hash") for r in rows)),
            "ids":[r.get("id") for r in rows]
        }
