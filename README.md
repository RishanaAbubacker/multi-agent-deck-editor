# LLM-Based PowerPoint Correction Workflow

A folder-structured Python project using **LangChain** for structured LLM calls and **LangGraph** for orchestration. It compares a target PowerPoint deck with a reference deck, plans corrections, executes supported edits, and verifies the result.

> Important: The LLM decides what to change. The Python editor writes changes into the `.pptx` file. The LLM cannot directly rewrite the binary PowerPoint package without an execution layer.

## Architecture

```text
load_context -> analyze -> plan -> edit -> verify
                               |         ^      |
                               | no edits|      | failed and retries remain
                               +-------> verify +----> analyze
                                         |
                                       finish
```

Existing workflow nodes are retained: `load_context`, `analyze`, `plan`, `edit`, `verify`, `finish`. There is no rules file and no RulesAgent.

## Folder structure

```text
ppt_llm_correction_workflow/
├── app/                 # CLI entry point
├── agents/              # Reference inspection and LLM-based audit/plan/edit/verify
├── comparison/          # Optional comparison helpers
├── config/              # Environment-backed settings
├── document/            # PPTX inspection and deterministic editing operations
├── llm/                 # LangChain chat-model factory
├── prompts/             # One structured prompt module per LLM call
├── schemas/             # Pydantic output schemas and LangGraph state
├── state/               # Artifacts and audit logging
├── workflow/            # LangGraph orchestration and retry routing
├── tests/
├── artifacts/
├── .env.example
└── requirements.txt
```

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`. Configure `LLM_MODEL` if you want a different model supported by `langchain-openai`.

## Run

```bash
python -m app.main --target path/to/target.pptx --reference path/to/reference.pptx --output-dir artifacts/run_001 --max-iterations 3
```

Outputs are written under the chosen output directory, including the final deck, per-iteration audit/plans/verification JSON, a run summary, and `audit_log.jsonl`.

## LLM calls

1. `DeckAnalyzer`: slide-by-slide audit; returns `AuditResult`.
2. `PlannerAgent`: converts findings to supported operations; returns `EditPlan`.
3. `EditorAgent`: selects exact approved operations; returns `EditExecutionPlan`; Python applies them.
4. `VerifierAgent`: reassesses the edited deck; returns `VerificationResult`.

Every LLM call uses `ChatPromptTemplate` and `with_structured_output(...)` with a Pydantic schema.

## Supported editing operations

The initial editor supports `replace_text`, `set_font_size`, `set_bold`, `set_italic`, `set_font_name`, `set_font_color`, `set_shape_position`, and `set_shape_size`. Position and size use PowerPoint EMU units, not pixels or points.

Unsupported PowerPoint constructs or operations should be reported rather than guessed. Replacing an entire text frame may affect run-level formatting, so review such operations carefully.

## Limitations to address before production

- The inspector extracts text and basic run formatting/geometry; it does not yet fully inspect charts, SmartArt, animation, all paragraph/shape styling, or every PowerPoint feature.
- Slide/shape matching is LLM-guided and can be ambiguous when decks differ substantially.
- A vision-capable model plus rendered slide images is needed for richer visual comparison.
- Add stricter operation-parameter validation and tests before running on important presentations.
- `VERIFIED` means the verifier returned `passed=true`; `UNVERIFIED` means the workflow ended without a verified pass.
