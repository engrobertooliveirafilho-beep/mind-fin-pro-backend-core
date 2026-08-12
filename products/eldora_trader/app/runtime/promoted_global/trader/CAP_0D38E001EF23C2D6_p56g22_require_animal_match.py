from pathlib import Path

p = Path("app/mind/p5_6g22_youtube_pedigree_harvester/harvester.py")
text = p.read_text(encoding="utf-8")

text = text.replace(
'status = "NEEDS_TRANSCRIPT_EXTRACTION" if score >= 70 else "LOW_SIGNAL"',
'status = "NEEDS_TRANSCRIPT_EXTRACTION" if (score >= 70 and animal_match and domain_match and not hard_negative) else "LOW_SIGNAL"'
)

p.write_text(text, encoding="utf-8")

print("PATCHED_G22_REQUIRE_ANIMAL_MATCH=True")
