from schemas.models import EditAction, EditPlan

class PlannerAgent:
    name = "planner_agent"

    def run(self, issues):
        actions = []
        for i, issue in enumerate(issues, 1):
            if issue.category == "content_formatting" and issue.slide_number:
                actions.append(EditAction(
                    action_id=f"edit-{i}",
                    action="strip_text_whitespace",
                    slide_number=issue.slide_number,
                    reason=issue.description
                ))
        return EditPlan(actions=actions, assumptions=[])
