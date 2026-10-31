import pytest
from pathlib import Path
from recovery_pipeline import safe,inventory,recover
def test_traversal_rejected():
 for name in ("../secret","/etc/passwd","a/../b","C:/private","a//b"):
  with pytest.raises(ValueError):safe(name)
def test_missing_inventory_column(tmp_path):
 f=tmp_path/"index.csv";f.write_text("name\na.py\n")
 with pytest.raises(ValueError,match="MISSING_PATH"):list(inventory(f))
def test_invalid_reference_hash(tmp_path):
 f=tmp_path/"index.csv";f.write_text("path,sha256\na.py,bad\n")
 with pytest.raises(ValueError,match="INVALID_SHA"):list(inventory(f))
def test_fail_closed_transport(monkeypatch,tmp_path):
 f=tmp_path/"index.csv";f.write_text("path\na.py\n")
 def unavailable(*args,**kwargs):raise FileNotFoundError("rclone")
 monkeypatch.setattr("recovery_pipeline.subprocess.run",unavailable)
 report=recover(f,"gdrive:MIND",tmp_path/"out")
 assert report["counts"]["failed"]==1 and report["certified"] is False
