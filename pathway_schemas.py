"""Pathway schema definitions for claims triage streaming pipeline."""
import pathway as pw
from typing import Any


class ClaimInputSchema(pw.Schema):
    """Schema for incoming claim files from filesystem."""
    filepath: str = pw.column_definition(description="Path to the PDF file")
    data: bytes = pw.column_definition(description="Raw file content")
    modified_at: pw.DateTimeUtc = pw.column_definition(description="File modification timestamp")


class StructuredClaimSchema(pw.Schema):
    """Schema for structured claims extracted from documents."""
    file_id: str = pw.column_definition(primary_key=True, description="Unique file identifier")
    filename: str
    claimant_name: str | None = pw.column_definition(default_value=None)
    policy_id: str | None = pw.column_definition(default_value=None)
    incident_date: str | None = pw.column_definition(default_value=None)
    claim_amount_total_usd: float | None = pw.column_definition(default_value=None)
    injury_severity: str = pw.column_definition(default_value="none")
    incident_type: str = pw.column_definition(default_value="auto")
    repeat_claims_count: int = pw.column_definition(default_value=0)
    adverse_keywords: pw.Json = pw.column_definition(
        default_value=pw.Json([]),
        description="List of adverse keywords found"
    )
    extracted_tables: pw.Json = pw.column_definition(
        default_value=pw.Json([]),
        description="Extracted table data"
    )
    bboxes: pw.Json = pw.column_definition(
        default_value=pw.Json({}),
        description="Bounding box coordinates for fields"
    )
    confidences: pw.Json = pw.column_definition(
        default_value=pw.Json({}),
        description="Confidence scores for extracted fields"
    )
    extraction_time_ms: float = pw.column_definition(
        default_value=0.0,
        description="Time taken for extraction in milliseconds"
    )
    raw_file_hash: str = pw.column_definition(
        default_value="",
        description="SHA256 hash of raw file"
    )


class RoutingDecisionSchema(pw.Schema):
    """Schema for routing decisions."""
    decision_id: str = pw.column_definition(primary_key=True, description="Unique decision identifier")
    file_id: str = pw.column_definition(description="Reference to claim file_id")
    route: str = pw.column_definition(description="Assigned route")
    rule_fired: str = pw.column_definition(description="Name of the rule that matched")
    model_score: float | None = pw.column_definition(default_value=None)
    rationale: pw.Json = pw.column_definition(
        default_value=pw.Json([]),
        description="List of rationale strings"
    )
    evidence_pointers: pw.Json = pw.column_definition(
        default_value=pw.Json([]),
        description="Evidence pointers for decision"
    )
    sha256_raw: str = pw.column_definition(default_value="")
    sha256_structured: str = pw.column_definition(default_value="")
    created_at: str = pw.column_definition(description="ISO timestamp")
    routing_time_ms: float = pw.column_definition(
        default_value=0.0,
        description="Time taken for routing in milliseconds"
    )


class MetricsSchema(pw.Schema):
    """Schema for aggregated metrics."""
    metric_name: str = pw.column_definition(primary_key=True, description="Name of the metric")
    metric_value: float = pw.column_definition(description="Metric value")
    window_start: pw.DateTimeUtc = pw.column_definition(description="Start of time window")
    window_end: pw.DateTimeUtc = pw.column_definition(description="End of time window")
    count: int = pw.column_definition(default_value=0, description="Number of samples")


class QueueSizeSchema(pw.Schema):
    """Schema for queue size tracking."""
    route: str = pw.column_definition(primary_key=True, description="Route name")
    size: int = pw.column_definition(description="Number of claims in queue")
    updated_at: pw.DateTimeUtc = pw.column_definition(description="Last update timestamp")
