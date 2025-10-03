#!/usr/bin/env python3.11
"""
Market Drivers Analysis Extraction using LandingAI ADE
Extracts key information from weekly market outlook and driver analysis reports
"""
import json
import os
import requests
from pathlib import Path

def extract_market_drivers(pdf_path: str, api_key: str, output_path: str = None):
    """Extract data from market drivers and weekly outlook PDFs"""
    schema = {
        "type": "object",
        "properties": {
            "document_info": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "publisher": {"type": "string"},
                    "publication_date": {"type": "string"},
                    "report_type": {"type": "string"},
                    "authors": {"type": "array", "items": {"type": "string"}}
                }
            },
            "key_messages": {
                "type": "array",
                "items": {"type": "string"}
            },
            "market_drivers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "driver_name": {"type": "string"},
                        "description": {"type": "string"},
                        "impact": {"type": "string"},
                        "outlook": {"type": "string"},
                        "recommendations": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "weekly_outlook": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "market_performance": {"type": "string"},
                    "key_events": {"type": "array", "items": {"type": "string"}},
                    "upcoming_events": {"type": "array", "items": {"type": "string"}}
                }
            },
            "questions_for_week": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "context": {"type": "string"},
                        "implications": {"type": "string"}
                    }
                }
            },
            "policy_developments": {
                "type": "object",
                "properties": {
                    "us_trade_policy": {"type": "string"},
                    "fiscal_policy": {"type": "string"},
                    "monetary_policy": {"type": "string"},
                    "other_policies": {"type": "array", "items": {"type": "string"}}
                }
            },
            "geopolitical_risks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string"},
                        "issue": {"type": "string"},
                        "status": {"type": "string"},
                        "market_impact": {"type": "string"}
                    }
                }
            },
            "economic_data": {
                "type": "object",
                "properties": {
                    "recent_releases": {"type": "array", "items": {"type": "string"}},
                    "upcoming_releases": {"type": "array", "items": {"type": "string"}},
                    "key_indicators": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "indicator": {"type": "string"},
                                "current_value": {"type": "string"},
                                "previous_value": {"type": "string"},
                                "forecast": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "sector_highlights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sector": {"type": "string"},
                        "performance": {"type": "string"},
                        "drivers": {"type": "array", "items": {"type": "string"}},
                        "outlook": {"type": "string"}
                    }
                }
            },
            "investment_themes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string"},
                        "rationale": {"type": "string"},
                        "recommendations": {"type": "array", "items": {"type": "string"}},
                        "risks": {"type": "string"}
                    }
                }
            },
            "asset_class_views": {
                "type": "object",
                "properties": {
                    "equities": {
                        "type": "object",
                        "properties": {
                            "view": {"type": "string"},
                            "rationale": {"type": "string"},
                            "recommendations": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "fixed_income": {
                        "type": "object",
                        "properties": {
                            "view": {"type": "string"},
                            "rationale": {"type": "string"},
                            "recommendations": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "currencies": {
                        "type": "object",
                        "properties": {
                            "view": {"type": "string"},
                            "rationale": {"type": "string"},
                            "recommendations": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "commodities": {
                        "type": "object",
                        "properties": {
                            "view": {"type": "string"},
                            "rationale": {"type": "string"},
                            "recommendations": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "alternatives": {
                        "type": "object",
                        "properties": {
                            "view": {"type": "string"},
                            "rationale": {"type": "string"},
                            "recommendations": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            },
            "tactical_recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "recommendation": {"type": "string"},
                        "asset_class": {"type": "string"},
                        "time_horizon": {"type": "string"},
                        "conviction_level": {"type": "string"}
                    }
                }
            },
            "risk_factors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "risk_name": {"type": "string"},
                        "description": {"type": "string"},
                        "probability": {"type": "string"},
                        "potential_impact": {"type": "string"},
                        "mitigation": {"type": "string"}
                    }
                }
            },
            "market_positioning": {
                "type": "object",
                "properties": {
                    "sentiment": {"type": "string"},
                    "positioning_metrics": {"type": "array", "items": {"type": "string"}},
                    "flows": {"type": "string"},
                    "valuation_levels": {"type": "string"}
                }
            },
            "takeaways": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "takeaway": {"type": "string"},
                        "action_items": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
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

    # Example: Process market drivers document
    pdf_file = "ok/Market Drivers to Watch in the Second Half of 2025.pdf"
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found")
        exit(1)

    extract_market_drivers(pdf_file, api_key)
