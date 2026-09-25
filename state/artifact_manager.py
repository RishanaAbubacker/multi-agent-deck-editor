from hashlib import sha256
from pathlib import Path
import shutil
from schemas.models import Artifact

class ArtifactManager:
    def __init__(self, root: Path):
        self.root = root
        self.input_dir = root/"input"
        self.iterations_dir = root/"iterations"
        self.final_dir = root/"final"
        for d in [self.input_dir, self.iterations_dir, self.final_dir]:
            d.mkdir(parents=True, exist_ok=True)
        self.state_path = root/"state.json"
        self.audit_path = root/"audit.jsonl"

    def copy_input(self, source: Path, name: str):
        target = self.input_dir/name
        shutil.copy2(source, target)
        return target

    def iteration_dir(self, iteration: int):
        d = self.iterations_dir/f"iteration_{iteration:02d}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def register(self, path: Path, artifact_type: str, iteration: int, created_by: str):
        return Artifact(
            path=str(path), artifact_type=artifact_type,
            iteration=iteration, created_by=created_by,
            hash=sha256(path.read_bytes()).hexdigest()
        )

    def save_final(self, source: Path):
        target = self.final_dir/"finished.pptx"
        shutil.copy2(source, target)
        return target
