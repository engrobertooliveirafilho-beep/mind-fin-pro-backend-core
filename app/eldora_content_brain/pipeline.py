from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import BrainSettings
from .planner import normalize_plan
from .prompt_builder import build_image_prompt
from .research import research


class ContentBrainPipeline:
    def __init__(self, settings: BrainSettings) -> None:
        self.settings = settings

    def run_research(self) -> Path:
        payload = research(self.settings)
        plan = normalize_plan(payload, self.settings)

        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_root = self.settings.output_root / run_id
        run_root.mkdir(parents=True, exist_ok=True)

        plan_path = run_root / "research_plan.json"
        plan_path.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        prompts_root = run_root / "prompts"
        prompts_root.mkdir(parents=True, exist_ok=True)
        for index, decision in enumerate(plan.get("decisions", []), start=1):
            content_id = decision["content_id"]
            prompt = build_image_prompt(decision)
            (prompts_root / f"{index:02d}_{content_id}.txt").write_text(prompt, encoding="utf-8")

        return run_root

    def load_latest_plan(self) -> tuple[Path, dict[str, Any]]:
        roots = sorted(
            [p for p in self.settings.output_root.iterdir() if p.is_dir()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not roots:
            raise RuntimeError("Nenhuma pesquisa anterior encontrada.")
        plan_path = roots[0] / "research_plan.json"
        return roots[0], json.loads(plan_path.read_text(encoding="utf-8"))