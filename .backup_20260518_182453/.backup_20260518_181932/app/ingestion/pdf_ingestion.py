from app.ingestion.semantic_chunking import SemanticChunker
class PDFIngestionRuntime:
    def ingest_text(self, title: str, extracted_text: str):
        return {'title': title, 'modality': 'PDF', 'chunks': SemanticChunker().chunk(extracted_text), 'semantic_ingestion_ready': True}