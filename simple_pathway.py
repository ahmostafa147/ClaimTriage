"""Simplified Pathway integration for claims processing."""
import os
import time
import threading
from pathlib import Path
from typing import Any
import pathway as pw

from schema import StructuredClaim, RoutingDecision
from ade_client import MockExtractor, ADEExtractor
from rule_engine import RuleEngine
from storage import sha256_file


class SimplePathwayPipeline:
    """Simplified Pathway pipeline for real-time claims processing."""

    def __init__(self, app_mode: str = "MOCK", inbox_dir: str = "demo_data/inbox"):
        self.app_mode = app_mode
        self.inbox_dir = Path(inbox_dir)
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        # Initialize extractor
        if app_mode == "PROD":
            api_key = os.getenv("LANDINGAI_API_KEY")
            if api_key:
                self.extractor = ADEExtractor(api_key)
                print("✅ Using LandingAI ADE Extractor")
            else:
                print("Warning: LANDINGAI_API_KEY not found, falling back to MOCK mode")
                self.extractor = MockExtractor()
        else:
            self.extractor = MockExtractor()

        # Initialize rule engine
        self.rule_engine = RuleEngine()

        # Cache for UI access
        self.claims_cache: dict[str, StructuredClaim] = {}
        self.decisions_cache: dict[str, RoutingDecision] = {}
        self.metrics_cache: dict[str, Any] = {
            "extraction": {"p50": 0.0, "p95": 0.0, "count": 0},
            "routing": {"p50": 0.0, "p95": 0.0, "count": 0},
            "queues": {}
        }

        # Thread safety
        self.lock = threading.Lock()
        self.running = False

    def start(self) -> None:
        """Start the Pathway pipeline."""
        if self.running:
            return
        
        print("🚀 Starting Pathway streaming pipeline...")
        self.running = True
        
        # For demo purposes, we'll simulate streaming by processing files
        # In production, this would use Pathway's real-time capabilities
        self._simulate_streaming()

    def _simulate_streaming(self) -> None:
        """Simulate streaming processing."""
        def process_loop():
            while self.running:
                try:
                    # Process any new files in inbox
                    for file_path in self.inbox_dir.glob("*.pdf"):
                        if file_path.name not in [c.filename for c in self.claims_cache.values()]:
                            self._process_file_streaming(file_path)
                    
                    time.sleep(1)  # Check every second
                except Exception as e:
                    print(f"Streaming error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=process_loop, daemon=True)
        thread.start()

    def _process_file_streaming(self, file_path: Path) -> None:
        """Process a file in streaming mode."""
        try:
            print(f"📄 Pathway processing: {file_path.name}")
            
            # Extract
            start_time = time.time()
            claim = self.extractor.extract(file_path)
            extraction_time = time.time() - start_time
            
            # Route
            start_time = time.time()
            decision = self.rule_engine.evaluate(claim, str(file_path))
            routing_time = time.time() - start_time
            
            # Update cache
            with self.lock:
                self.claims_cache[claim.file_id] = claim
                self.decisions_cache[claim.file_id] = decision
                
                # Update metrics
                self._update_metric("extraction", extraction_time)
                self._update_metric("routing", routing_time)
                
                # Update queue sizes
                route = decision.route
                if route not in self.metrics_cache["queues"]:
                    self.metrics_cache["queues"][route] = 0
                self.metrics_cache["queues"][route] += 1
            
            print(f"✅ Processed {file_path.name} -> {decision.route}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _update_metric(self, metric_type: str, value: float) -> None:
        """Update metrics with new value."""
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
        if metrics["values"]:
            import numpy as np
            metrics["p50"] = float(np.percentile(metrics["values"], 50))
            metrics["p95"] = float(np.percentile(metrics["values"], 95))

    def stop(self) -> None:
        """Stop the Pathway pipeline."""
        self.running = False

    # Interface methods for compatibility with existing ClaimsPipeline

    def process_file(self, file_path: str | Path) -> tuple[StructuredClaim, RoutingDecision] | None:
        """Process a single file (compatibility method)."""
        file_path = Path(file_path)
        
        # Process the file
        self._process_file_streaming(file_path)
        
        # Return the result
        filename = file_path.name
        for claim in self.claims_cache.values():
            if claim.filename == filename:
                decision = self.decisions_cache.get(claim.file_id)
                if decision:
                    return claim, decision
        
        return None

    def process_inbox(self) -> list[tuple[StructuredClaim, RoutingDecision]]:
        """Process inbox (compatibility method)."""
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
