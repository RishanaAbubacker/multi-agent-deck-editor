from typing import Any, Literal, TypedDict
from pydantic import BaseModel, Field

Severity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
OperationName = Literal[
    "replace_text", "set_font_size", "set_bold", "set_italic",
    "set_font_name", "set_font_color", "set_shape_position", "set_shape_size"
]

class ShapeInfo(BaseModel):
    shape_id: int
    name: str
    shape_type: str
    left: int
    top: int
    width: int
    height: int
    text: str = ""
    font_runs: list[dict[str, Any]] = Field(default_factory=list)

class SlideInfo(BaseModel):
    slide_number: int
    layout_name: str
    shapes: list[ShapeInfo] = Field(default_factory=list)

class DeckInfo(BaseModel):
    path: str
    slide_width: int
    slide_height: int
    slides: list[SlideInfo] = Field(default_factory=list)

class AuditIssue(BaseModel):
    issue_id: str
    reference_slide: int | None = None
    target_slide: int | None = None
    element_identifier: str = ""
    category: str
    severity: Severity
    reference_value: str = ""
    target_value: str = ""
    description: str
    recommended_correction: str = ""
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0, le=1)

class AuditResult(BaseModel):
    issues: list[AuditIssue] = Field(default_factory=list)
    summary: str = ""

class EditAction(BaseModel):
    action_id: str
    issue_id: str
    slide_number: int
    shape_id: int
    operation: OperationName
    parameters: dict[str, Any] = Field(default_factory=dict)
    reason: str
    postcondition: str

class EditPlan(BaseModel):
    actions: list[EditAction] = Field(default_factory=list)
    items_requiring_review: list[str] = Field(default_factory=list)
    summary: str = ""

class EditExecutionPlan(BaseModel):
    actions: list[EditAction] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

class OperationResult(BaseModel):
    action_id: str
    issue_id: str
    success: bool
    message: str
    slide_number: int
    shape_id: int

class VerificationIssue(BaseModel):
    issue_id: str
    resolved: bool
    reason: str
    evidence: list[str] = Field(default_factory=list)

class VerificationResult(BaseModel):
    passed: bool
    issues: list[VerificationIssue] = Field(default_factory=list)
    new_issues: list[str] = Field(default_factory=list)
    summary: str = ""

class GraphState(TypedDict, total=False):
    target_path: str
    reference_path: str
    current_path: str
    output_dir: str
    iteration: int
    max_iterations: int
    reference_structure: dict[str, Any]
    target_structure: dict[str, Any]
    audit_result: dict[str, Any]
    edit_plan: dict[str, Any]
    execution_results: list[dict[str, Any]]
    verification: dict[str, Any]
    final_path: str
    status: str
