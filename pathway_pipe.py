"""Pathway-based streaming pipeline for claims processing."""
import os
import time
from pathlib import Path
from typing import Any
from collections import defaultdict
import threading

from schema import StructuredClaim, RoutingDecision
from ade_client import MockExtractor, ADEExtractor
from rule_engine import RuleEngine
from metrics import MetricsTracker, Timer
from storage import sha256_file


class ClaimsPipeline:
    """Simple pipeline for claims processing without Pathway (for mock mode)."""

    def __init__(self, app_mode: str = "MOCK", inbox_dir: str = "demo_data/inbox"):
        self.app_mode = app_mode
        self.inbox_dir = Path(inbox_dir)
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        # Initialize extractor based on mode
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

        # Initialize metrics
        self.metrics = MetricsTracker()

        # Storage
        self.claims: dict[str, StructuredClaim] = {}
        self.decisions: dict[str, RoutingDecision] = {}
        self.processed_files: set[str] = set()

        # Thread safety
        self.lock = threading.Lock()

    def process_file(self, file_path: str | Path) -> tuple[StructuredClaim, RoutingDecision] | None:
        """Process a single file."""
        file_path = Path(file_path)

        if not file_path.exists():
            return None

        # Skip if already processed
        file_hash = sha256_file(file_path)
        if file_hash in self.processed_files:
            return None

        try:
            # Extract
            with Timer() as extraction_timer:
                claim = self.extractor.extract(file_path)

            self.metrics.record_extraction_time(extraction_timer.get_elapsed())

            # Route
            with Timer() as routing_timer:
                decision = self.rule_engine.evaluate(claim, str(file_path))

            self.metrics.record_routing_time(routing_timer.get_elapsed())

            # Store
            with self.lock:
                self.claims[claim.file_id] = claim
                self.decisions[claim.file_id] = decision
                self.processed_files.add(file_hash)
                self.metrics.increment_queue_size(decision.route)

            return claim, decision

        except Exception as e:
            self.metrics.record_error(str(type(e).__name__))
            print(f"Error processing {file_path}: {e}")
            return None

    def process_inbox(self) -> list[tuple[StructuredClaim, RoutingDecision]]:
        """Process all files in inbox."""
        results = []

        if not self.inbox_dir.exists():
            return results

        for file_path in self.inbox_dir.glob("*.pdf"):
            result = self.process_file(file_path)
            if result:
                results.append(result)

        return results

    def get_claims(self) -> list[StructuredClaim]:
        """Get all processed claims."""
        with self.lock:
            return list(self.claims.values())

    def get_decisions(self) -> list[RoutingDecision]:
        """Get all routing decisions."""
        with self.lock:
            return list(self.decisions.values())

    def get_claim_by_id(self, file_id: str) -> StructuredClaim | None:
        """Get claim by file_id."""
        with self.lock:
            return self.claims.get(file_id)

    def get_decision_by_id(self, file_id: str) -> RoutingDecision | None:
        """Get decision by file_id."""
        with self.lock:
            return self.decisions.get(file_id)

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""
        return self.metrics.get_all_metrics()

    def reload_rules(self) -> None:
        """Reload rules from file."""
        self.rule_engine.reload_rules()

    def reprocess_claims(self, claims: list[StructuredClaim]) -> list[RoutingDecision]:
        """Reprocess claims with current rules."""
        decisions = []

        for claim in claims:
            with Timer() as routing_timer:
                decision = self.rule_engine.evaluate(claim)

            self.metrics.record_routing_time(routing_timer.get_elapsed())
            decisions.append(decision)

        return decisions

    def get_recent_claims(self, limit: int = 10) -> list[StructuredClaim]:
        """Get most recent claims."""
        with self.lock:
            claims = sorted(self.claims.values(),
                          key=lambda c: self.decisions.get(c.file_id).created_at
                          if self.decisions.get(c.file_id) else "",
                          reverse=True)
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


# Global pipeline instance
_pipeline_instance: ClaimsPipeline | None = None
_pipeline_lock = threading.Lock()


def get_pipeline(app_mode: str = "MOCK") -> ClaimsPipeline:
    """Get or create global pipeline instance."""
    global _pipeline_instance

    with _pipeline_lock:
        if _pipeline_instance is None:
            _pipeline_instance = ClaimsPipeline(app_mode=app_mode)

        return _pipeline_instance


def reset_pipeline() -> None:
    """Reset global pipeline instance."""
    global _pipeline_instance

    with _pipeline_lock:
        _pipeline_instance = None
