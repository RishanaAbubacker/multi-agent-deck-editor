from pathlib import Path
from document.pptx_xml import pptx_xml_signatures

def compare_pptx_xml(left: Path, right: Path) -> list[dict]:
    a, b = pptx_xml_signatures(left), pptx_xml_signatures(right)
    differences = []
    for part in sorted(set(a) | set(b)):
        if part not in a:
            status = "ONLY_IN_REFERENCE"
        elif part not in b:
            status = "ONLY_IN_LEFT"
        elif a[part] != b[part]:
            status = "DIFFERENT"
        else:
            continue
        differences.append({"part": part, "status": status})
    return differences
