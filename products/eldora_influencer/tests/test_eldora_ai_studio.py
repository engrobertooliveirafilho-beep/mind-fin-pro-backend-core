from pathlib import Path

from app.eldora_ai_studio.queue import TaskQueue
from app.eldora_ai_studio.state import StudioState


def test_queue_enqueues_task(tmp_path: Path) -> None:
    queue = TaskQueue(tmp_path / "queue")
    path = queue.enqueue("RESEARCH", {"x": 1})
    assert path.exists()
    assert queue.counts()["pending"] == 1


def test_state_round_trip(tmp_path: Path) -> None:
    store = StudioState(tmp_path / "state.json")
    state = store.load()
    state["last_candidate"] = "x.png"
    store.save(state)
    assert store.load()["last_candidate"] == "x.png"