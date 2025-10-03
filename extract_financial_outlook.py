#!/usr/bin/env python3.11
"""
Financial Market Outlook Extraction using LandingAI ADE
Extracts key information from market outlook reports (UBS, Goldman Sachs, etc.)
"""
import json
import os
import requests
from pathlib import Path

def extract_financial_outlook(pdf_path: str, api_key: str, output_path: str = None):
    """Extract data from financial market outlook PDFs"""
    schema = {
        "type": "object",
        "properties": {
            "document_metadata": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "publisher": {"type": "string"},
                    "publication_date": {"type": "string"},
                    "quarter": {"type": "string"},
                    "year": {"type": "string"},
                    "document_type": {"type": "string"}
                }
            },
            "executive_summary": {
                "type": "object",
                "properties": {
                    "key_messages": {"type": "array", "items": {"type": "string"}},
                    "main_themes": {"type": "array", "items": {"type": "string"}},
                    "investment_recommendations": {"type": "array", "items": {"type": "string"}}
                }
            },
            "economic_outlook": {
                "type": "object",
                "properties": {
                    "gdp_forecasts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "region": {"type": "string"},
                                "year": {"type": "string"},
                                "forecast_value": {"type": "string"},
                                "previous_forecast": {"type": "string"}
                            }
                        }
                    },
                    "inflation_forecasts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "region": {"type": "string"},
                                "year": {"type": "string"},
                                "forecast_value": {"type": "string"}
                            }
                        }
                    },
                    "economic_risks": {"type": "array", "items": {"type": "string"}},
                    "economic_opportunities": {"type": "array", "items": {"type": "string"}}
                }
            },
            "monetary_policy": {
                "type": "object",
                "properties": {
                    "fed_outlook": {"type": "string"},
                    "rate_cut_expectations": {"type": "string"},
                    "ecb_outlook": {"type": "string"},
                    "other_central_banks": {"type": "string"}
                }
            },
            "market_outlook": {
                "type": "object",
                "properties": {
                    "equities": {
                        "type": "object",
                        "properties": {
                            "overall_view": {"type": "string"},
                            "sp500_target": {"type": "string"},
                            "eps_forecast": {"type": "string"},
                            "recommended_sectors": {"type": "array", "items": {"type": "string"}},
                            "regional_preferences": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "fixed_income": {
                        "type": "object",
                        "properties": {
                            "overall_view": {"type": "string"},
                            "treasury_yield_forecast": {"type": "string"},
                            "credit_view": {"type": "string"}
                        }
                    },
                    "currencies": {
                        "type": "object",
                        "properties": {
                            "dollar_outlook": {"type": "string"},
                            "recommended_currencies": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "commodities": {
                        "type": "object",
                        "properties": {
                            "gold_outlook": {"type": "string"},
                            "gold_price_target": {"type": "string"},
                            "oil_outlook": {"type": "string"}
                        }
                    }
                }
            },
            "investment_themes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "theme_name": {"type": "string"},
                        "description": {"type": "string"},
                        "recommended_allocation": {"type": "string"}
                    }
                }
            },
            "risks_and_opportunities": {
                "type": "object",
                "properties": {
                    "geopolitical_risks": {"type": "array", "items": {"type": "string"}},
                    "trade_policy_risks": {"type": "array", "items": {"type": "string"}},
                    "market_risks": {"type": "array", "items": {"type": "string"}},
                    "key_opportunities": {"type": "array", "items": {"type": "string"}}
                }
            },
            "asset_allocation": {
                "type": "object",
                "properties": {
                    "cash_recommendation": {"type": "string"},
                    "equities_recommendation": {"type": "string"},
                    "bonds_recommendation": {"type": "string"},
                    "alternatives_recommendation": {"type": "string"}
                }
            },
            "market_forecasts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "asset_class": {"type": "string"},
                        "current_level": {"type": "string"},
                        "target_level": {"type": "string"},
                        "target_date": {"type": "string"}
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

    # Example: Process UBS outlook document
    pdf_file = "ok/outlook-summary-en-4q25.pdf"
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found")
        exit(1)

    extract_financial_outlook(pdf_file, api_key)
