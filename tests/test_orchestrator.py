from pathlib import Path
from workflow.orchestrator import DeckOrchestrator

def test_orchestrator_builds_langgraph():
    o = DeckOrchestrator(Path('input.pptx'), Path('reference.pptx'), Path('rules.md'), max_iterations=1, run_id='test_run')
    assert o.graph is not None
