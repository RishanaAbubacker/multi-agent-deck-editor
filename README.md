# PPT Multi-Agent Editing System

A traceable, resumable MVP for editing PowerPoint decks against a reference/template deck and a rules file.

## Architecture

```text
Input PPTX + Reference PPTX + rules.md
                  |
                  v
             Rules Agent
                  |
                  v
          Reference Agent
                  |
                  v
           Deck Analyzer
                  |
                  v
          Planner / Editor
                  |
                  v
        PPTX Mutation Engine
                  |
                  v
       XML + Semantic Comparison
                  |
                  v
          Verification Agent
                  |
             PASS / RETRY
                  |
                  v
            Orchestrator
```

The **LangGraph-based orchestrator is the central controller**. It owns iteration control, execution state, artifacts, audit logs, and retry decisions.

## Design principles

1. **LLMs reason; Python mutates files.** An eventual LLM planner should output structured edit actions. `python-pptx` performs deterministic mutations.
2. **Reference deck = source of truth for structure/style**, not automatic content source.
3. **Rules are explicit** in `rules.md`.
4. **Every mutation and assumption is logged.**
5. **Every iteration is checkpointed** in `state.json`.
6. **Verification happens after mutation.**
7. XML comparison is evidence, not a claim that two different-content decks should be byte-for-byte identical.

## Project structure

```text
ppt_multi_agent/
├── README.md
├── rules.md
├── requirements.txt
├── main.py
├── .gitignore
├── agents/
│   ├── rules_agent.py
│   ├── reference_agent.py
│   ├── deck_analyzer.py
│   ├── planner_agent.py
│   ├── editor_agent.py
│   └── verifier_agent.py
├── comparison/
│   └── xml_comparator.py
├── document/
│   ├── pptx_inspector.py
│   └── pptx_xml.py
├── schemas/
│   └── models.py
├── state/
│   ├── execution_state.py
│   ├── audit_logger.py
│   └── artifact_manager.py
├── workflow/
│   └── orchestrator.py
├── tests/
│   └── test_xml.py
└── artifacts/
```

## Installation

Python 3.10+:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py --deck input.pptx --reference reference.pptx --rules rules.md --max-iterations 3
```

Each run creates:

```text
artifacts/<run_id>/
├── input/
│   ├── deck.pptx
│   ├── reference.pptx
│   └── rules.md
├── iterations/
│   ├── iteration_01/
│   │   ├── working.pptx
│   │   ├── comparison.json
│   │   └── verification.json
│   └── ...
├── final/
│   └── finished.pptx
├── state.json
└── audit.jsonl
```

## Current MVP

The workflow is orchestrated with **LangGraph**, with conditional routing from verification back to analysis when a retry is required.

- Rules parser
- Reference deck inspection
- PPTX structural inspection
- Deterministic issue detection
- Structured edit plan
- Safe text-whitespace mutation
- PPTX XML package comparison
- Verification
- Execution state
- Artifact tracking
- JSONL audit trail
- Iterative orchestration

## Future production layer

The contracts are designed so you can add:

- OpenAI/other LLM structured outputs
- LangGraph orchestration
- slide rendering + visual diffing
- semantic comparison of slide content
- PowerPoint theme/master analysis
- human approval gates
- persistent database-backed state
- resumable runs
- richer edit operations

Recommended production pattern:

```text
PPTX / rules / reference
        ↓
deterministic extraction
        ↓
LLM planner
        ↓
Pydantic EditPlan
        ↓
deterministic editor
        ↓
XML + visual + semantic verification
        ↓
orchestrator decides PASS / RETRY / HUMAN REVIEW
```

## Git

```bash
git init
git add .
git commit -m "Initial multi-agent PPT editing system"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```
