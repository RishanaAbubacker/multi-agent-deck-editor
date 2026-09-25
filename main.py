import argparse
from pathlib import Path
from workflow.orchestrator import DeckOrchestrator

def main():
    p = argparse.ArgumentParser(description="Multi-agent PowerPoint editing workflow")
    p.add_argument("--deck", required=True)
    p.add_argument("--reference", required=True)
    p.add_argument("--rules", default="rules.md")
    p.add_argument("--max-iterations", type=int, default=3)
    p.add_argument("--run-id", default=None)
    args = p.parse_args()

    result = DeckOrchestrator(
        Path(args.deck), Path(args.reference), Path(args.rules),
        args.max_iterations, args.run_id
    ).run()

    print("=== RUN COMPLETE ===")
    print("Run ID:", result.run_id)
    print("Status:", result.status)
    print("Iteration:", result.iteration)
    print("Final artifact:", result.current_artifact)

if __name__ == "__main__":
    main()
