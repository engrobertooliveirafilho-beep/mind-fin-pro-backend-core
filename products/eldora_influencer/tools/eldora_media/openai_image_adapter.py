from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path

from openai import OpenAI


SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}


def select_references(reference_dir: Path, limit: int = 6) -> list[Path]:
    preferred = []
    fallback = []
    for path in reference_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        text = str(path).upper()
        if "FACE_LOCK_V1" in text or "MASTER_CANON_15" in text or "MASTER_CANON_10" in text:
            preferred.append(path)
        else:
            fallback.append(path)
    refs = sorted(preferred)[:limit] or sorted(fallback)[:limit]
    if not refs:
        raise RuntimeError(f"Nenhuma referência encontrada em {reference_dir}")
    return refs


def load_prompt(prompt_file: Path) -> str:
    payload = json.loads(prompt_file.read_text(encoding="utf-8"))
    prompt = str(payload.get("image_prompt", "")).strip()
    negative = str(payload.get("negative_prompt", "")).strip()
    if not prompt:
        raise RuntimeError("image_prompt ausente.")
    return (
        f"{prompt}\n\nIDENTITY POLICY: preserve the exact same adult woman from the supplied "
        "canonical references. References are absolute identity ground truth. "
        "Do not redesign, beautify, age-shift, or reinterpret her face. "
        f"\n\nNEGATIVE CONSTRAINTS: {negative}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--reference-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--content-id", required=True)
    parser.add_argument("--model", default=os.getenv("ELDORA_IMAGE_MODEL", "gpt-image-1.5"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    refs = select_references(args.reference_dir)
    if args.check:
        print(json.dumps({
            "status": "READY",
            "references": len(refs),
            "model": args.model,
            "api_key_present": bool(os.getenv("OPENAI_API_KEY")),
        }, indent=2))
        return 0

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY ausente.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    prompt = load_prompt(args.prompt_file)
    client = OpenAI()

    streams = [path.open("rb") for path in refs]
    try:
        result = client.images.edit(
            model=args.model,
            image=streams,
            prompt=prompt,
            input_fidelity="high",
            size="1024x1536",
            quality="high",
            output_format="png",
        )
    finally:
        for stream in streams:
            stream.close()

    if not result.data:
        raise RuntimeError("API não retornou imagem.")

    item = result.data[0]
    output = args.output_dir / f"{args.content_id}.png"
    if getattr(item, "b64_json", None):
        output.write_bytes(base64.b64decode(item.b64_json))
    elif getattr(item, "url", None):
        import urllib.request
        urllib.request.urlretrieve(item.url, output)
    else:
        raise RuntimeError("Resposta sem b64_json ou URL.")

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())