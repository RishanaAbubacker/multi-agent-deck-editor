from pathlib import Path
from comparison.xml_comparator import compare_pptx_xml
from document.pptx_inspector import inspect_pptx
from schemas.models import Issue, VerificationResult

class VerifierAgent:
    name = "verifier_agent"

    def run(self, edited_path: Path, reference_path: Path, expected_changes):
        deck = inspect_pptx(edited_path)
        issues = []
        for slide in deck.slides:
            for shape in slide.shapes:
                if shape.text and shape.text != shape.text.strip():
                    issues.append(Issue(
                        issue_id=f"verify-s{slide.slide_number}-sh{shape.shape_id}",
                        severity="LOW",
                        category="content_formatting",
                        description="Leading/trailing whitespace remains.",
                        slide_number=slide.slide_number
                    ))
        return VerificationResult(
            passed=not issues,
            issues=issues,
            xml_differences=compare_pptx_xml(edited_path, reference_path),
            notes=[
                "XML differences are reported for inspection.",
                "Different-content decks are not expected to have identical XML."
            ]
        )
