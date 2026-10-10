from pathlib import Path
from document.pptx_inspector import inspect_pptx

class ReferenceAgent:
    """Deterministically extracts reference-deck structure; it does not call an LLM."""
    def run(self, reference_path: Path) -> dict:
        return inspect_pptx(reference_path).model_dump()
