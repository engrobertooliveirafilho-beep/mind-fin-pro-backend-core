import re
import json
from pathlib import Path
from html import unescape

src = Path("reports/P5.6G28_ABBI_PEDIGREE_EXTRACTION/fetched_profiles")
out = Path("reports/P5.6G28_ABBI_PEDIGREE_EXTRACTION")
rows = []

def clean_html(html):
    html = re.sub(r"(?is)<script.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?</style>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

for f in sorted(src.glob("*.html")):
    html = f.read_text(encoding="utf-8", errors="ignore")
    text = clean_html(html)

    Path(out / f"{f.stem}_text.txt").write_text(text, encoding="utf-8")

    signals = []
    for pat in ["Sire", "Dam", "GrandSire", "GrandDam", "Animal", "ABBI#", "Pedigree"]:
        for m in re.finditer(pat, text, flags=re.I):
            start = max(0, m.start()-180)
            end = min(len(text), m.end()+300)
            signals.append({
                "pattern": pat,
                "context": text[start:end]
            })

    rows.append({
        "file": str(f),
        "animal_id": f.stem,
        "text_length": len(text),
        "signals_found": len(signals),
        "signals": signals[:30]
    })

Path(out / "P56G28C_ABBI_TEXT_SIGNAL_AUDIT.json").write_text(
    json.dumps(rows, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps([
    {
        "animal_id": r["animal_id"],
        "text_length": r["text_length"],
        "signals_found": r["signals_found"]
    }
    for r in rows
], indent=2))
