"""Pydantic schemas for claims triage system."""
from typing import Any
from pydantic import BaseModel, Field, field_validator


class StructuredClaim(BaseModel):
    """Structured claim extracted from document."""
    file_id: str
    filename: str
    claimant_name: str | None = None
    policy_id: str | None = None
    incident_date: str | None = None  # ISO yyyy-mm-dd
    claim_amount_total_usd: float | None = None
    injury_severity: str = "none"  # none, minor, severe
    incident_type: str = "auto"  # auto, property, liability, theft
    repeat_claims_count: int = 0
    adverse_keywords: list[str] = Field(default_factory=list)
    extracted_tables: list[dict[str, Any]] = Field(default_factory=list)
    bboxes: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    confidences: dict[str, float] = Field(default_factory=dict)

    @field_validator("injury_severity")
    @classmethod
    def validate_injury_severity(cls, v: str) -> str:
        if v not in {"none", "minor", "severe"}:
            return "none"
        return v

    @field_validator("incident_type")
    @classmethod
    def validate_incident_type(cls, v: str) -> str:
        if v not in {"auto", "property", "liability", "theft"}:
            return "auto"
        return v

    @field_validator("confidences")
    @classmethod
    def validate_confidences(cls, v: dict[str, float]) -> dict[str, float]:
        return {k: max(0.0, min(1.0, val)) for k, val in v.items()}


class RoutingDecision(BaseModel):
    """Routing decision for a claim."""
    decision_id: str
    file_id: str
    route: str  # adjuster_junior, adjuster_senior, fraud_queue, litigation, human_review
    rule_fired: str
    model_score: float | None = None
    rationale: list[str] = Field(default_factory=list)
    evidence_pointers: list[dict[str, Any]] = Field(default_factory=list)
    sha256_raw: str = ""
    sha256_structured: str = ""
    created_at: str = ""

    @field_validator("route")
    @classmethod
    def validate_route(cls, v: str) -> str:
        valid_routes = {"adjuster_junior", "adjuster_senior", "fraud_queue", "litigation", "human_review"}
        if v not in valid_routes:
            return "human_review"
        return v


def empty_claim(file_id: str, filename: str) -> StructuredClaim:
    """Create an empty claim with defaults."""
    return StructuredClaim(file_id=file_id, filename=filename)
