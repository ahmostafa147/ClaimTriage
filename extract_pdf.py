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
            "email": {"type": "string"}
        },
        "required": ["invoice_number", "order_number", "email"]
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
    # Get API key from environment
    api_key = os.getenv("LANDINGAI_API_KEY")
    if not api_key:
        print("Error: LANDINGAI_API_KEY environment variable not set")
        exit(1)

    # Find PDF
    pdf_file = "PDF Invoice Example.pdf"
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found")
        exit(1)

    # Extract
    extract_pdf(pdf_file, api_key)
