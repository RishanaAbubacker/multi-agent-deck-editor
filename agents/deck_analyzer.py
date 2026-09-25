from pathlib import Path
from document.pptx_inspector import inspect_pptx
from schemas.models import Issue

class DeckAnalyzer:
    name = "deck_analyzer"

    def run(self, path: Path, rules: list[str]):
        deck = inspect_pptx(path)
        issues = []
        for slide in deck.slides:
            for shape in slide.shapes:
                if shape.text and shape.text != shape.text.strip():
                    issues.append(Issue(
                        issue_id=f"whitespace-s{slide.slide_number}-sh{shape.shape_id}",
                        severity="LOW",
                        category="content_formatting",
                        description="Text has leading/trailing whitespace.",
                        slide_number=slide.slide_number
                    ))
        return deck, issues
