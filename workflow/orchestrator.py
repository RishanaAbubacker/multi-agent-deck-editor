from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents.rules_agent import RulesAgent
from agents.reference_agent import ReferenceAgent
from agents.deck_analyzer import DeckAnalyzer
from agents.planner_agent import PlannerAgent
from agents.editor_agent import EditorAgent
from agents.verifier_agent import VerifierAgent
from schemas.models import ExecutionState, AgentExecution
from state.execution_state import StateManager
from state.audit_logger import AuditLogger
from state.artifact_manager import ArtifactManager


class GraphState(TypedDict):
    current_path: str
    reference_path: str
    rules_path: str
    iteration: int
    max_iterations: int
    issues: list
    plan: object
    changes: list
    verification: object


class DeckOrchestrator:
    """LangGraph controller for the multi-agent PPT editing workflow."""

    def __init__(self, deck_path: Path, reference_path: Path, rules_path: Path,
                 max_iterations: int = 3, run_id: str | None = None):
        self.deck_path = deck_path
        self.reference_path = reference_path
        self.rules_path = rules_path
        self.max_iterations = max_iterations
        self.run_id = run_id or f"ppt_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"

        self.artifacts = ArtifactManager(Path("artifacts") / self.run_id)
        self.state_manager = StateManager(self.artifacts.state_path)
        self.audit = AuditLogger(self.artifacts.audit_path)
        self.state = ExecutionState(
            run_id=self.run_id,
            input={"deck": str(deck_path), "reference": str(reference_path), "rules": str(rules_path)},
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        self.rules_agent = RulesAgent()
        self.reference_agent = ReferenceAgent()
        self.analyzer = DeckAnalyzer()
        self.planner = PlannerAgent()
        self.editor = EditorAgent()
        self.verifier = VerifierAgent()
        self.rules_doc = None
        self.reference_info = None
        self.graph = self._build_graph()

    def checkpoint(self):
        self.state_manager.save(self.state)

    def record(self, agent, iteration, status, summary):
        self.state.agents.append(AgentExecution(
            agent=agent, iteration=iteration, status=status,
            reasoning_summary=summary
        ))
        self.audit.log("agent_execution", {
            "agent": agent, "iteration": iteration,
            "status": status, "summary": summary
        })
        self.checkpoint()

    def load_context(self, state: GraphState):
        deck = self.artifacts.copy_input(self.deck_path, "deck.pptx")
        reference = self.artifacts.copy_input(self.reference_path, "reference.pptx")
        rules = self.artifacts.copy_input(self.rules_path, "rules.md")

        self.rules_doc = self.rules_agent.run(rules)
        self.record("rules_agent", 0, "COMPLETED", f"Loaded {len(self.rules_doc.rules)} rules.")
        self.reference_info = self.reference_agent.run(reference)
        self.record("reference_agent", 0, "COMPLETED",
                    f"Inspected {len(self.reference_info['deck']['slides'])} reference slides.")

        self.state.current_artifact = str(deck)
        self.checkpoint()
        return {**state, "current_path": str(deck), "reference_path": str(reference),
                "rules_path": str(rules), "iteration": 0}

    def analyze(self, state: GraphState):
        iteration = state["iteration"] + 1
        _, issues = self.analyzer.run(Path(state["current_path"]), [r.text for r in self.rules_doc.rules])
        self.state.iteration = iteration
        self.state.issues = issues
        self.record("deck_analyzer", iteration, "COMPLETED", f"Detected {len(issues)} issues.")
        return {**state, "iteration": iteration, "issues": issues}

    def plan(self, state: GraphState):
        plan = self.planner.run(state["issues"])
        self.state.assumptions.extend(
            {"iteration": state["iteration"], "agent": "planner_agent", "assumption": x}
            for x in plan.assumptions
        )
        self.audit.log("plan_created", {
            "iteration": state["iteration"],
            "actions": [a.model_dump() for a in plan.actions],
            "assumptions": plan.assumptions,
        })
        self.record("planner_agent", state["iteration"], "COMPLETED", f"Planned {len(plan.actions)} actions.")
        return {**state, "plan": plan}

    def edit(self, state: GraphState):
        iteration_dir = self.artifacts.iteration_dir(state["iteration"])
        output = iteration_dir / "working.pptx"
        changes = self.editor.run(Path(state["current_path"]), output, state["plan"])
        self.state.changes.extend(changes)
        self.audit.log("changes_applied", {"iteration": state["iteration"], "changes": changes})
        self.record("editor_agent", state["iteration"], "COMPLETED", f"Applied {len(changes)} changes.")
        return {**state, "current_path": str(output), "changes": changes}

    def verify(self, state: GraphState):
        verification = self.verifier.run(Path(state["current_path"]), Path(state["reference_path"]), state.get("changes", []))
        self.state.verification = verification
        iteration_dir = self.artifacts.iteration_dir(state["iteration"])
        (iteration_dir / "comparison.json").write_text(json.dumps({
            "xml_difference_count": len(verification.xml_differences),
            "xml_differences": verification.xml_differences,
        }, indent=2), encoding="utf-8")
        (iteration_dir / "verification.json").write_text(verification.model_dump_json(indent=2), encoding="utf-8")
        self.record("verifier_agent", state["iteration"], "COMPLETED",
                    f"passed={verification.passed}; remaining={len(verification.issues)}")
        self.state.previous_artifact = self.state.current_artifact
        self.state.current_artifact = state["current_path"]
        self.checkpoint()
        return {**state, "verification": verification}

    def route_after_verify(self, state: GraphState):
        if state["verification"].passed or state["iteration"] >= state["max_iterations"]:
            return "finish"
        return "retry"

    def finish(self, state: GraphState):
        final = self.artifacts.save_final(Path(state["current_path"]))
        self.state.current_artifact = str(final)
        self.state.status = "COMPLETED"
        self.audit.log("run_completed", {"run_id": self.run_id, "status": self.state.status, "final_artifact": str(final)})
        self.checkpoint()
        return state

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
        graph.add_conditional_edges("plan", lambda s: "edit" if s["plan"].actions else "verify",
                                    {"edit": "edit", "verify": "verify"})
        graph.add_edge("edit", "verify")
        graph.add_conditional_edges("verify", self.route_after_verify,
                                    {"retry": "analyze", "finish": "finish"})
        graph.add_edge("finish", END)
        return graph.compile()

    def run(self):
        self.audit.log("run_started", {"run_id": self.run_id})
        self.checkpoint()
        initial: GraphState = {
            "current_path": "", "reference_path": "", "rules_path": "",
            "iteration": 0, "max_iterations": self.max_iterations,
            "issues": [], "plan": None, "changes": [], "verification": None,
        }
        self.graph.invoke(initial)
        return self.state
