from app.mind.p5_5c_supabase_ingestion_writer.writer import SupabaseIngestionWriter

w = SupabaseIngestionWriter()

result = w.insert(
    "p55a_sources",
    w.health_payload()
)

print(result)
