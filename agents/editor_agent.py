import json
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from llm.model_factory import get_chat_model
from prompts.editor import EDITOR_SYSTEM_PROMPT, EDITOR_USER_PROMPT
from schemas.models import EditPlan, EditExecutionPlan, OperationResult
from document.pptx_editor import SUPPORTED_OPERATIONS, apply_edit_plan
from document.pptx_inspector import inspect_pptx

class EditorAgent:
    """LLM chooses exact approved operations; Python executes them on the PPTX."""
    def __init__(self, llm=None):
        self.llm = llm or get_chat_model()
        self.chain = ChatPromptTemplate.from_messages([
            ("system", EDITOR_SYSTEM_PROMPT), ("human", EDITOR_USER_PROMPT)
        ]) | self.llm.with_structured_output(EditExecutionPlan)

    def run(self, reference_path: Path, target_path: Path, output_path: Path, plan: EditPlan) -> list[dict]:
        reference = inspect_pptx(reference_path).model_dump()
        target = inspect_pptx(target_path).model_dump()
        execution_plan = self.chain.invoke({
            "reference_structure": json.dumps(reference, ensure_ascii=False),
            "target_structure": json.dumps(target, ensure_ascii=False),
            "edit_plan": plan.model_dump_json(indent=2),
            "supported_operations": json.dumps(SUPPORTED_OPERATIONS),
        })
        # Only execute operations that were present in the approved plan.
        approved_by_id = {a.action_id: a for a in plan.actions}
        approved_actions = []
        for proposed in execution_plan.actions:
            approved = approved_by_id.get(proposed.action_id)
            # The editor LLM may select approved actions, but cannot mutate the
            # planner-approved operation or its parameters.
            if approved and proposed.model_dump() == approved.model_dump():
                approved_actions.append(approved)
        results = apply_edit_plan(target_path, output_path, approved_actions)
        return [r.model_dump() for r in results]
