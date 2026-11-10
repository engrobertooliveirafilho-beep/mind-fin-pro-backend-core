"""R388: regression for pinned-manifest metadata snapshot (offline only)."""
from pathlib import Path
from test_et665_r311_p2404_offline_integration import sample
from mind_trader.research.et665_r311_p2404_offline_integration import analyze_verified_paper_csv

def test_manifest_metadata_not_reread_after_pinned_validation(tmp_path, monkeypatch):
    source, manifest, anchor = sample(tmp_path)
    original = Path.read_text
    def reject_manifest_text_read(self, *args, **kwargs):
        if self == manifest:
            raise AssertionError("manifest must not be re-read after SHA256 verification")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", reject_manifest_text_read)
    result = analyze_verified_paper_csv(source, manifest, anchor, source_id="s1")
    assert result["analysis_valid"]
    assert result["authority_integrity_verified"]
    assert not result["runtime_promotion_allowed"]
