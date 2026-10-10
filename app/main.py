import argparse
from pathlib import Path
from workflow.orchestrator import DeckOrchestrator


def main():
    parser = argparse.ArgumentParser(description="LLM-based reference PowerPoint correction workflow")
    parser.add_argument("--target", required=True, help="Target deck to correct (.pptx)")
    parser.add_argument("--reference", required=True, help="Reference deck (.pptx)")
    parser.add_argument("--output-dir", default="artifacts/run_001")
    parser.add_argument("--max-iterations", type=int, default=3)
    args = parser.parse_args()
    target, reference = Path(args.target), Path(args.reference)
    if not target.is_file() or not reference.is_file():
        parser.error("Both --target and --reference must point to existing files")
    result = DeckOrchestrator(target, reference, Path(args.output_dir), args.max_iterations).run()
    print("Workflow status:", result.get("status"))
    print("Iterations:", result.get("iteration"))
    print("Final deck:", result.get("final_path"))

if __name__ == "__main__":
    main()
