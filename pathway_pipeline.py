"""Pathway-based streaming pipeline for real-time claims processing."""
import os
import uuid
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any
import pathway as pw

from pathway_schemas import (
    StructuredClaimSchema,
    RoutingDecisionSchema,
    MetricsSchema,
    QueueSizeSchema
)
from schema import StructuredClaim, RoutingDecision
from ade_client import MockExtractor, ADEExtractor
from rule_engine import RuleEngine
from storage import sha256_file, sha256_json


class PathwayClaimsPipeline:
    """Real-time streaming pipeline using Pathway."""

    def __init__(self, app_mode: str = "MOCK", inbox_dir: str = "demo_data/inbox"):
        self.app_mode = app_mode
        self.inbox_dir = Path(inbox_dir)
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        # Initialize extractor
        if app_mode == "PROD":
            api_key = os.getenv("LANDINGAI_API_KEY")
            if api_key:
                self.extractor = ADEExtractor(api_key)
            else:
                print("Warning: LANDINGAI_API_KEY not found, falling back to MOCK mode")
                self.extractor = MockExtractor()
        else:
            self.extractor = MockExtractor()

        # Initialize rule engine
        self.rule_engine = RuleEngine()

        # Pathway tables (will be initialized in build_pipeline)
        self.claims_table: pw.Table | None = None
        self.decisions_table: pw.Table | None = None
        self.metrics_table: pw.Table | None = None
        self.queue_sizes_table: pw.Table | None = None

        # Running state
        self.pipeline_thread: threading.Thread | None = None
        self.pipeline_running = False
        self.lock = threading.Lock()

        # Cache for UI access (updated from Pathway outputs)
        self.claims_cache: dict[str, StructuredClaim] = {}
        self.decisions_cache: dict[str, RoutingDecision] = {}
        self.metrics_cache: dict[str, Any] = {
            "extraction": {"p50": 0.0, "p95": 0.0, "count": 0},
            "routing": {"p50": 0.0, "p95": 0.0, "count": 0},
            "queues": {}
        }

    def build_pipeline(self) -> None:
        """Build the Pathway streaming pipeline."""

        # 1. Read files from inbox directory
        files_table = pw.io.fs.read(
            path=str(self.inbox_dir),
            format="binary",
            mode="streaming",
            with_metadata=True
        )

        # Add filepath column
        files_table = files_table.with_columns(
            filepath=pw.this.path
        )

        # 2. Extract structured claims using UDF
        @pw.udf
        def extract_claim(filepath: str, data: bytes) -> dict:
            """Extract structured claim from PDF file."""
            try:
                start_time = time.time()

                # Use extractor to process file
                claim = self.extractor.extract(Path(filepath))

                extraction_time_ms = (time.time() - start_time) * 1000

                # Compute file hash
                raw_hash = sha256_file(filepath) if Path(filepath).exists() else ""

                # Convert to dict for Pathway
                return {
                    "file_id": claim.file_id,
                    "filename": claim.filename,
                    "claimant_name": claim.claimant_name,
                    "policy_id": claim.policy_id,
                    "incident_date": claim.incident_date,
                    "claim_amount_total_usd": claim.claim_amount_total_usd,
                    "injury_severity": claim.injury_severity,
                    "incident_type": claim.incident_type,
                    "repeat_claims_count": claim.repeat_claims_count,
                    "adverse_keywords": pw.Json(claim.adverse_keywords),
                    "extracted_tables": pw.Json(claim.extracted_tables),
                    "bboxes": pw.Json(claim.bboxes),
                    "confidences": pw.Json(claim.confidences),
                    "extraction_time_ms": extraction_time_ms,
                    "raw_file_hash": raw_hash
                }
            except Exception as e:
                print(f"Error extracting {filepath}: {e}")
                # Return empty claim on error
                return {
                    "file_id": str(uuid.uuid4()),
                    "filename": Path(filepath).name,
                    "claimant_name": None,
                    "policy_id": None,
                    "incident_date": None,
                    "claim_amount_total_usd": None,
                    "injury_severity": "none",
                    "incident_type": "auto",
                    "repeat_claims_count": 0,
                    "adverse_keywords": pw.Json([]),
                    "extracted_tables": pw.Json([]),
                    "bboxes": pw.Json({}),
                    "confidences": pw.Json({}),
                    "extraction_time_ms": 0.0,
                    "raw_file_hash": ""
                }

        # Apply extraction
        claims_raw = files_table.select(
            claim_data=extract_claim(pw.this.filepath, pw.this.data)
        )

        # Flatten the claim data into columns
        self.claims_table = claims_raw.select(
            file_id=pw.this.claim_data["file_id"],
            filename=pw.this.claim_data["filename"],
            claimant_name=pw.this.claim_data["claimant_name"],
            policy_id=pw.this.claim_data["policy_id"],
            incident_date=pw.this.claim_data["incident_date"],
            claim_amount_total_usd=pw.this.claim_data["claim_amount_total_usd"],
            injury_severity=pw.this.claim_data["injury_severity"],
            incident_type=pw.this.claim_data["incident_type"],
            repeat_claims_count=pw.this.claim_data["repeat_claims_count"],
            adverse_keywords=pw.this.claim_data["adverse_keywords"],
            extracted_tables=pw.this.claim_data["extracted_tables"],
            bboxes=pw.this.claim_data["bboxes"],
            confidences=pw.this.claim_data["confidences"],
            extraction_time_ms=pw.this.claim_data["extraction_time_ms"],
            raw_file_hash=pw.this.claim_data["raw_file_hash"]
        ).with_id_from(pw.this.file_id)

        # 3. Route claims using rule engine
        @pw.udf
        def route_claim(
            file_id: str,
            filename: str,
            claimant_name: str | None,
            policy_id: str | None,
            incident_date: str | None,
            claim_amount_total_usd: float | None,
            injury_severity: str,
            incident_type: str,
            repeat_claims_count: int,
            adverse_keywords: pw.Json,
            extracted_tables: pw.Json,
            bboxes: pw.Json,
            confidences: pw.Json,
            raw_file_hash: str
        ) -> dict:
            """Route claim using rule engine."""
            try:
                start_time = time.time()

                # Reconstruct StructuredClaim from Pathway columns
                claim = StructuredClaim(
                    file_id=file_id,
                    filename=filename,
                    claimant_name=claimant_name,
                    policy_id=policy_id,
                    incident_date=incident_date,
                    claim_amount_total_usd=claim_amount_total_usd,
                    injury_severity=injury_severity,
                    incident_type=incident_type,
                    repeat_claims_count=repeat_claims_count,
                    adverse_keywords=adverse_keywords.as_list() if adverse_keywords else [],
                    extracted_tables=extracted_tables.as_list() if extracted_tables else [],
                    bboxes=bboxes.as_dict() if bboxes else {},
                    confidences=confidences.as_dict() if confidences else {}
                )

                # Evaluate routing decision
                decision = self.rule_engine.evaluate(claim, "")
                decision.sha256_raw = raw_file_hash

                routing_time_ms = (time.time() - start_time) * 1000

                # Convert to dict for Pathway
                return {
                    "decision_id": decision.decision_id,
                    "file_id": decision.file_id,
                    "route": decision.route,
                    "rule_fired": decision.rule_fired,
                    "model_score": decision.model_score,
                    "rationale": pw.Json(decision.rationale),
                    "evidence_pointers": pw.Json(decision.evidence_pointers),
                    "sha256_raw": decision.sha256_raw,
                    "sha256_structured": decision.sha256_structured,
                    "created_at": decision.created_at,
                    "routing_time_ms": routing_time_ms
                }
            except Exception as e:
                print(f"Error routing claim {file_id}: {e}")
                # Return default decision on error
                return {
                    "decision_id": str(uuid.uuid4()),
                    "file_id": file_id,
                    "route": "human_review",
                    "rule_fired": "error",
                    "model_score": None,
                    "rationale": pw.Json([f"Error: {str(e)}"]),
                    "evidence_pointers": pw.Json([]),
                    "sha256_raw": raw_file_hash,
                    "sha256_structured": "",
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "routing_time_ms": 0.0
                }

        # Apply routing
        decisions_raw = self.claims_table.select(
            decision_data=route_claim(
                pw.this.file_id,
                pw.this.filename,
                pw.this.claimant_name,
                pw.this.policy_id,
                pw.this.incident_date,
                pw.this.claim_amount_total_usd,
                pw.this.injury_severity,
                pw.this.incident_type,
                pw.this.repeat_claims_count,
                pw.this.adverse_keywords,
                pw.this.extracted_tables,
                pw.this.bboxes,
                pw.this.confidences,
                pw.this.raw_file_hash
            )
        )

        # Flatten decision data
        self.decisions_table = decisions_raw.select(
            decision_id=pw.this.decision_data["decision_id"],
            file_id=pw.this.decision_data["file_id"],
            route=pw.this.decision_data["route"],
            rule_fired=pw.this.decision_data["rule_fired"],
            model_score=pw.this.decision_data["model_score"],
            rationale=pw.this.decision_data["rationale"],
            evidence_pointers=pw.this.decision_data["evidence_pointers"],
            sha256_raw=pw.this.decision_data["sha256_raw"],
            sha256_structured=pw.this.decision_data["sha256_structured"],
            created_at=pw.this.decision_data["created_at"],
            routing_time_ms=pw.this.decision_data["routing_time_ms"]
        ).with_id_from(pw.this.decision_id)

        # 4. Compute queue sizes using groupby
        self.queue_sizes_table = self.decisions_table.groupby(pw.this.route).reduce(
            route=pw.this.route,
            size=pw.reducers.count()
        )

        # 5. Setup output connectors to update cache
        # We'll use pw.io.subscribe to update our cache
        pw.io.subscribe(
            self.claims_table,
            on_change=self._update_claims_cache,
            on_end=lambda: None
        )

        pw.io.subscribe(
            self.decisions_table,
            on_change=self._update_decisions_cache,
            on_end=lambda: None
        )

        pw.io.subscribe(
            self.queue_sizes_table,
            on_change=self._update_queue_sizes_cache,
            on_end=lambda: None
        )

    def _update_claims_cache(self, key: Any, row: dict, time: int, diff: int) -> None:
        """Update claims cache when Pathway emits changes."""
        with self.lock:
            if diff > 0:  # Addition
                # Convert from Pathway row to StructuredClaim
                claim = StructuredClaim(
                    file_id=row["file_id"],
                    filename=row["filename"],
                    claimant_name=row.get("claimant_name"),
                    policy_id=row.get("policy_id"),
                    incident_date=row.get("incident_date"),
                    claim_amount_total_usd=row.get("claim_amount_total_usd"),
                    injury_severity=row.get("injury_severity", "none"),
                    incident_type=row.get("incident_type", "auto"),
                    repeat_claims_count=row.get("repeat_claims_count", 0),
                    adverse_keywords=row.get("adverse_keywords", []),
                    extracted_tables=row.get("extracted_tables", []),
                    bboxes=row.get("bboxes", {}),
                    confidences=row.get("confidences", {})
                )
                self.claims_cache[claim.file_id] = claim

                # Update extraction metrics
                extraction_time_ms = row.get("extraction_time_ms", 0.0)
                self._update_metric("extraction", extraction_time_ms / 1000.0)

            elif diff < 0:  # Deletion
                file_id = row["file_id"]
                if file_id in self.claims_cache:
                    del self.claims_cache[file_id]

    def _update_decisions_cache(self, key: Any, row: dict, time: int, diff: int) -> None:
        """Update decisions cache when Pathway emits changes."""
        with self.lock:
            if diff > 0:  # Addition
                # Convert from Pathway row to RoutingDecision
                decision = RoutingDecision(
                    decision_id=row["decision_id"],
                    file_id=row["file_id"],
                    route=row["route"],
                    rule_fired=row["rule_fired"],
                    model_score=row.get("model_score"),
                    rationale=row.get("rationale", []),
                    evidence_pointers=row.get("evidence_pointers", []),
                    sha256_raw=row.get("sha256_raw", ""),
                    sha256_structured=row.get("sha256_structured", ""),
                    created_at=row.get("created_at", "")
                )
                self.decisions_cache[decision.file_id] = decision

                # Update routing metrics
                routing_time_ms = row.get("routing_time_ms", 0.0)
                self._update_metric("routing", routing_time_ms / 1000.0)

            elif diff < 0:  # Deletion
                file_id = row["file_id"]
                if file_id in self.decisions_cache:
                    del self.decisions_cache[file_id]

    def _update_queue_sizes_cache(self, key: Any, row: dict, time: int, diff: int) -> None:
        """Update queue sizes cache when Pathway emits changes."""
        with self.lock:
            route = row["route"]
            size = row["size"]
            self.metrics_cache["queues"][route] = size

    def _update_metric(self, metric_type: str, value: float) -> None:
        """Update metrics with new value (simplified for demo)."""
        if metric_type not in self.metrics_cache:
            self.metrics_cache[metric_type] = {"p50": 0.0, "p95": 0.0, "count": 0, "values": []}

        metrics = self.metrics_cache[metric_type]
        if "values" not in metrics:
            metrics["values"] = []

        metrics["values"].append(value)
        metrics["count"] = len(metrics["values"])

        # Keep only last 100 values for percentile calculation
        if len(metrics["values"]) > 100:
            metrics["values"] = metrics["values"][-100:]

        # Calculate percentiles
        import numpy as np
        if metrics["values"]:
            metrics["p50"] = float(np.percentile(metrics["values"], 50))
            metrics["p95"] = float(np.percentile(metrics["values"], 95))

    def start(self) -> None:
        """Start the Pathway pipeline in a background thread."""
        if self.pipeline_running:
            return

        self.build_pipeline()

        def run_pipeline():
            self.pipeline_running = True
            try:
                pw.run(
                    monitoring_level=pw.MonitoringLevel.NONE,
                    with_http_server=False
                )
            except Exception as e:
                print(f"Pipeline error: {e}")
            finally:
                self.pipeline_running = False

        self.pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
        self.pipeline_thread.start()

    def stop(self) -> None:
        """Stop the Pathway pipeline."""
        # Pathway doesn't have a clean stop mechanism
        # In production, you'd use signals or other mechanisms
        self.pipeline_running = False

    # Interface methods for compatibility with existing ClaimsPipeline

    def process_file(self, file_path: str | Path) -> tuple[StructuredClaim, RoutingDecision] | None:
        """Process a single file (compatibility method)."""
        # In streaming mode, files are processed automatically
        # This is a no-op - the file watcher will pick it up
        file_path = Path(file_path)
        if file_path.exists() and file_path.suffix == ".pdf":
            # Copy to inbox if not already there
            dest = self.inbox_dir / file_path.name
            if not dest.exists():
                import shutil
                shutil.copy(file_path, dest)

        # Wait a bit for processing (simplified)
        time.sleep(0.5)

        # Try to find the processed claim
        filename = Path(file_path).name
        for claim in self.claims_cache.values():
            if claim.filename == filename:
                decision = self.decisions_cache.get(claim.file_id)
                if decision:
                    return claim, decision

        return None

    def process_inbox(self) -> list[tuple[StructuredClaim, RoutingDecision]]:
        """Process inbox (compatibility method)."""
        # In streaming mode, this happens automatically
        # Just return what we have
        results = []
        with self.lock:
            for claim in self.claims_cache.values():
                decision = self.decisions_cache.get(claim.file_id)
                if decision:
                    results.append((claim, decision))
        return results

    def get_claims(self) -> list[StructuredClaim]:
        """Get all processed claims."""
        with self.lock:
            return list(self.claims_cache.values())

    def get_decisions(self) -> list[RoutingDecision]:
        """Get all routing decisions."""
        with self.lock:
            return list(self.decisions_cache.values())

    def get_claim_by_id(self, file_id: str) -> StructuredClaim | None:
        """Get claim by file_id."""
        with self.lock:
            return self.claims_cache.get(file_id)

    def get_decision_by_id(self, file_id: str) -> RoutingDecision | None:
        """Get decision by file_id."""
        with self.lock:
            return self.decisions_cache.get(file_id)

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""
        with self.lock:
            return {
                "extraction": {
                    "p50": self.metrics_cache.get("extraction", {}).get("p50", 0.0),
                    "p95": self.metrics_cache.get("extraction", {}).get("p95", 0.0),
                    "count": self.metrics_cache.get("extraction", {}).get("count", 0)
                },
                "routing": {
                    "p50": self.metrics_cache.get("routing", {}).get("p50", 0.0),
                    "p95": self.metrics_cache.get("routing", {}).get("p95", 0.0),
                    "count": self.metrics_cache.get("routing", {}).get("count", 0)
                },
                "queues": self.metrics_cache.get("queues", {})
            }

    def reload_rules(self) -> None:
        """Reload rules from file."""
        self.rule_engine.reload_rules()

    def get_recent_claims(self, limit: int = 10) -> list[StructuredClaim]:
        """Get most recent claims."""
        with self.lock:
            claims = sorted(
                self.claims_cache.values(),
                key=lambda c: self.decisions_cache.get(c.file_id).created_at
                if self.decisions_cache.get(c.file_id) else "",
                reverse=True
            )
            return claims[:limit]

    def initialize_mock_data(self) -> None:
        """Initialize with mock data if in MOCK mode."""
        if self.app_mode != "MOCK":
            return

        if isinstance(self.extractor, MockExtractor):
            # Generate synthetic PDFs
            generated_files = self.extractor.generate_synthetic_claims()

            # Copy some to inbox for processing
            for i, src_file in enumerate(generated_files[:6]):
                dest_file = self.inbox_dir / src_file.name
                if not dest_file.exists():
                    import shutil
                    shutil.copy(src_file, dest_file)
