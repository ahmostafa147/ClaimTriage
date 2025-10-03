"""Tests for rule engine."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from rule_engine import RuleEngine
from schema import StructuredClaim


def test_rule_matches():
    """Test rule matching logic."""
    engine = RuleEngine()

    # High amount claim
    claim = StructuredClaim(
        file_id="test1",
        filename="test.pdf",
        claim_amount_total_usd=75000,
        injury_severity="none",
        incident_type="auto"
    )

    decision = engine.evaluate(claim)
    assert decision.route == "litigation"
    assert decision.rule_fired == "litigation_high_amount"


def test_severe_injury_rule():
    """Test severe injury routing."""
    engine = RuleEngine()

    claim = StructuredClaim(
        file_id="test2",
        filename="test.pdf",
        claim_amount_total_usd=5000,
        injury_severity="severe",
        incident_type="auto"
    )

    decision = engine.evaluate(claim)
    assert decision.route == "adjuster_senior"
    assert decision.rule_fired == "severe_injury"


def test_fraud_rule():
    """Test fraud detection routing."""
    engine = RuleEngine()

    claim = StructuredClaim(
        file_id="test3",
        filename="test.pdf",
        claim_amount_total_usd=5000,
        injury_severity="none",
        incident_type="auto",
        repeat_claims_count=3
    )

    decision = engine.evaluate(claim)
    assert decision.route == "fraud_queue"
    assert decision.rule_fired == "suspected_fraud"


def test_fraud_keywords():
    """Test fraud keyword detection."""
    engine = RuleEngine()

    claim = StructuredClaim(
        file_id="test4",
        filename="test.pdf",
        claim_amount_total_usd=5000,
        injury_severity="none",
        incident_type="auto",
        adverse_keywords=["staged", "suspicious"]
    )

    decision = engine.evaluate(claim)
    assert decision.route == "fraud_queue"


def test_missing_fields_rule():
    """Test missing fields routing."""
    engine = RuleEngine()

    claim = StructuredClaim(
        file_id="test5",
        filename="test.pdf",
        claim_amount_total_usd=None,
        injury_severity="none",
        incident_type="auto",
        confidences={}
    )

    decision = engine.evaluate(claim)
    assert decision.route == "human_review"
    assert decision.rule_fired == "low_confidence_handoff"


def test_default_rule():
    """Test default routing."""
    engine = RuleEngine()

    claim = StructuredClaim(
        file_id="test6",
        filename="test.pdf",
        claim_amount_total_usd=3000,
        injury_severity="minor",
        incident_type="auto",
        claimant_name="Test",
        policy_id="POL-001",
        incident_date="2024-01-01"
    )

    decision = engine.evaluate(claim)
    assert decision.route == "adjuster_junior"


def test_rule_precedence():
    """Test that rules fire in correct order."""
    engine = RuleEngine()

    # Claim that matches multiple rules - litigation should win
    claim = StructuredClaim(
        file_id="test7",
        filename="test.pdf",
        claim_amount_total_usd=75000,
        injury_severity="severe",
        incident_type="auto"
    )

    decision = engine.evaluate(claim)
    assert decision.route == "litigation"
    assert decision.rule_fired == "litigation_high_amount"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
