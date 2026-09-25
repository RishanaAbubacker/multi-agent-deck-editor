from pathlib import Path
from pptx import Presentation
from schemas.models import DeckInfo, SlideInfo, ShapeInfo

def inspect_pptx(path: Path) -> DeckInfo:
    prs = Presentation(str(path))
    slides = []
    for n, slide in enumerate(prs.slides, 1):
        shapes = []
        for shape in slide.shapes:
            text = getattr(shape, "text", "") or ""
            try:
                shape_type = shape.shape_type.name
            except Exception:
                shape_type = str(shape.shape_type)
            shapes.append(ShapeInfo(
                shape_id=shape.shape_id, shape_type=shape_type,
                name=getattr(shape, "name", ""),
                left=shape.left, top=shape.top,
                width=shape.width, height=shape.height, text=text
            ))
        slides.append(SlideInfo(
            slide_number=n,
            layout_name=getattr(slide.slide_layout, "name", ""),
            shapes=shapes
        ))
    return DeckInfo(
        path=str(path),
        slide_width=prs.slide_width,
        slide_height=prs.slide_height,
        slides=slides
    )
