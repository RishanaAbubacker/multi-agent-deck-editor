from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
from lxml import etree

VOLATILE_PARTS = {"docProps/core.xml", "docProps/app.xml"}

def canonical_xml_bytes(data: bytes) -> bytes:
    return etree.tostring(
        etree.fromstring(data), method="c14n", with_comments=False
    )

def pptx_xml_signatures(path: Path) -> dict[str,str]:
    result = {}
    with ZipFile(path) as zf:
        for name in sorted(zf.namelist()):
            if name in VOLATILE_PARTS or not name.endswith(".xml"):
                continue
            result[name] = sha256(canonical_xml_bytes(zf.read(name))).hexdigest()
    return result
