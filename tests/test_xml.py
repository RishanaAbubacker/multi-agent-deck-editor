from pathlib import Path
from zipfile import ZipFile
from document.pptx_xml import pptx_xml_signatures

def test_pptx_xml_signature_function(tmp_path: Path):
    pptx = tmp_path/"test.pptx"
    with ZipFile(pptx, "w") as zf:
        zf.writestr("ppt/slides/slide1.xml",
                    "<p:sld xmlns:p='http://schemas.openxmlformats.org/presentationml/2006/main'/>")
        zf.writestr("docProps/core.xml", "<core/>")
    signatures = pptx_xml_signatures(pptx)
    assert "ppt/slides/slide1.xml" in signatures
    assert "docProps/core.xml" not in signatures
