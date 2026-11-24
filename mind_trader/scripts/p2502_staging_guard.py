import hashlib
from pathlib import Path, PureWindowsPath

def stage(root, destination, relative, expected_sha256):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    rel = PureWindowsPath(relative)
    if rel.anchor or '..' in rel.parts or not rel.parts or any(':' in p for p in rel.parts):
        raise ValueError('unsafe path')
    if destination.is_relative_to(root) or root.is_relative_to(destination):
        raise ValueError('staging must be separate')
    src = root.joinpath(*rel.parts).resolve(strict=True)
    if not src.is_relative_to(root):
        raise ValueError('source escape')
    raw = src.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError('hash mismatch')
    target = destination.joinpath(*rel.parts)
    if not target.resolve().is_relative_to(destination):
        raise ValueError('destination escape')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(raw)
    return dict(sha256=digest, runtime_active=False, promotion_allowed=False)
