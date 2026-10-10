import json
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from llm.model_factory import get_chat_model
from prompts.verifier import VERIFIER_SYSTEM_PROMPT, VERIFIER_USER_PROMPT
from schemas.models import AuditResult, EditPlan, VerificationResult
from document.pptx_inspector import inspect_pptx

class VerifierAgent:
    def __init__(self, llm=None):
        self.llm = llm or get_chat_model()
        self.chain = ChatPromptTemplate.from_messages([
            ("system", VERIFIER_SYSTEM_PROMPT), ("human", VERIFIER_USER_PROMPT)
        ]) | self.llm.with_structured_output(VerificationResult)

    def run(self, reference_path: Path, edited_path: Path, audit_result: AuditResult,
            edit_plan: EditPlan, execution_results: list[dict]) -> VerificationResult:
        reference = inspect_pptx(reference_path).model_dump()
        edited = inspect_pptx(edited_path).model_dump()
        return self.chain.invoke({
            "reference_structure": json.dumps(reference, ensure_ascii=False),
            "edited_structure": json.dumps(edited, ensure_ascii=False),
            "audit_result": audit_result.model_dump_json(indent=2),
            "edit_plan": edit_plan.model_dump_json(indent=2),
            "execution_results": json.dumps(execution_results, ensure_ascii=False),
        })
