from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


class AdapterError(RuntimeError):
    pass


@dataclass(frozen=True)
class AdapterResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


def _run_template(template: str | None, values: dict[str, str], operation: str) -> AdapterResult:
    if not template:
        raise AdapterError(
            f"{operation} não configurado. Defina a variável de ambiente correspondente antes do modo produce."
        )

    command = template.format(**values)
    completed = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    result = AdapterResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if completed.returncode != 0:
        raise AdapterError(
            f"{operation} falhou com código {completed.returncode}: {completed.stderr.strip()}"
        )
    return result


def generate_image(
    template: str | None,
    prompt_file: Path,
    reference_dir: Path,
    output_dir: Path,
    content_id: str,
) -> AdapterResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    return _run_template(
        template,
        {
            "prompt_file": str(prompt_file),
            "reference_dir": str(reference_dir),
            "output_dir": str(output_dir),
            "content_id": content_id,
        },
        "Gerador de imagem",
    )


def generate_video(
    template: str | None,
    prompt_file: Path,
    source_image: Path,
    output_dir: Path,
    content_id: str,
) -> AdapterResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    return _run_template(
        template,
        {
            "prompt_file": str(prompt_file),
            "source_image": str(source_image),
            "output_dir": str(output_dir),
            "content_id": content_id,
        },
        "Gerador de vídeo",
    )


def validate_identity(
    template: str | None,
    candidate: Path,
    reference_dir: Path,
    report_file: Path,
) -> AdapterResult:
    report_file.parent.mkdir(parents=True, exist_ok=True)
    result = _run_template(
        template,
        {
            "candidate": str(candidate),
            "reference_dir": str(reference_dir),
            "report_file": str(report_file),
        },
        "Validador de identidade",
    )
    if not report_file.exists():
        report_file.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "validator": "external-command",
                    "candidate": str(candidate),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    return result