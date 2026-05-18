import hashlib, time

class AutoIngestionRuntime:

    def classify(self, item):
        text=(item.get("title","")+" "+item.get("source_type","")+" "+item.get("url","")).lower()
        if any(x in text for x in ["tcc","thesis","dissertation","monografia"]): return "TCC_THESIS"
        if any(x in text for x in ["paper","pubmed","doi","article"]): return "RESEARCH_PAPER"
        if any(x in text for x in ["audio","mp3","wav","podcast"]): return "AUDIO_LECTURE"
        if any(x in text for x in ["video","youtube","mp4","aula","palestra","lecture"]): return "VIDEO_LECTURE"
        if any(x in text for x in ["guideline","who","nih","protocolo"]): return "GUIDELINE"
        return "GENERAL_MEDICAL_CONTENT"

    def ingest(self, item):
        content=item.get("content") or item.get("transcript") or item.get("abstract") or item.get("description") or ""
        fingerprint=hashlib.sha256((item.get("url","")+item.get("title","")+content[:500]).encode("utf-8")).hexdigest()
        source_class=self.classify(item)
        summary=content[:1200] if content else "PENDING_TRANSCRIPTION_OR_CONTENT_EXTRACTION"

        return {
            "status":"AUTO_INGESTION_ITEM_READY",
            "fingerprint":fingerprint,
            "source_class":source_class,
            "title":item.get("title"),
            "url":item.get("url"),
            "language":item.get("language","unknown"),
            "modality":item.get("source_type","unknown"),
            "summary":summary,
            "semantic_ingestion_ready":bool(content),
            "requires_transcription":source_class in ["AUDIO_LECTURE","VIDEO_LECTURE"] and not bool(content),
            "safety_gate":"EDUCATIONAL_RESEARCH_ONLY",
            "created_at":int(time.time())
        }

    def batch(self, items):
        return {
            "status":"AUTO_INGESTION_RUNTIME_OPERATIONAL",
            "count":len(items),
            "items":[self.ingest(x) for x in items]
        }
