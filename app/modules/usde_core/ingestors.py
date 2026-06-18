from __future__ import annotations
import csv, json, re
from pathlib import Path

def parse_numbers(text: str) -> list[int]:
    return [int(x) for x in re.findall(r"\d+", text)]

def load_txt_events(path: str) -> list[dict]:
    events = []
    for raw in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^\s*(\d+)\s*[-;:,]\s*(.+)$", line)
        if m:
            event_id = int(m.group(1))
            nums = parse_numbers(m.group(2))
        else:
            nums = parse_numbers(line)
            event_id = len(events) + 1
        values = sorted(set(nums))
        if values:
            events.append({"id": event_id, "values": values})
    return sorted(events, key=lambda e: e["id"])

def load_csv_events(path: str) -> list[dict]:
    events = []
    with open(path, newline="", encoding="utf-8-sig", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            nums = []
            for cell in row:
                nums.extend(parse_numbers(str(cell)))
            if not nums:
                continue
            if len(nums) >= 2:
                event_id = nums[0]
                values = sorted(set(nums[1:]))
            else:
                event_id = len(events) + 1
                values = sorted(set(nums))
            events.append({"id": int(event_id), "values": values})
    return sorted(events, key=lambda e: e["id"])

def load_json_events(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "events" in data:
        data = data["events"]
    return sorted(
        [{"id": int(e["id"]), "values": sorted(set(map(int, e["values"])))} for e in data],
        key=lambda e: e["id"]
    )

def load_events(path: str) -> list[dict]:
    suffix = Path(path).suffix.lower()
    if suffix == ".txt":
        return load_txt_events(path)
    if suffix == ".csv":
        return load_csv_events(path)
    if suffix == ".json":
        return load_json_events(path)
    raise ValueError(f"unsupported_file_type:{suffix}")
