from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .adapters import AdapterError, generate_image, generate_video, validate_identity
from .canon import CanonAsset, discover_canon_assets
from .config import Settings
from .manifest import ContentSpec, write_batch_manifest, write_json

NEGATIVE_UNIVERSAL = (
    "No different face, no age shift, no jaw drift, no eye distortion, "
    "no hair color change, no body warp, no plastic skin, no uncanny valley, "
    "no hypersexualization, no fake CGI, no extra fingers, no deformed hands, "
    "no aggressive camera, no exaggerated motion."
)

DEFAULT_CONTENT = [
    {
        "channel": "STATUS",
        "format": "BOM_DIA",
        "scene": "SELFIE_NATURAL",
        "objective": "presença diária",
        "image_prompt": (
            "Usar MASTER_CANON_15 como identidade rígida. Eldora em selfie natural, "
            "luz de janela, café, pele realista, expressão acolhedora, fotografia premium."
        ),
        "video_prompt": (
            "Micro movimento humano: blink natural, respiração discreta, leve sorriso, "
            "câmera fixa, sem face drift."
        ),
        "overlay_text": "Qual sua meta de hoje?",
        "caption": "Bom dia 💛 Me conta sua meta e eu te ajudo a organizar.",
        "cta": "Me manda sua meta no Whats.",
    },
    {
        "channel": "REELS",
        "format": "WHATSAPP_CTA",
        "scene": "HOME_OFFICE",
        "objective": "iniciar conversa no WhatsApp",
        "image_prompt": (
            "Usar MASTER_CANON_15 como identidade rígida. Eldora segurando smartphone "
            "em home office clean, luz natural, roupa neutra, fotografia premium realista."
        ),
        "video_prompt": (
            "Blink natural, leve sorriso, olhar alternando celular e câmera, "
            "movimento mínimo, câmera fixa, sem face drift."
        ),
        "overlay_text": "Eu converso com você no Whats 💛",
        "caption": "Me chama no Whats e me fala o que você precisa resolver hoje.",
        "cta": "Me chama no Whats 💛",
    },
    {
        "channel": "SHORTS",
        "format": "ESTUDO",
        "scene": "NOTEBOOK_CADERNO",
        "objective": "atrair estudantes",
        "image_prompt": (
            "Usar MASTER_CANON_15 como identidade rígida. Eldora estudando com notebook "
            "e caderno, ambiente realista, luz natural, postura concentrada."
        ),
        "video_prompt": (
            "Movimento sutil de escrita e olhar, blink natural, sem alteração facial, "
            "sem movimento agressivo de câmera."
        ),
        "overlay_text": "Me manda o assunto que você travou.",
        "caption": "Me manda no Whats que eu explico de um jeito simples.",
        "cta": "Me manda o tema no Whats.",
    },
]


class PipelineError(RuntimeError):
    pass


class EldoraMediaPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def audit(self) -> dict[str, object]:
        report: dict[str, object] = {
            "repo_root": str(self.settings.repo_root),
            "canon_root": str(self.settings.canon_root),
            "runtime_root": str(self.settings.runtime_root),
            "image_generator_configured": bool(self.settings.image_generator_cmd),
            "video_generator_configured": bool(self.settings.video_generator_cmd),
            "identity_validator_configured": bool(self.settings.identity_validator_cmd),
        }
        try:
            assets = discover_canon_assets(self.settings.canon_root)
            report["canon_status"] = "PASS"
            report["canon_assets"] = len(assets)
        except Exception as exc:
            report["canon_status"] = "BLOCKED"
            report["canon_error"] = str(exc)
        return report

    def plan(self, count: int = 3) -> Path:
        assets = discover_canon_assets(self.settings.canon_root)
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_root = self.settings.output_root / batch_id
        prompts_root = batch_root / "01_PROMPTS_READY"
        prompts_root.mkdir(parents=True, exist_ok=True)

        specs: list[ContentSpec] = []
        for index in range(count):
            base = DEFAULT_CONTENT[index % len(DEFAULT_CONTENT)]
            content_id = f"ELDORA_{batch_id}_{index + 1:03d}_{base['format']}"
            spec = ContentSpec(
                content_id=content_id,
                channel=base["channel"],
                format=base["format"],
                scene=base["scene"],
                objective=base["objective"],
                image_prompt=base["image_prompt"],
                video_prompt=base["video_prompt"],
                overlay_text=base["overlay_text"],
                caption=base["caption"],
                cta=base["cta"],
                negative_prompt=NEGATIVE_UNIVERSAL,
            )
            specs.append(spec)
            write_json(prompts_root / f"{content_id}.json", asdict(spec))

        canon_payload = [
            {"path": str(asset.path), "sha256": asset.sha256, "bytes": asset.bytes}
            for asset in assets
        ]
        write_batch_manifest(batch_root / "batch_manifest.json", batch_id, specs, canon_payload)
        return batch_root

    def produce(self, count: int = 3) -> Path:
        if not self.settings.image_generator_cmd:
            raise PipelineError("ELDORA_IMAGE_GENERATOR_CMD ausente.")
        if not self.settings.identity_validator_cmd:
            raise PipelineError("ELDORA_IDENTITY_VALIDATOR_CMD ausente. Produção bloqueada por segurança.")

        batch_root = self.plan(count=count)
        manifest = json.loads((batch_root / "batch_manifest.json").read_text(encoding="utf-8"))
        reference_dir = self.settings.canon_root
        raw_root = batch_root / "02_GENERATED_RAW"
        approved_root = batch_root / "03_APPROVED_POSTS"
        rejected_root = batch_root / "04_REJECTED_DRIFT"
        reports_root = batch_root / "05_VALIDATION_REPORTS"

        for item in manifest["items"]:
            content_id = item["content_id"]
            prompt_file = batch_root / "01_PROMPTS_READY" / f"{content_id}.json"
            item_raw = raw_root / content_id
            generate_image(
                self.settings.image_generator_cmd,
                prompt_file,
                reference_dir,
                item_raw,
                content_id,
            )

            candidates = sorted(
                p for p in item_raw.rglob("*")
                if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
            )
            if not candidates:
                raise PipelineError(f"Gerador não produziu imagem para {content_id}.")

            image = candidates[0]
            report_file = reports_root / f"{content_id}_identity.json"
            try:
                validate_identity(
                    self.settings.identity_validator_cmd,
                    image,
                    reference_dir,
                    report_file,
                )
            except AdapterError:
                rejected_root.mkdir(parents=True, exist_ok=True)
                shutil.copy2(image, rejected_root / image.name)
                continue

            approved_root.mkdir(parents=True, exist_ok=True)
            approved_image = approved_root / image.name
            shutil.copy2(image, approved_image)

            if self.settings.video_generator_cmd:
                video_root = batch_root / "06_VIDEO_RAW" / content_id
                generate_video(
                    self.settings.video_generator_cmd,
                    prompt_file,
                    approved_image,
                    video_root,
                    content_id,
                )

        return batch_root