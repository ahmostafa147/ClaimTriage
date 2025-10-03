"""Counterfactual analysis for rule changes."""
from typing import Any
from pathlib import Path

from schema import StructuredClaim, RoutingDecision
from rule_engine import RuleEngine


class CounterfactualAnalyzer:
    """Analyze routing changes when rules are modified."""

    def __init__(self):
        self.original_engine: RuleEngine | None = None
        self.new_engine: RuleEngine | None = None

    def analyze(self, claims: list[StructuredClaim], new_rules_content: str,
                original_rules_path: str | Path = "rules.yaml") -> dict[str, Any]:
        """Analyze routing changes with new rules."""
        # Create engines
        self.original_engine = RuleEngine(original_rules_path)

        # Create temp file for new rules
        temp_rules_path = Path("temp_rules.yaml")
        with open(temp_rules_path, "w") as f:
            f.write(new_rules_content)

        try:
            self.new_engine = RuleEngine(temp_rules_path)

            # Compute routing with both rule sets
            results = []
            for claim in claims:
                original_decision = self.original_engine.evaluate(claim)
                new_decision = self.new_engine.evaluate(claim)

                if original_decision.route != new_decision.route:
                    results.append({
                        "file_id": claim.file_id,
                        "filename": claim.filename,
                        "from_route": original_decision.route,
                        "to_route": new_decision.route,
                        "from_rule": original_decision.rule_fired,
                        "new_rule": new_decision.rule_fired,
                        "rationale": new_decision.rationale[0] if new_decision.rationale else ""
                    })

            # Compute summary statistics
            route_changes = self._compute_route_changes(claims)

            return {
                "changes": results,
                "summary": route_changes,
                "total_claims": len(claims),
                "changed_count": len(results)
            }

        finally:
            # Cleanup temp file
            if temp_rules_path.exists():
                temp_rules_path.unlink()

    def _compute_route_changes(self, claims: list[StructuredClaim]) -> dict[str, Any]:
        """Compute before/after route distribution."""
        if not self.original_engine or not self.new_engine:
            return {}

        original_routes = {}
        new_routes = {}

        for claim in claims:
            orig_decision = self.original_engine.evaluate(claim)
            new_decision = self.new_engine.evaluate(claim)

            original_routes[orig_decision.route] = original_routes.get(orig_decision.route, 0) + 1
            new_routes[new_decision.route] = new_routes.get(new_decision.route, 0) + 1

        return {
            "before": original_routes,
            "after": new_routes
        }

    def get_moved_counts(self, claims: list[StructuredClaim], new_rules_content: str) -> dict[str, int]:
        """Get count of claims moved between routes."""
        result = self.analyze(claims, new_rules_content)
        changes = result["changes"]

        moved = {}
        for change in changes:
            key = f"{change['from_route']} → {change['to_route']}"
            moved[key] = moved.get(key, 0) + 1

        return moved


def compare_decisions(before: list[RoutingDecision], after: list[RoutingDecision]) -> dict[str, Any]:
    """Compare two sets of routing decisions."""
    changes = []

    # Create lookup by file_id
    after_map = {d.file_id: d for d in after}

    for before_dec in before:
        after_dec = after_map.get(before_dec.file_id)
        if not after_dec:
            continue

        if before_dec.route != after_dec.route:
            changes.append({
                "file_id": before_dec.file_id,
                "from_route": before_dec.route,
                "to_route": after_dec.route,
                "from_rule": before_dec.rule_fired,
                "to_rule": after_dec.rule_fired
            })

    return {
        "changes": changes,
        "change_count": len(changes),
        "total": len(before)
    }
