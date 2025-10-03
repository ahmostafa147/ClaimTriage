"""Rule engine with safe evaluation and hot reload."""
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from schema import StructuredClaim, RoutingDecision
from storage import load_yaml_rules, save_yaml_rules, sha256_json


class RuleEngine:
    """Safe rule engine for claim routing."""

    def __init__(self, rules_path: str | Path = "rules.yaml"):
        self.rules_path = Path(rules_path)
        self.rules: list[dict[str, Any]] = []
        self.reload_rules()

    def reload_rules(self) -> None:
        """Reload rules from YAML file."""
        if not self.rules_path.exists():
            self.rules = []
            return

        rules_data = load_yaml_rules(self.rules_path)
        self.rules = rules_data.get("rules", [])

    def evaluate(self, claim: StructuredClaim, raw_file_path: str = "") -> RoutingDecision:
        """Evaluate claim against rules and return routing decision."""
        # Build safe evaluation context
        ctx = self._build_context(claim)

        # Try each rule in order
        for rule in self.rules:
            rule_name = rule.get("name", "unknown")
            condition = rule.get("when", "False")
            route = rule.get("route", "human_review")
            rationale = rule.get("rationale", "")

            try:
                if self._safe_eval(condition, ctx):
                    # Rule matched
                    evidence = self._extract_evidence(claim, condition, ctx)
                    decision = RoutingDecision(
                        decision_id=str(uuid.uuid4()),
                        file_id=claim.file_id,
                        route=route,
                        rule_fired=rule_name,
                        rationale=[rationale] if rationale else [],
                        evidence_pointers=evidence,
                        sha256_raw=self._compute_raw_hash(raw_file_path),
                        sha256_structured=sha256_json(claim.model_dump()),
                        created_at=datetime.utcnow().isoformat() + "Z"
                    )
                    return decision
            except Exception as e:
                # Skip failed rule evaluation
                print(f"Rule {rule_name} evaluation failed: {e}")
                continue

        # Default fallback if no rule matches
        return RoutingDecision(
            decision_id=str(uuid.uuid4()),
            file_id=claim.file_id,
            route="human_review",
            rule_fired="fallback",
            rationale=["No matching rule found"],
            evidence_pointers=[],
            sha256_raw=self._compute_raw_hash(raw_file_path),
            sha256_structured=sha256_json(claim.model_dump()),
            created_at=datetime.utcnow().isoformat() + "Z"
        )

    def _build_context(self, claim: StructuredClaim) -> dict[str, Any]:
        """Build safe evaluation context with claim fields and helpers."""
        def any_kw(keywords: list[str]) -> bool:
            """Check if any keyword matches adverse keywords."""
            return any(kw.lower() in [k.lower() for k in claim.adverse_keywords]
                      for kw in keywords)

        def missing(fields: list[str]) -> bool:
            """Check if any field is missing or has low confidence."""
            for field in fields:
                value = getattr(claim, field, None)
                if value is None:
                    return True
                # Check confidence if available
                confidence = claim.confidences.get(field, 1.0)
                if confidence < 0.6:
                    return True
            return False

        # Build context with claim fields
        ctx = {
            "claim_amount_total_usd": claim.claim_amount_total_usd,
            "injury_severity": claim.injury_severity,
            "incident_type": claim.incident_type,
            "repeat_claims_count": claim.repeat_claims_count,
            "claimant_name": claim.claimant_name,
            "policy_id": claim.policy_id,
            "incident_date": claim.incident_date,
            "adverse_keywords": claim.adverse_keywords,
            # Helper functions
            "any_kw": any_kw,
            "missing": missing,
            # Constants
            "True": True,
            "False": False,
            "None": None,
        }

        return ctx

    def _safe_eval(self, expression: str, context: dict[str, Any]) -> bool:
        """Safely evaluate expression with restricted context."""
        try:
            # Create a restricted namespace
            safe_globals = {
                "__builtins__": {
                    "True": True,
                    "False": False,
                    "None": None,
                }
            }

            # Evaluate with restricted globals and provided context
            result = eval(expression, safe_globals, context)
            return bool(result)
        except Exception as e:
            print(f"Evaluation error for '{expression}': {e}")
            return False

    def _extract_evidence(self, claim: StructuredClaim, condition: str,
                         context: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract evidence pointers based on condition."""
        evidence = []

        # Parse condition to find referenced fields
        referenced_fields = []
        for field in ["claim_amount_total_usd", "injury_severity", "incident_type",
                     "repeat_claims_count", "incident_date", "claimant_name", "policy_id"]:
            if field in condition:
                referenced_fields.append(field)

        # Build evidence pointers
        for field in referenced_fields:
            bboxes = claim.bboxes.get(field, [])
            for bbox in bboxes:
                evidence.append({
                    "field": field,
                    "page": bbox.get("page", 0),
                    "bbox_ref": f"page_{bbox.get('page', 0)}_field_{field}"
                })

        # If no bboxes, add field reference anyway
        if not evidence and referenced_fields:
            for field in referenced_fields:
                evidence.append({
                    "field": field,
                    "page": 0,
                    "bbox_ref": f"field_{field}"
                })

        return evidence

    def _compute_raw_hash(self, file_path: str) -> str:
        """Compute hash of raw file."""
        if not file_path or not Path(file_path).exists():
            return ""

        from storage import sha256_file
        return sha256_file(file_path)

    def get_alternative_routes(self, claim: StructuredClaim) -> list[dict[str, Any]]:
        """Get alternative routes that almost matched."""
        ctx = self._build_context(claim)
        alternatives = []

        for rule in self.rules:
            rule_name = rule.get("name", "unknown")
            condition = rule.get("when", "False")
            route = rule.get("route", "human_review")

            try:
                matched = self._safe_eval(condition, ctx)
                if not matched:
                    # Analyze why it didn't match
                    reason = self._analyze_non_match(claim, condition, ctx)
                    alternatives.append({
                        "rule": rule_name,
                        "route": route,
                        "reason": reason
                    })
            except Exception:
                continue

        return alternatives[:3]  # Return top 3

    def _analyze_non_match(self, claim: StructuredClaim, condition: str,
                           context: dict[str, Any]) -> str:
        """Analyze why a condition didn't match."""
        # Simple heuristic analysis
        if "claim_amount_total_usd" in condition and claim.claim_amount_total_usd is not None:
            if ">=" in condition:
                import re
                match = re.search(r">=\s*(\d+)", condition)
                if match:
                    threshold = int(match.group(1))
                    if claim.claim_amount_total_usd < threshold:
                        return f"Amount ${claim.claim_amount_total_usd:.0f} below threshold ${threshold}"

        if "injury_severity" in condition:
            if "severe" in condition and claim.injury_severity != "severe":
                return f"Injury severity is '{claim.injury_severity}', not 'severe'"

        if "repeat_claims_count" in condition:
            import re
            match = re.search(r">=\s*(\d+)", condition)
            if match:
                threshold = int(match.group(1))
                if claim.repeat_claims_count < threshold:
                    return f"Repeat claims count {claim.repeat_claims_count} below threshold {threshold}"

        if "any_kw" in condition:
            return "No adverse keywords matched"

        if "missing" in condition:
            return "All required fields present"

        return "Condition not met"

    def update_rules(self, new_rules_content: str) -> None:
        """Update rules and save to file."""
        save_yaml_rules(new_rules_content, self.rules_path)
        self.reload_rules()
