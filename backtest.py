"""Backtesting module for evaluating rule performance."""
import json
from pathlib import Path
from typing import Any
from collections import defaultdict

from schema import StructuredClaim, RoutingDecision
from rule_engine import RuleEngine


class Backtester:
    """Backtest rule engine against gold labeled data."""

    def __init__(self, gold_dir: str | Path = "demo_data/gold"):
        self.gold_dir = Path(gold_dir)
        self.gold_dir.mkdir(parents=True, exist_ok=True)

    def load_gold_labels(self) -> list[dict[str, Any]]:
        """Load gold labeled claims."""
        gold_file = self.gold_dir / "gold_labels.jsonl"

        if not gold_file.exists():
            # Create sample gold labels
            self._create_sample_gold_labels()

        labels = []
        with open(gold_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    labels.append(json.loads(line))

        return labels

    def _create_sample_gold_labels(self) -> None:
        """Create sample gold labels for testing."""
        gold_file = self.gold_dir / "gold_labels.jsonl"

        sample_labels = [
            {
                "filename": "claim_auto_001.pdf",
                "expected_route": "adjuster_junior",
                "claim_amount": 3200,
                "injury_severity": "minor"
            },
            {
                "filename": "claim_auto_002.pdf",
                "expected_route": "adjuster_junior",
                "claim_amount": 4800,
                "injury_severity": "none"
            },
            {
                "filename": "claim_severe_001.pdf",
                "expected_route": "litigation",
                "claim_amount": 75000,
                "injury_severity": "severe"
            },
            {
                "filename": "claim_severe_002.pdf",
                "expected_route": "litigation",
                "claim_amount": 92500,
                "injury_severity": "severe"
            },
            {
                "filename": "claim_fraud_001.pdf",
                "expected_route": "fraud_queue",
                "claim_amount": 8500,
                "repeat_claims": 3
            },
            {
                "filename": "claim_fraud_002.pdf",
                "expected_route": "fraud_queue",
                "claim_amount": 12000,
                "repeat_claims": 2
            },
        ]

        with open(gold_file, "w") as f:
            for label in sample_labels:
                f.write(json.dumps(label) + "\n")

    def run_backtest(self, claims: list[StructuredClaim], decisions: list[RoutingDecision]) -> dict[str, Any]:
        """Run backtest against gold labels."""
        gold_labels = self.load_gold_labels()

        # Create lookup maps
        gold_map = {label["filename"]: label for label in gold_labels}
        decision_map = {d.file_id: d for d in decisions}
        claim_map = {c.file_id: c for c in claims}

        # Match predictions with gold labels
        matches = []
        mismatches = []

        for claim in claims:
            if claim.filename not in gold_map:
                continue

            gold = gold_map[claim.filename]
            decision = decision_map.get(claim.file_id)

            if not decision:
                continue

            expected_route = gold["expected_route"]
            actual_route = decision.route

            match_record = {
                "filename": claim.filename,
                "file_id": claim.file_id,
                "expected": expected_route,
                "actual": actual_route,
                "matched": expected_route == actual_route,
                "rule_fired": decision.rule_fired
            }

            if expected_route == actual_route:
                matches.append(match_record)
            else:
                mismatches.append(match_record)

        # Compute metrics
        metrics = self._compute_metrics(matches, mismatches)

        return {
            "metrics": metrics,
            "matches": matches,
            "mismatches": mismatches,
            "confusion_matrix": self._build_confusion_matrix(matches + mismatches)
        }

    def _compute_metrics(self, matches: list[dict], mismatches: list[dict]) -> dict[str, Any]:
        """Compute precision, recall, and F1 per route."""
        all_records = matches + mismatches

        # Get unique routes
        routes = set()
        for record in all_records:
            routes.add(record["expected"])
            routes.add(record["actual"])

        # Compute per-route metrics
        route_metrics = {}
        for route in routes:
            tp = sum(1 for r in all_records if r["expected"] == route and r["actual"] == route)
            fp = sum(1 for r in all_records if r["expected"] != route and r["actual"] == route)
            fn = sum(1 for r in all_records if r["expected"] == route and r["actual"] != route)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            route_metrics[route] = {
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1": round(f1, 3),
                "support": tp + fn
            }

        # Overall accuracy
        total = len(all_records)
        accuracy = len(matches) / total if total > 0 else 0.0

        return {
            "overall_accuracy": round(accuracy, 3),
            "by_route": route_metrics,
            "total_predictions": total,
            "correct": len(matches),
            "incorrect": len(mismatches)
        }

    def _build_confusion_matrix(self, records: list[dict]) -> dict[str, Any]:
        """Build confusion matrix."""
        matrix = defaultdict(lambda: defaultdict(int))

        for record in records:
            expected = record["expected"]
            actual = record["actual"]
            matrix[expected][actual] += 1

        # Convert to regular dict
        result = {}
        for expected, actuals in matrix.items():
            result[expected] = dict(actuals)

        return result

    def format_metrics_report(self, backtest_results: dict[str, Any]) -> str:
        """Format backtest results as readable report."""
        metrics = backtest_results["metrics"]
        confusion = backtest_results["confusion_matrix"]

        report = []
        report.append("=" * 60)
        report.append("BACKTEST RESULTS")
        report.append("=" * 60)
        report.append(f"Overall Accuracy: {metrics['overall_accuracy']:.1%}")
        report.append(f"Correct: {metrics['correct']} / {metrics['total_predictions']}")
        report.append("")

        report.append("Per-Route Metrics:")
        report.append("-" * 60)
        for route, m in metrics["by_route"].items():
            report.append(f"{route:20s} P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} (n={m['support']})")

        report.append("")
        report.append("Confusion Matrix:")
        report.append("-" * 60)

        # Get all routes
        all_routes = set()
        for row in confusion.values():
            all_routes.update(row.keys())
        for expected in confusion.keys():
            all_routes.add(expected)

        all_routes = sorted(all_routes)

        # Header
        header = "Expected \\ Actual".ljust(20) + " ".join(r[:10].ljust(10) for r in all_routes)
        report.append(header)

        # Rows
        for expected in all_routes:
            row = expected[:20].ljust(20)
            for actual in all_routes:
                count = confusion.get(expected, {}).get(actual, 0)
                row += str(count).ljust(10)
            report.append(row)

        report.append("=" * 60)

        return "\n".join(report)
