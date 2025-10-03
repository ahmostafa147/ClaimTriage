"""ADE client with mock and production extractors."""
import json
import os
import random
from pathlib import Path
from typing import Any
import uuid

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

from schema import StructuredClaim
from normalize import (
    normalize_currency, normalize_date, extract_adverse_keywords,
    normalize_injury_severity, normalize_incident_type
)
from storage import sha256_file, sha256_json


class MockExtractor:
    """Mock extractor that generates synthetic PDFs and extracts data."""

    def __init__(self, mock_docs_dir: str = "demo_data/mock_docs",
                 extracted_dir: str = "demo_data/extracted_mock"):
        self.mock_docs_dir = Path(mock_docs_dir)
        self.extracted_dir = Path(extracted_dir)
        self.mock_docs_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)

    def generate_synthetic_claims(self) -> list[Path]:
        """Generate synthetic claim PDFs."""
        claims_data = [
            {
                "filename": "claim_auto_001.pdf",
                "claimant_name": "John Smith",
                "policy_id": "POL-2024-001",
                "incident_date": "2024-01-15",
                "claim_amount": "$3,200",
                "injury_severity": "minor",
                "incident_type": "auto",
                "repeat_claims": 0,
                "description": "Minor fender bender at intersection. No injuries reported."
            },
            {
                "filename": "claim_auto_002.pdf",
                "claimant_name": "Sarah Johnson",
                "policy_id": "POL-2024-002",
                "incident_date": "2024-02-20",
                "claim_amount": "$4,800",
                "injury_severity": "none",
                "incident_type": "auto",
                "repeat_claims": 0,
                "description": "Rear-end collision in parking lot. Vehicle damage only."
            },
            {
                "filename": "claim_auto_003.pdf",
                "claimant_name": "Michael Brown",
                "policy_id": "POL-2024-003",
                "incident_date": "2024-03-10",
                "claim_amount": "$2,100",
                "injury_severity": "none",
                "incident_type": "auto",
                "repeat_claims": 0,
                "description": "Sideswipe accident on highway. Minor vehicle damage."
            },
            {
                "filename": "claim_severe_001.pdf",
                "claimant_name": "Emily Davis",
                "policy_id": "POL-2024-004",
                "incident_date": "2024-01-25",
                "claim_amount": "$75,000",
                "injury_severity": "severe",
                "incident_type": "auto",
                "repeat_claims": 0,
                "description": "Major collision with severe injuries requiring hospitalization."
            },
            {
                "filename": "claim_severe_002.pdf",
                "claimant_name": "Robert Wilson",
                "policy_id": "POL-2024-005",
                "incident_date": "2024-02-15",
                "claim_amount": "$92,500",
                "injury_severity": "severe",
                "incident_type": "auto",
                "repeat_claims": 0,
                "description": "Critical injuries from high-speed collision. Life-threatening situation."
            },
            {
                "filename": "claim_severe_003.pdf",
                "claimant_name": "Lisa Martinez",
                "policy_id": "POL-2024-006",
                "incident_date": "2024-03-05",
                "claim_amount": "$65,000",
                "injury_severity": "severe",
                "incident_type": "liability",
                "repeat_claims": 0,
                "description": "Severe slip and fall injury at commercial property."
            },
            {
                "filename": "claim_fraud_001.pdf",
                "claimant_name": "David Anderson",
                "policy_id": "POL-2024-007",
                "incident_date": "2024-02-28",
                "claim_amount": "$8,500",
                "injury_severity": "minor",
                "incident_type": "auto",
                "repeat_claims": 3,
                "description": "Prior loss reported last year. Inconsistent story about accident details."
            },
            {
                "filename": "claim_fraud_002.pdf",
                "claimant_name": "Jennifer Taylor",
                "policy_id": "POL-2024-008",
                "incident_date": "2024-03-15",
                "claim_amount": "$12,000",
                "injury_severity": "none",
                "incident_type": "auto",
                "repeat_claims": 2,
                "description": "Suspicious circumstances. Possible staged accident with conflicting witness statements."
            },
            {
                "filename": "claim_property_001.pdf",
                "claimant_name": "James Thomas",
                "policy_id": "POL-2024-009",
                "incident_date": "2024-01-30",
                "claim_amount": "$18,500",
                "injury_severity": "none",
                "incident_type": "property",
                "repeat_claims": 0,
                "description": "Water damage to building. Potential subrogation against contractor."
            },
            {
                "filename": "claim_property_002.pdf",
                "claimant_name": "Patricia Jackson",
                "policy_id": "POL-2024-010",
                "incident_date": "2024-03-20",
                "claim_amount": "$22,300",
                "injury_severity": "none",
                "incident_type": "property",
                "repeat_claims": 0,
                "description": "Fire damage to residential property. Subrogation potential."
            },
        ]

        generated_files = []
        for claim_data in claims_data:
            file_path = self.mock_docs_dir / claim_data["filename"]
            if not file_path.exists():
                self._generate_pdf(file_path, claim_data)
            generated_files.append(file_path)

        return generated_files

    def _generate_pdf(self, file_path: Path, data: dict[str, Any]) -> None:
        """Generate a single PDF claim document."""
        doc = SimpleDocTemplate(str(file_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title = Paragraph("<b>FIRST NOTICE OF LOSS (FNOL)</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))

        # Claimant info
        info_data = [
            ["Claimant Name:", data["claimant_name"]],
            ["Policy Number:", data["policy_id"]],
            ["Incident Date:", data["incident_date"]],
            ["Claim Amount:", data["claim_amount"]],
            ["Injury Severity:", data["injury_severity"].title()],
            ["Incident Type:", data["incident_type"].title()],
        ]

        if data["repeat_claims"] > 0:
            info_data.append(["Repeat Claims Count:", str(data["repeat_claims"])])

        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))

        # Description
        story.append(Paragraph("<b>Incident Description:</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(data["description"], styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Damage breakdown table
        damage_data = [
            ["Item", "Amount"],
            ["Vehicle Damage", f"${random.randint(1000, 5000):,}"],
            ["Medical Expenses", f"${random.randint(0, 10000):,}"],
            ["Towing/Rental", f"${random.randint(200, 800):,}"],
            ["Total", data["claim_amount"]],
        ]
        damage_table = Table(damage_data, colWidths=[3*inch, 2*inch])
        damage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(damage_table)

        doc.build(story)

    def extract(self, file_path: str | Path) -> StructuredClaim:
        """Extract structured claim from PDF."""
        file_path = Path(file_path)
        file_id = str(uuid.uuid4())

        # Check if we have cached extraction
        cache_file = self.extracted_dir / f"{file_path.stem}.json"

        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
                claim = StructuredClaim(**data)
                claim.file_id = file_id
                return claim

        # Generate extraction based on filename patterns
        claim_data = self._extract_from_filename(file_path)
        claim_data["file_id"] = file_id
        claim_data["filename"] = file_path.name

        # Add mock bboxes and confidences
        claim_data["bboxes"] = self._generate_mock_bboxes()
        claim_data["confidences"] = self._generate_mock_confidences(claim_data)

        claim = StructuredClaim(**claim_data)

        # Cache the extraction
        with open(cache_file, "w") as f:
            json.dump(claim.model_dump(), f, indent=2)

        return claim

    def _extract_from_filename(self, file_path: Path) -> dict[str, Any]:
        """Extract claim data from filename pattern."""
        filename = file_path.stem.lower()

        # Parse based on patterns
        if "fraud" in filename:
            return {
                "claimant_name": "Fraud Suspect",
                "policy_id": f"POL-2024-{random.randint(100, 999)}",
                "incident_date": "2024-03-15",
                "claim_amount_total_usd": random.uniform(5000, 15000),
                "injury_severity": "minor",
                "incident_type": "auto",
                "repeat_claims_count": random.randint(2, 4),
                "adverse_keywords": ["prior loss", "suspicious", "inconsistent story"],
                "extracted_tables": [{"item": "Total", "amount": "$12,000"}]
            }
        elif "severe" in filename:
            return {
                "claimant_name": "Severe Injury Claimant",
                "policy_id": f"POL-2024-{random.randint(100, 999)}",
                "incident_date": "2024-02-20",
                "claim_amount_total_usd": random.uniform(50000, 100000),
                "injury_severity": "severe",
                "incident_type": "auto",
                "repeat_claims_count": 0,
                "adverse_keywords": [],
                "extracted_tables": [{"item": "Medical", "amount": "$75,000"}]
            }
        elif "property" in filename:
            return {
                "claimant_name": "Property Owner",
                "policy_id": f"POL-2024-{random.randint(100, 999)}",
                "incident_date": "2024-01-30",
                "claim_amount_total_usd": random.uniform(15000, 25000),
                "injury_severity": "none",
                "incident_type": "property",
                "repeat_claims_count": 0,
                "adverse_keywords": [],
                "extracted_tables": [{"item": "Property Damage", "amount": "$18,500"}]
            }
        else:
            return {
                "claimant_name": "Standard Claimant",
                "policy_id": f"POL-2024-{random.randint(100, 999)}",
                "incident_date": "2024-03-01",
                "claim_amount_total_usd": random.uniform(2000, 5000),
                "injury_severity": "minor",
                "incident_type": "auto",
                "repeat_claims_count": 0,
                "adverse_keywords": [],
                "extracted_tables": [{"item": "Vehicle Damage", "amount": "$3,500"}]
            }

    def _generate_mock_bboxes(self) -> dict[str, list[dict[str, Any]]]:
        """Generate mock bounding boxes."""
        return {
            "claimant_name": [{"page": 0, "x0": 100, "y0": 150, "x1": 300, "y1": 170}],
            "policy_id": [{"page": 0, "x0": 100, "y0": 180, "x1": 300, "y1": 200}],
            "incident_date": [{"page": 0, "x0": 100, "y0": 210, "x1": 300, "y1": 230}],
            "claim_amount_total_usd": [{"page": 0, "x0": 100, "y0": 240, "x1": 300, "y1": 260}],
        }

    def _generate_mock_confidences(self, data: dict[str, Any]) -> dict[str, float]:
        """Generate mock confidence scores."""
        confidences = {}
        for key in ["claimant_name", "policy_id", "incident_date", "claim_amount_total_usd"]:
            if data.get(key) is not None:
                confidences[key] = random.uniform(0.85, 0.99)
        return confidences


class ADEExtractor:
    """Production extractor using LandingAI."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("LANDINGAI_API_KEY")
        if not self.api_key:
            raise ValueError("LANDINGAI_API_KEY not set")

        # Get endpoint ID if available (optional for some APIs)
        self.endpoint_id = os.getenv("LANDINGAI_ENDPOINT_ID", "")

    def extract(self, file_path: str | Path) -> StructuredClaim:
        """Extract structured claim using LandingAI."""
        try:
            # Import LandingAI SDK
            from landingai.predict import Predictor, OcrPredictor

            # For document extraction, we'll use OcrPredictor if available, else Predictor
            # Note: This is a simplified version. Real usage would need proper endpoint setup.

            # Create predictor
            # For demo: if no endpoint_id, use OcrPredictor for general OCR
            if self.endpoint_id:
                predictor = Predictor(endpoint_id=self.endpoint_id, api_key=self.api_key)
            else:
                # Use OCR predictor for document extraction
                try:
                    predictor = OcrPredictor(api_key=self.api_key)
                except Exception as e:
                    print(f"Note: Could not initialize OcrPredictor: {e}")
                    print("Using mock extraction. For real LandingAI extraction, set LANDINGAI_ENDPOINT_ID")
                    raise

            # Extract with retries
            max_retries = 3
            result = None

            for attempt in range(max_retries):
                try:
                    # Read and predict
                    from PIL import Image

                    # Convert PDF to image or read directly
                    with open(file_path, 'rb') as f:
                        # Predict using LandingAI
                        prediction_result = predictor.predict(image=str(file_path))

                    # Extract text and structured data from result
                    # LandingAI returns predictions in various formats
                    # This is a simplified extraction - real implementation would parse the specific format

                    extracted_text = ""
                    if hasattr(prediction_result, 'text'):
                        extracted_text = prediction_result.text
                    elif hasattr(prediction_result, 'ocr_text'):
                        extracted_text = prediction_result.ocr_text
                    elif isinstance(prediction_result, dict):
                        extracted_text = prediction_result.get('text', '')

                    # For now, parse text to extract fields (simplified)
                    # Real implementation would use LandingAI's structured extraction
                    result = {
                        "full_text": extracted_text,
                        "claimant_name": None,  # Would be extracted from text
                        "policy_id": None,
                        "incident_date": None,
                        "claim_amount": None,
                        "injury_severity": None,
                        "incident_type": None,
                        "tables": [],
                        "bboxes": {},
                        "confidences": {}
                    }

                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    continue

            # Map to StructuredClaim
            claim_data = {
                "file_id": str(uuid.uuid4()),
                "filename": Path(file_path).name,
                "claimant_name": result.get("claimant_name"),
                "policy_id": result.get("policy_id"),
                "incident_date": normalize_date(result.get("incident_date")),
                "claim_amount_total_usd": normalize_currency(result.get("claim_amount")),
                "injury_severity": normalize_injury_severity(result.get("injury_severity")),
                "incident_type": normalize_incident_type(result.get("incident_type")),
                "repeat_claims_count": 0,  # Would need additional logic
                "adverse_keywords": extract_adverse_keywords(result.get("full_text", "")),
                "extracted_tables": result.get("tables", []),
                "bboxes": result.get("bboxes", {}),
                "confidences": result.get("confidences", {})
            }

            # Filter low confidence fields
            for field, conf in claim_data["confidences"].items():
                if conf < 0.6:
                    claim_data[field] = None

            return StructuredClaim(**claim_data)

        except Exception as e:
            # Fallback to mock on error
            print(f"ADE extraction failed: {e}, falling back to mock")
            return MockExtractor().extract(file_path)
