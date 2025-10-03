#!/usr/bin/env python3.11
import json
import os
import requests

def extract_transcript(pdf_path: str, api_key: str, output_path: str = None):
    schema = {
        "type": "object",
        "properties": {
            "student_profile": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "student_id": {"type": "string"},
                    "major": {"type": "string"},
                    "academic_career": {"type": "string"},
                    "level": {"type": "string"},
                    "expected_graduation": {"type": "string"},
                    "cumulative_gpa": {"type": "number"}
                }
            },
            "enrollment": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "term": {"type": "string"},
                        "courses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "class_code": {"type": "string"},
                                    "title": {"type": "string"},
                                    "units": {"type": "number"},
                                    "grade": {"type": "string"},
                                    "points": {"type": "number"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

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

    if output_path is None:
        output_path = "transcript_extracted.json"

    with open(output_path, 'w') as f:
        json.dump(extracted_data, f, indent=2)

    print(f"Extracted data saved to: {output_path}")
    return extracted_data

if __name__ == "__main__":
    api_key = os.getenv("LANDINGAI_API_KEY")
    if not api_key:
        print("Error: LANDINGAI_API_KEY environment variable not set")
        exit(1)

    pdf_file = "Academic Summary _ CalCentral.pdf"
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found")
        exit(1)

    extract_transcript(pdf_file, api_key)
