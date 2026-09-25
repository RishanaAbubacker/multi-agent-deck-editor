from pathlib import Path
from schemas.models import Rule, RulesDocument

class RulesAgent:
    name = "rules_agent"

    def run(self, path: Path) -> RulesDocument:
        rules, category = [], "General"
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#"):
                category = line.lstrip("#").strip() or "General"
            elif line.startswith("- "):
                rules.append(Rule(category=category, text=line[2:].strip()))
        return RulesDocument(source=str(path), rules=rules)
