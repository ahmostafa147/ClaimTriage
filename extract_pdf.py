#!/usr/bin/env python3.11
"""
PDF extraction using LandingAI ADE
"""
import json
import os
from pathlib import Path
import requests

def extract_pdf(pdf_path: str, api_key: str, output_path: str = None):
    """Extract data from PDF using LandingAI ADE"""
    schema = {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "order_number": {"type": "string"},
            "invoice_date": {"type": "string"},
            "due_date": {"type": "string"},
            "total_due": {"type": "number"},
            "subtotal": {"type": "number"},
            "tax": {"type": "number"},
            "total": {"type": "number"},
            "payment_terms": {"type": "string"},
            "late_fee_percentage": {"type": "number"},
            "from_company": {"type": "string"},
            "from_address": {"type": "string"},
            "from_email": {"type": "string"},
            "to_company": {"type": "string"},
            "to_address": {"type": "string"},
            "to_email": {"type": "string"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "quantity": {"type": "number"},
                        "service": {"type": "string"},
                        "description": {"type": "string"},
                        "rate": {"type": "number"},
                        "adjustment": {"type": "string"},
                        "subtotal": {"type": "number"}
                    }
                }
            },
            "bank_name": {"type": "string"},
            "bank_account": {"type": "string"},
            "bank_bsb": {"type": "string"},
            "payment_status": {"type": "string"}
        }
    }

    # Extract from PDF
    url = 'https://api.va.landing.ai/v1/tools/agentic-document-analysis'
    with open(pdf_path, 'rb') as f:
        files = {'pdf': f}
        data = {'fields_schema': json.dumps(schema)}
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.post(url, files=files, data=data, headers=headers)

    result = response.json()
    extracted_data = {
        "file": pdf_path,
        "extracted_fields": result.get("data", {}).get("extracted_schema", {}),
        "full_response": result
    }

    # Output path
    if output_path is None:
        pdf_stem = Path(pdf_path).stem
        output_path = f"{pdf_stem}_extracted.json"

    # Write JSON
    with open(output_path, 'w') as f:
        json.dump(extracted_data, f, indent=2)

    print(f"Extracted data saved to: {output_path}")
    return extracted_data

if __name__ == "__main__":
    api_key = os.getenv("LANDINGAI_API_KEY")
    if not api_key:
        print("Error: LANDINGAI_API_KEY environment variable not set")
        exit(1)

    pdf_file = "PDF Invoice Example.pdf"
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found")
        exit(1)

    extract_pdf(pdf_file, api_key)
