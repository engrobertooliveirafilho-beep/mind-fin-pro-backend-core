from pathlib import Path

from tools.eldora_media.openai_image_adapter import select_references


def test_select_references_prioritizes_face_lock(tmp_path: Path) -> None:
    other = tmp_path / "BODY_LOCK_V1"
    face = tmp_path / "FACE_LOCK_V1"
    other.mkdir()
    face.mkdir()
    (other / "body.png").write_bytes(b"x")
    (face / "face.png").write_bytes(b"x")
    refs = select_references(tmp_path, limit=1)
    assert refs[0].name == "face.png"