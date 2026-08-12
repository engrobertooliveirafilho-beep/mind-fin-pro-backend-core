from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path

from openai import OpenAI


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--canon", required=True, type=Path)
    parser.add_argument("--downloads", required=True, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.plan.read_text(encoding="utf-8"))
    decisions = payload.get("decisions", [])
    if not decisions:
        raise RuntimeError("Plano sem decisões aprovadas.")

    decision = decisions[0]
    prompt_file = sorted((args.plan.parent / "prompts").glob("*.txt"))[0]
    prompt = prompt_file.read_text(encoding="utf-8")

    supported = {".jpg", ".jpeg", ".png", ".webp"}
    refs = [
        p for p in args.canon.rglob("*")
        if p.is_file()
        and p.suffix.lower() in supported
        and ("FACE_LOCK_V1" in str(p).upper() or "MASTER_CANON" in str(p).upper())
    ]
    refs = sorted(refs)[:6]
    if not refs:
        raise RuntimeError("Referências canônicas ausentes.")

    streams = [p.open("rb") for p in refs]
    try:
        response = OpenAI().images.edit(
            model=os.getenv("ELDORA_IMAGE_MODEL", "gpt-image-1.5"),
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

    if not response.data:
        raise RuntimeError("API não retornou imagem.")

    args.downloads.mkdir(parents=True, exist_ok=True)
    output = args.downloads / f"{decision['content_id']}_CANDIDATE.png"
    item = response.data[0]
    if getattr(item, "b64_json", None):
        output.write_bytes(base64.b64decode(item.b64_json))
    elif getattr(item, "url", None):
        import urllib.request
        urllib.request.urlretrieve(item.url, output)
    else:
        raise RuntimeError("Resposta sem imagem.")

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())