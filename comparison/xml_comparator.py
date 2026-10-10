"""Optional package-level XML diagnostics. Not the primary semantic audit."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
from lxml import etree


def pptx_xml_signatures(path: Path) -> dict[str, str]:
    signatures = {}
    with ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(".xml") or name in {"docProps/core.xml", "docProps/app.xml"}:
                continue
            try:
                root = etree.fromstring(archive.read(name))
                canonical = etree.tostring(root, method="c14n", with_comments=False)
                signatures[name] = sha256(canonical).hexdigest()
            except etree.XMLSyntaxError:
                continue
    return signatures


def compare_signatures(reference: dict[str, str], target: dict[str, str]) -> list[dict[str, str]]:
    differences = []
    for name in sorted(set(reference) | set(target)):
        if name not in reference:
            differences.append({"part": name, "difference": "only_in_target"})
        elif name not in target:
            differences.append({"part": name, "difference": "only_in_reference"})
        elif reference[name] != target[name]:
            differences.append({"part": name, "difference": "content_differs"})
    return differences
