import json
from langchain_core.prompts import ChatPromptTemplate
from llm.model_factory import get_chat_model
from prompts.audit import AUDIT_SYSTEM_PROMPT, AUDIT_USER_PROMPT
from schemas.models import AuditResult
from document.pptx_inspector import inspect_pptx
from pathlib import Path

class DeckAnalyzer:
    """LLM-based slide-by-slide auditor (one structured LLM call per analysis)."""
    def __init__(self, llm=None):
        self.llm = llm or get_chat_model()
        self.chain = ChatPromptTemplate.from_messages([
            ("system", AUDIT_SYSTEM_PROMPT), ("human", AUDIT_USER_PROMPT)
        ]) | self.llm.with_structured_output(AuditResult)

    def run(self, reference_path: Path, target_path: Path) -> AuditResult:
        reference = inspect_pptx(reference_path).model_dump()
        target = inspect_pptx(target_path).model_dump()
        return self.chain.invoke({
            "reference_structure": json.dumps(reference, ensure_ascii=False),
            "target_structure": json.dumps(target, ensure_ascii=False),
        })
