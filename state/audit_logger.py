import json
from datetime import datetime, timezone
from pathlib import Path

class AuditLogger:
    def __init__(self, path: Path):
        self.path = path

    def log(self, event_type: str, payload: dict):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            **payload
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
