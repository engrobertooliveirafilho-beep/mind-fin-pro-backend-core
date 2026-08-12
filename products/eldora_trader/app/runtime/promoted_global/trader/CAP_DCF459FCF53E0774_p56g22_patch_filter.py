from pathlib import Path

p = Path("app/mind/p5_6g22_youtube_pedigree_harvester/harvester.py")
text = p.read_text(encoding="utf-8")

text = text.replace(
'''            score = 0
            if "sire" in text: score += 30
            if "dam" in text: score += 30
            if "pedigree" in text: score += 20
            if "abbi" in text: score += 10
            if "pbr" in text: score += 10

            candidates.append({
                **r,
                "query": block["query"],
                "pedigree_signal_score": score,
                "status": "NEEDS_TRANSCRIPT_EXTRACTION" if score >= 40 else "LOW_SIGNAL"
            })''',
'''            query_animal = block["query"].split(" bucking bull")[0].lower()
            hard_negative = any(x in text for x in ["pitbull", "doglover", "audiobook", "textile", "worm gear", "oil seal"])
            animal_match = query_animal in text
            domain_match = any(x in text for x in ["bucking", "bull", "pbr", "abbi", "rodeo", "prca"])
            
            score = 0
            if animal_match: score += 40
            if domain_match: score += 20
            if "sire" in text: score += 25
            if "dam" in text: score += 25
            if "pedigree" in text: score += 20
            if "abbi" in text: score += 10
            if "pbr" in text: score += 10
            if hard_negative: score = 0

            status = "NEEDS_TRANSCRIPT_EXTRACTION" if score >= 70 else "LOW_SIGNAL"

            candidates.append({
                **r,
                "query": block["query"],
                "animal_match": animal_match,
                "domain_match": domain_match,
                "hard_negative": hard_negative,
                "pedigree_signal_score": score,
                "status": status
            })'''
)

p.write_text(text,encoding="utf-8")
print("PATCHED_G22_FILTER=True")
