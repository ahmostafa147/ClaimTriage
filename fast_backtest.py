"""Fast backtesting module for Claims Triage Pro."""
import json
from pathlib import Path
from typing import List, Dict, Any

from schema import StructuredClaim, RoutingDecision

class FastBacktester:
    """Fast backtesting with essential metrics only."""
    
    def __init__(self):
        self.gold_labels_path = Path("demo_data/gold/gold_labels.json")
        self.gold_labels = self._load_gold_labels()
    
    def _load_gold_labels(self) -> Dict[str, str]:
        """Load gold labels from JSON file."""
        if not self.gold_labels_path.exists():
            return {}
        
        with open(self.gold_labels_path, 'r') as f:
            labels_data = json.load(f)
        
        # Handle both old and new format
        if isinstance(labels_data, list):
            return {item["filename"]: item.get("expected_route", item.get("true_route", "adjuster_junior")) for item in labels_data}
        elif isinstance(labels_data, dict) and "claims" in labels_data:
            return {item["filename"]: item.get("true_route", item.get("expected_route", "adjuster_junior")) for item in labels_data["claims"]}
        else:
            return {}
    
    def run_backtest(self, claims: List[StructuredClaim], decisions: List[RoutingDecision]) -> Dict[str, Any]:
        """Run fast backtest analysis."""
        # Limit to first 10 claims for performance
        claims = claims[:10]
        decisions = decisions[:10]
        
        # Match claims with decisions and gold labels by filename
        matched_data = []
        for claim in claims:
            decision = next((d for d in decisions if d.file_id == claim.file_id), None)
            gold_route = self.gold_labels.get(claim.filename)
            
            if decision and gold_route:
                matched_data.append({
                    "filename": claim.filename,
                    "predicted_route": decision.route,
                    "actual_route": gold_route,
                    "claim_amount": claim.claim_amount_total_usd,
                    "injury_severity": claim.injury_severity
                })
        
        if not matched_data:
            return {"error": "No matching data found for backtest"}
        
        # Fast metrics calculation
        y_true = [item["actual_route"] for item in matched_data]
        y_pred = [item["predicted_route"] for item in matched_data]
        
        # Overall accuracy
        accuracy = sum(1 for true, pred in zip(y_true, y_pred) if true == pred) / len(y_true)
        
        # Simple route metrics
        routes = list(set(y_true + y_pred))
        route_metrics = {}
        
        for route in routes:
            tp = sum(1 for true, pred in zip(y_true, y_pred) if true == route and pred == route)
            fp = sum(1 for true, pred in zip(y_true, y_pred) if true != route and pred == route)
            fn = sum(1 for true, pred in zip(y_true, y_pred) if true == route and pred != route)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            route_metrics[route] = {
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1_score": round(f1_score, 3),
                "support": tp + fn
            }
        
        # Simple confusion matrix
        cm = [[0 for _ in routes] for _ in routes]
        for true, pred in zip(y_true, y_pred):
            true_idx = routes.index(true)
            pred_idx = routes.index(pred)
            cm[true_idx][pred_idx] += 1
        
        # Misclassified cases (limit to 3 for performance)
        misclassified = [
            item for item in matched_data 
            if item["predicted_route"] != item["actual_route"]
        ][:3]
        
        return {
            "metrics": {
                "overall_accuracy": round(accuracy, 3),
                "coverage_rate": round(len(matched_data) / len(self.gold_labels), 3),
                "total_predictions": len(matched_data),
                "total_gold_labels": len(self.gold_labels),
                "by_route": route_metrics
            },
            "confusion_matrix": {
                "labels": routes,
                "matrix": cm
            },
            "misclassified": misclassified,
            "summary": {
                "correct_predictions": len(matched_data) - len(misclassified),
                "incorrect_predictions": len(misclassified),
                "most_common_error": "No errors" if not misclassified else f"{misclassified[0]['actual_route']} → {misclassified[0]['predicted_route']}"
            }
        }
