"""Enhanced backtesting module for Claims Triage Pro."""
import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import plotly.graph_objects as go
import plotly.express as px

from schema import StructuredClaim, RoutingDecision

class EnhancedBacktester:
    """Enhanced backtesting with comprehensive metrics and visualizations."""
    
    def __init__(self):
        self.gold_labels_path = Path("demo_data/gold/gold_labels.json")
        self.gold_labels = self._load_gold_labels()
    
    def _load_gold_labels(self) -> Dict[str, str]:
        """Load gold labels from JSON file."""
        if not self.gold_labels_path.exists():
            # Create default gold labels in new format
            default_labels = {
                "version": "1.0",
                "description": "Gold standard labels for claims triage evaluation",
                "claims": [
                    {"file_id": "claim_auto_001", "filename": "claim_auto_001.pdf", "true_route": "adjuster_junior"},
                    {"file_id": "claim_auto_002", "filename": "claim_auto_002.pdf", "true_route": "adjuster_junior"},
                    {"file_id": "claim_auto_003", "filename": "claim_auto_003.pdf", "true_route": "adjuster_junior"},
                    {"file_id": "claim_severe_001", "filename": "claim_severe_001.pdf", "true_route": "litigation"},
                    {"file_id": "claim_severe_002", "filename": "claim_severe_002.pdf", "true_route": "litigation"},
                    {"file_id": "claim_severe_003", "filename": "claim_severe_003.pdf", "true_route": "litigation"},
                    {"file_id": "claim_fraud_001", "filename": "claim_fraud_001.pdf", "true_route": "fraud_queue"},
                    {"file_id": "claim_fraud_002", "filename": "claim_fraud_002.pdf", "true_route": "fraud_queue"},
                    {"file_id": "claim_property_001", "filename": "claim_property_001.pdf", "true_route": "property_specialist"},
                    {"file_id": "claim_property_002", "filename": "claim_property_002.pdf", "true_route": "property_specialist"}
                ]
            }
            
            # Create directory if it doesn't exist
            self.gold_labels_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.gold_labels_path, 'w') as f:
                json.dump(default_labels, f, indent=2)
        
        with open(self.gold_labels_path, 'r') as f:
            labels_data = json.load(f)
        
        # Handle both old and new format
        if isinstance(labels_data, list):
            # Old format: direct array
            return {item["filename"]: item.get("expected_route", item.get("true_route", "adjuster_junior")) for item in labels_data}
        elif isinstance(labels_data, dict) and "claims" in labels_data:
            # New format: object with claims array - match by filename
            return {item["filename"]: item.get("true_route", item.get("expected_route", "adjuster_junior")) for item in labels_data["claims"]}
        else:
            # Fallback
            return {}
    
    def run_backtest(self, claims: List[StructuredClaim], decisions: List[RoutingDecision]) -> Dict[str, Any]:
        """Run comprehensive backtest analysis."""
        # Match claims with decisions and gold labels by filename
        matched_data = []
        for claim in claims:
            decision = next((d for d in decisions if d.file_id == claim.file_id), None)
            gold_route = self.gold_labels.get(claim.filename)
            
            if decision and gold_route:
                matched_data.append({
                    "file_id": claim.file_id,
                    "filename": claim.filename,
                    "predicted_route": decision.route,
                    "actual_route": gold_route,
                    "rule_fired": decision.rule_fired,
                    "confidence": getattr(claim, 'confidences', {}),
                    "claim_amount": claim.claim_amount_total_usd,
                    "injury_severity": claim.injury_severity
                })
        
        if not matched_data:
            # Debug information
            debug_info = {
                "total_claims": len(claims),
                "total_decisions": len(decisions),
                "total_gold_labels": len(self.gold_labels),
                "claim_filenames": [c.filename for c in claims[:5]],
                "gold_filenames": list(self.gold_labels.keys())[:5],
                "matching_filenames": [c.filename for c in claims if c.filename in self.gold_labels]
            }
            return {"error": "No matching data found for backtest", "debug": debug_info}
        
        # Calculate metrics
        y_true = [item["actual_route"] for item in matched_data]
        y_pred = [item["predicted_route"] for item in matched_data]
        
        # Overall metrics
        accuracy = sum(1 for true, pred in zip(y_true, y_pred) if true == pred) / len(y_true)
        
        # Per-route metrics
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
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "support": tp + fn
            }
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=routes)
        
        # Misclassified cases
        misclassified = [
            item for item in matched_data 
            if item["predicted_route"] != item["actual_route"]
        ]
        
        # Coverage analysis
        total_gold = len(self.gold_labels)
        covered = len(matched_data)
        coverage_rate = covered / total_gold if total_gold > 0 else 0
        
        return {
            "metrics": {
                "overall_accuracy": accuracy,
                "coverage_rate": coverage_rate,
                "total_predictions": len(matched_data),
                "total_gold_labels": total_gold,
                "by_route": route_metrics
            },
            "confusion_matrix": {
                "labels": routes,
                "matrix": cm.tolist()
            },
            "misclassified": misclassified,
            "summary": {
                "correct_predictions": len(matched_data) - len(misclassified),
                "incorrect_predictions": len(misclassified),
                "most_common_error": self._get_most_common_error(misclassified)
            }
        }
    
    def _get_most_common_error(self, misclassified: List[Dict]) -> str:
        """Get the most common prediction error."""
        if not misclassified:
            return "No errors"
        
        error_patterns = defaultdict(int)
        for item in misclassified:
            pattern = f"{item['actual_route']} → {item['predicted_route']}"
            error_patterns[pattern] += 1
        
        return max(error_patterns.items(), key=lambda x: x[1])[0]
    
    def generate_confusion_matrix_plot(self, confusion_data: Dict) -> str:
        """Generate Plotly confusion matrix."""
        labels = confusion_data["labels"]
        matrix = confusion_data["matrix"]
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=labels,
            y=labels,
            colorscale='Blues',
            text=matrix,
            texttemplate="%{text}",
            textfont={"size": 16},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Confusion Matrix - Route Predictions",
            xaxis_title="Predicted Route",
            yaxis_title="Actual Route",
            font=dict(size=14)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="confusion-matrix")
