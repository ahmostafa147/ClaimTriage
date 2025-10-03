"""Tests for counterfactual analysis."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from counterfactual import CounterfactualAnalyzer
from schema import StructuredClaim


def test_counterfactual_analysis():
    """Test counterfactual analysis with modified rules."""
    analyzer = CounterfactualAnalyzer()

    # Create test claims
    claims = [
        StructuredClaim(
            file_id="cf1",
            filename="test1.pdf",
            claim_amount_total_usd=45000,
            injury_severity="none",
            incident_type="auto"
        ),
        StructuredClaim(
            file_id="cf2",
            filename="test2.pdf",
            claim_amount_total_usd=30000,
            injury_severity="none",
            incident_type="auto"
        ),
    ]

    # New rules with lower threshold
    new_rules = """version: 1
rules:
  - name: litigation_high_amount
    when: "claim_amount_total_usd is not None and claim_amount_total_usd >= 25000"
    route: "litigation"
    rationale: "High amount >= 25k triggers litigation review"
  - name: default
    when: "True"
    route: "adjuster_junior"
    rationale: "No risk signals"
"""

    result = analyzer.analyze(claims, new_rules)

    # Both claims should move to litigation with new threshold
    assert result["changed_count"] >= 1
    assert len(result["changes"]) >= 1


def test_no_changes():
    """Test when rules don't change routing for simple claim."""
    analyzer = CounterfactualAnalyzer()

    # Simple claim that will always route to default
    claims = [
        StructuredClaim(
            file_id="cf3",
            filename="test3.pdf",
            claim_amount_total_usd=1000,
            injury_severity="none",
            incident_type="auto",
            claimant_name="Test",
            policy_id="POL-001",
            incident_date="2024-01-01"
        ),
    ]

    # Same rules from rules.yaml - small claim always goes to junior
    same_rules = """version: 1
rules:
  - name: litigation_high_amount
    when: "claim_amount_total_usd is not None and claim_amount_total_usd >= 50000"
    route: "litigation"
    rationale: "High amount >= 50k triggers litigation review"
  - name: severe_injury
    when: "injury_severity == 'severe'"
    route: "adjuster_senior"
    rationale: "Severe injury requires senior adjuster"
  - name: suspected_fraud
    when: "repeat_claims_count >= 2 or any_kw(['staged', 'prior loss', 'inconsistent story', 'suspicious'])"
    route: "fraud_queue"
    rationale: "Repeat claims or fraud keywords detected"
  - name: low_confidence_handoff
    when: "missing(['claim_amount_total_usd', 'incident_date'])"
    route: "human_review"
    rationale: "Key fields missing or low confidence"
  - name: high_amount_senior
    when: "claim_amount_total_usd is not None and claim_amount_total_usd >= 10000"
    route: "adjuster_senior"
    rationale: "High amount requires senior review"
  - name: default
    when: "True"
    route: "adjuster_junior"
    rationale: "No risk signals, standard processing"
"""

    result = analyzer.analyze(claims, same_rules)

    # Should be no changes since rules are the same
    assert result["changed_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
