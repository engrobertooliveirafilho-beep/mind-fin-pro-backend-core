from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import StudioConfig
from .queue import TaskQueue
from .state import StudioState


class StudioError(RuntimeError):
    pass


class EldoraAIStudio:
    def __init__(self, config: StudioConfig) -> None:
        self.config = config
        self.config.runtime_root.mkdir(parents=True, exist_ok=True)
        self.queue = TaskQueue(self.config.runtime_root / "queue")
        self.state_store = StudioState(self.config.runtime_root / "studio_state.json")
        self.python = self.config.repo_root / "runtime/eldora_media/.venv/Scripts/python.exe"

    def audit(self) -> dict[str, Any]:
        state = self.state_store.load()
        required = {
            "media_cli": self.config.repo_root / "app/eldora_media_runtime/cli.py",
            "content_brain_cli": self.config.repo_root / "app/eldora_content_brain/cli.py",
            "media_config": self.config.media_config,
            "brain_config": self.config.brain_config,
            "venv_python": self.python,
            "canon_cache": self.config.repo_root / "runtime/eldora_media/canon_cache",
        }
        checks = {name: path.exists() for name, path in required.items()}
        return {
            "schema": "eldora.ai.studio.audit.v1",
            "status": "PASS" if all(checks.values()) else "BLOCKED",
            "checks": checks,
            "queue": self.queue.counts(),
            "state": state,
            "review_required": self.config.review_required,
            "auto_publish": self.config.auto_publish,
            "auto_delete_local": self.config.auto_delete_local,
        }

    def _run(self, args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            args,
            cwd=self.config.repo_root,
            text=True,
            capture_output=True,
            env=env or os.environ.copy(),
            check=False,
        )
        if completed.returncode != 0:
            raise StudioError(
                f"Comando falhou ({completed.returncode}): {' '.join(args)}\n{completed.stderr}"
            )
        return completed

    def research(self) -> Path:
        task = self.queue.enqueue("RESEARCH", {"requested_at": datetime.now().isoformat()})
        try:
            completed = self._run([
                str(self.python),
                "-m",
                "app.eldora_content_brain.cli",
                "research",
                "--config",
                str(self.config.brain_config),
            ])
            run_root = Path(completed.stdout.strip().splitlines()[-1])
            state = self.state_store.load()
            state["last_research_run"] = str(run_root)
            state["last_error"] = None
            self.state_store.save(state)
            return run_root
        except Exception as exc:
            state = self.state_store.load()
            state["last_error"] = str(exc)
            self.state_store.save(state)
            raise

    def generate_candidate(self) -> Path:
        latest_plan = sorted(
            self.config.repo_root.glob("runtime/eldora_content_brain/runs/*/research_plan.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not latest_plan:
            raise StudioError("Nenhum plano de pesquisa disponível.")

        self.config.downloads_root.mkdir(parents=True, exist_ok=True)
        completed = self._run([
            str(self.python),
            "-m",
            "tools.eldora_content_brain.generate_candidate",
            "--plan",
            str(latest_plan[0]),
            "--canon",
            str(self.config.repo_root / "runtime/eldora_media/canon_cache"),
            "--downloads",
            str(self.config.downloads_root),
        ])
        output = Path(completed.stdout.strip().splitlines()[-1])
        state = self.state_store.load()
        state["last_candidate"] = str(output)
        state["last_error"] = None
        self.state_store.save(state)
        return output

    def latest(self) -> dict[str, Any]:
        return self.state_store.load()