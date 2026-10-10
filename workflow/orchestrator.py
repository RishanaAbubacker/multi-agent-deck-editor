from pathlib import Path
import json
from langgraph.graph import StateGraph, END
from agents.reference_agent import ReferenceAgent
from agents.deck_analyzer import DeckAnalyzer
from agents.planner_agent import PlannerAgent
from agents.editor_agent import EditorAgent
from agents.verifier_agent import VerifierAgent
from document.pptx_inspector import inspect_pptx
from schemas.models import GraphState, AuditResult, EditPlan, VerificationResult
from state.artifact_manager import ArtifactManager
from state.audit_logger import AuditLogger

class DeckOrchestrator:
    """Existing six-node workflow with structured LangChain LLM calls."""
    def __init__(self, target_path: Path, reference_path: Path, output_dir: Path, max_iterations: int = 3):
        self.target_path = target_path.resolve()
        self.reference_path = reference_path.resolve()
        self.artifacts = ArtifactManager(output_dir.resolve())
        self.audit = AuditLogger(self.artifacts.root / "audit_log.jsonl")
        self.max_iterations = max_iterations
        self.reference_agent = ReferenceAgent()
        self.analyzer = DeckAnalyzer()
        self.planner = PlannerAgent()
        self.editor = EditorAgent()
        self.verifier = VerifierAgent()
        self.graph = self._build_graph()

    def load_context(self, state: GraphState) -> GraphState:
        target = self.artifacts.copy_input(self.target_path, "target.pptx")
        reference = self.artifacts.copy_input(self.reference_path, "reference.pptx")
        reference_structure = self.reference_agent.run(reference)
        target_structure = inspect_pptx(target).model_dump()
        self.audit.log("context_loaded", {"target": str(target), "reference": str(reference)})
        return {**state, "target_path": str(target), "current_path": str(target),
                "reference_path": str(reference), "reference_structure": reference_structure,
                "target_structure": target_structure, "iteration": 0, "status": "RUNNING"}

    def analyze(self, state: GraphState) -> GraphState:
        iteration = state.get("iteration", 0) + 1
        result = self.analyzer.run(Path(state["reference_path"]), Path(state["current_path"]))
        self.artifacts.write_json(f"audit_iteration_{iteration}.json", result.model_dump())
        self.audit.log("audit_completed", {"iteration": iteration, "issue_count": len(result.issues)})
        return {**state, "iteration": iteration, "audit_result": result.model_dump(),
                "target_structure": inspect_pptx(Path(state["current_path"])).model_dump()}

    def plan(self, state: GraphState) -> GraphState:
        audit_result = AuditResult.model_validate(state["audit_result"])
        target_structure = state["target_structure"]
        plan = self.planner.run(audit_result, target_structure)
        self.artifacts.write_json(f"edit_plan_iteration_{state['iteration']}.json", plan.model_dump())
        self.audit.log("plan_created", {"iteration": state["iteration"], "action_count": len(plan.actions)})
        return {**state, "edit_plan": plan.model_dump(), "execution_results": []}

    def edit(self, state: GraphState) -> GraphState:
        plan = EditPlan.model_validate(state["edit_plan"])
        out = self.artifacts.iteration_dir(state["iteration"]) / "working.pptx"
        results = self.editor.run(Path(state["reference_path"]), Path(state["current_path"]), out, plan)
        self.artifacts.write_json(f"edit_execution_iteration_{state['iteration']}.json", results)
        self.audit.log("edits_executed", {"iteration": state["iteration"], "results": results})
        return {**state, "current_path": str(out), "execution_results": results}

    def verify(self, state: GraphState) -> GraphState:
        audit_result = AuditResult.model_validate(state.get("audit_result", {}))
        plan = EditPlan.model_validate(state.get("edit_plan", {}))
        results = state.get("execution_results", [])
        verification = self.verifier.run(Path(state["reference_path"]), Path(state["current_path"]),
                                         audit_result, plan, results)
        self.artifacts.write_json(f"verification_iteration_{state['iteration']}.json", verification.model_dump())
        self.audit.log("verification_completed", {"iteration": state["iteration"], "passed": verification.passed})
        return {**state, "verification": verification.model_dump()}

    def route_after_verify(self, state: GraphState) -> str:
        result = VerificationResult.model_validate(state["verification"])
        if result.passed:
            return "finish"
        if state["iteration"] >= state["max_iterations"]:
            return "finish"
        return "retry"

    def finish(self, state: GraphState) -> GraphState:
        final_path = self.artifacts.save_final(Path(state["current_path"]))
        verification = VerificationResult.model_validate(state["verification"]) if state.get("verification") else None
        status = "VERIFIED" if verification and verification.passed else "UNVERIFIED"
        self.artifacts.write_json("run_summary.json", {
            "status": status, "iteration": state.get("iteration", 0),
            "final_path": str(final_path),
            "verification": verification.model_dump() if verification else None,
        })
        self.audit.log("run_finished", {"status": status, "final_path": str(final_path)})
        return {**state, "final_path": str(final_path), "status": status}

    def _build_graph(self):
        graph = StateGraph(GraphState)
        graph.add_node("load_context", self.load_context)
        graph.add_node("analyze", self.analyze)
        graph.add_node("plan", self.plan)
        graph.add_node("edit", self.edit)
        graph.add_node("verify", self.verify)
        graph.add_node("finish", self.finish)
        graph.set_entry_point("load_context")
        graph.add_edge("load_context", "analyze")
        graph.add_edge("analyze", "plan")
        graph.add_conditional_edges("plan", lambda s: "edit" if s.get("edit_plan", {}).get("actions") else "verify",
                                    {"edit": "edit", "verify": "verify"})
        graph.add_edge("edit", "verify")
        graph.add_conditional_edges("verify", self.route_after_verify, {"retry": "analyze", "finish": "finish"})
        graph.add_edge("finish", END)
        return graph.compile()

    def run(self) -> GraphState:
        initial: GraphState = {"iteration": 0, "max_iterations": self.max_iterations,
                               "execution_results": [], "status": "RUNNING"}
        return self.graph.invoke(initial)
