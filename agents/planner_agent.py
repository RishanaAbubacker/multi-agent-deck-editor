import json
from langchain_core.prompts import ChatPromptTemplate
from llm.model_factory import get_chat_model
from prompts.planner import PLANNER_SYSTEM_PROMPT, PLANNER_USER_PROMPT
from schemas.models import AuditResult, EditPlan
from document.pptx_editor import SUPPORTED_OPERATIONS

class PlannerAgent:
    def __init__(self, llm=None):
        self.llm = llm or get_chat_model()
        self.chain = ChatPromptTemplate.from_messages([
            ("system", PLANNER_SYSTEM_PROMPT), ("human", PLANNER_USER_PROMPT)
        ]) | self.llm.with_structured_output(EditPlan)

    def run(self, audit_result: AuditResult, target_structure: dict) -> EditPlan:
        return self.chain.invoke({
            "audit_result": audit_result.model_dump_json(indent=2),
            "target_structure": json.dumps(target_structure, ensure_ascii=False),
            "supported_operations": json.dumps(SUPPORTED_OPERATIONS),
        })
