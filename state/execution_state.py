from datetime import datetime, timezone
from pathlib import Path
from schemas.models import ExecutionState

def utc_now():
    return datetime.now(timezone.utc).isoformat()

class StateManager:
    def __init__(self, path: Path):
        self.path = path

    def save(self, state: ExecutionState):
        state.updated_at = utc_now()
        self.path.write_text(state.model_dump_json(indent=2), encoding="utf-8")

    def load(self):
        return ExecutionState.model_validate_json(
            self.path.read_text(encoding="utf-8")
        )
