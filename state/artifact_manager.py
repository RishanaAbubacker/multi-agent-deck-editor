import json
import shutil
from pathlib import Path
from uuid import uuid4

class ArtifactManager:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.iterations = self.root / "iterations"
        self.iterations.mkdir(exist_ok=True)

    def iteration_dir(self, iteration: int) -> Path:
        path = self.iterations / f"iteration_{iteration:02d}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def copy_input(self, source: Path, name: str) -> Path:
        dest = self.root / "inputs" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        return dest

    def write_json(self, name: str, data) -> Path:
        path = self.root / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def save_final(self, source: Path) -> Path:
        dest = self.root / "final" / "finished.pptx"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        return dest
