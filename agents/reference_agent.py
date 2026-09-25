from pathlib import Path
from document.pptx_inspector import inspect_pptx
from document.pptx_xml import pptx_xml_signatures

class ReferenceAgent:
    name = "reference_agent"

    def run(self, path: Path) -> dict:
        return {
            "deck": inspect_pptx(path).model_dump(),
            "xml_signatures": pptx_xml_signatures(path)
        }
