from typing import Any, Literal
from pydantic import BaseModel, Field

class Rule(BaseModel):
    category: str
    text: str

class RulesDocument(BaseModel):
    source: str
    rules: list[Rule] = Field(default_factory=list)

class ShapeInfo(BaseModel):
    shape_id: int
    shape_type: str
    name: str
    left: int
    top: int
    width: int
    height: int
    text: str = ""

class SlideInfo(BaseModel):
    slide_number: int
    layout_name: str
    shapes: list[ShapeInfo] = Field(default_factory=list)

class DeckInfo(BaseModel):
    path: str
    slide_width: int
    slide_height: int
    slides: list[SlideInfo] = Field(default_factory=list)

class Issue(BaseModel):
    issue_id: str
    severity: Literal["LOW","MEDIUM","HIGH"]
    category: str
    description: str
    slide_number: int | None = None

class EditAction(BaseModel):
    action_id: str
    action: str
    slide_number: int
    shape_id: int | None = None
    reason: str
    old_value: str | None = None
    new_value: str | None = None

class EditPlan(BaseModel):
    actions: list[EditAction] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)

class AgentExecution(BaseModel):
    agent: str
    iteration: int
    status: str
    input_artifacts: list[str] = Field(default_factory=list)
    output_artifacts: list[str] = Field(default_factory=list)
    reasoning_summary: str = ""

class VerificationResult(BaseModel):
    passed: bool
    issues: list[Issue] = Field(default_factory=list)
    xml_differences: list[dict[str,Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

class ExecutionState(BaseModel):
    run_id: str
    status: str = "RUNNING"
    iteration: int = 0
    input: dict[str,str] = Field(default_factory=dict)
    agents: list[AgentExecution] = Field(default_factory=list)
    artifacts: list[dict[str,Any]] = Field(default_factory=list)
    changes: list[dict[str,Any]] = Field(default_factory=list)
    assumptions: list[dict[str,Any]] = Field(default_factory=list)
    issues: list[Issue] = Field(default_factory=list)
    verification: VerificationResult | None = None
    current_artifact: str = ""
    previous_artifact: str = ""
    started_at: str = ""
    updated_at: str = ""
