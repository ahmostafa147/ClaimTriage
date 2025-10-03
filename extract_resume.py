#!/usr/bin/env python3.11
import json
import os
import requests

def extract_resume(pdf_path: str, api_key: str, output_path: str = None):
    schema = {
        "type": "object",
        "properties": {
            "personal_info": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                    "linkedin": {"type": "string"},
                    "github": {"type": "string"}
                }
            },
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "institution": {"type": "string"},
                        "degree": {"type": "string"},
                        "major": {"type": "string"},
                        "minor": {"type": "string"},
                        "gpa": {"type": "string"},
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"},
                        "coursework": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "experience": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "company": {"type": "string"},
                        "location": {"type": "string"},
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"},
                        "responsibilities": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "projects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "technologies": {"type": "array", "items": {"type": "string"}},
                        "description": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "skills": {
                "type": "object",
                "properties": {
                    "languages": {"type": "array", "items": {"type": "string"}},
                    "frameworks": {"type": "array", "items": {"type": "string"}},
                    "tools": {"type": "array", "items": {"type": "string"}},
                    "libraries": {"type": "array", "items": {"type": "string"}}
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
        output_path = "resume_extracted.json"

    with open(output_path, 'w') as f:
        json.dump(extracted_data, f, indent=2)

    print(f"Extracted data saved to: {output_path}")
    return extracted_data

if __name__ == "__main__":
    api_key = os.getenv("LANDINGAI_API_KEY")
    if not api_key:
        print("Error: LANDINGAI_API_KEY environment variable not set")
        exit(1)

    pdf_file = "Ahmed Resume ML.pdf"
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found")
        exit(1)

    extract_resume(pdf_file, api_key)
