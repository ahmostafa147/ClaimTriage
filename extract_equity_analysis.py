#!/usr/bin/env python3.11
"""
Equity Market Analysis Extraction using LandingAI ADE
Extracts key information from equity research reports (Goldman Sachs, etc.)
"""
import json
import os
import requests
from pathlib import Path

def extract_equity_analysis(pdf_path: str, api_key: str, output_path: str = None):
    """Extract data from equity market analysis PDFs"""
    schema = {
        "type": "object",
        "properties": {
            "report_metadata": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "publisher": {"type": "string"},
                    "publication_date": {"type": "string"},
                    "authors": {"type": "array", "items": {"type": "string"}},
                    "report_type": {"type": "string"}
                }
            },
            "executive_summary": {
                "type": "object",
                "properties": {
                    "key_points": {"type": "array", "items": {"type": "string"}},
                    "main_thesis": {"type": "string"},
                    "investment_conclusion": {"type": "string"}
                }
            },
            "market_overview": {
                "type": "object",
                "properties": {
                    "current_market_level": {"type": "string"},
                    "ytd_performance": {"type": "string"},
                    "recent_trends": {"type": "array", "items": {"type": "string"}},
                    "market_drivers": {"type": "array", "items": {"type": "string"}}
                }
            },
            "index_targets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index_name": {"type": "string"},
                        "current_level": {"type": "string"},
                        "target_level": {"type": "string"},
                        "target_date": {"type": "string"},
                        "previous_target": {"type": "string"}
                    }
                }
            },
            "earnings_forecasts": {
                "type": "object",
                "properties": {
                    "current_year_eps": {"type": "string"},
                    "next_year_eps": {"type": "string"},
                    "eps_growth_rate": {"type": "string"},
                    "revenue_growth": {"type": "string"},
                    "margin_forecast": {"type": "string"}
                }
            },
            "valuation_analysis": {
                "type": "object",
                "properties": {
                    "current_pe": {"type": "string"},
                    "forward_pe": {"type": "string"},
                    "target_pe": {"type": "string"},
                    "pe_justification": {"type": "string"},
                    "valuation_metrics": {"type": "array", "items": {"type": "string"}}
                }
            },
            "sector_recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sector": {"type": "string"},
                        "recommendation": {"type": "string"},
                        "rationale": {"type": "string"},
                        "key_stocks": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "thematic_baskets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "basket_name": {"type": "string"},
                        "theme": {"type": "string"},
                        "description": {"type": "string"},
                        "performance": {"type": "string"},
                        "constituents": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "macro_scenarios": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scenario_name": {"type": "string"},
                        "probability": {"type": "string"},
                        "market_impact": {"type": "string"},
                        "index_target": {"type": "string"}
                    }
                }
            },
            "risks_and_catalysts": {
                "type": "object",
                "properties": {
                    "upside_risks": {"type": "array", "items": {"type": "string"}},
                    "downside_risks": {"type": "array", "items": {"type": "string"}},
                    "positive_catalysts": {"type": "array", "items": {"type": "string"}},
                    "negative_catalysts": {"type": "array", "items": {"type": "string"}}
                }
            },
            "positioning_analysis": {
                "type": "object",
                "properties": {
                    "hedge_fund_positioning": {"type": "string"},
                    "mutual_fund_positioning": {"type": "string"},
                    "sentiment_indicator": {"type": "string"},
                    "flows": {"type": "string"}
                }
            },
            "technical_analysis": {
                "type": "object",
                "properties": {
                    "support_levels": {"type": "array", "items": {"type": "string"}},
                    "resistance_levels": {"type": "array", "items": {"type": "string"}},
                    "trend": {"type": "string"},
                    "momentum_indicators": {"type": "string"}
                }
            },
            "investment_strategies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "strategy_name": {"type": "string"},
                        "description": {"type": "string"},
                        "target_investors": {"type": "string"},
                        "recommended_stocks": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "stock_selections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string"},
                        "company_name": {"type": "string"},
                        "sector": {"type": "string"},
                        "recommendation_type": {"type": "string"},
                        "target_price": {"type": "string"},
                        "current_price": {"type": "string"},
                        "upside": {"type": "string"}
                    }
                }
            },
            "key_data_points": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string"},
                        "value": {"type": "string"},
                        "change": {"type": "string"},
                        "significance": {"type": "string"}
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

    # Example: Process Goldman Sachs equity research
    pdf_file = "ok/US Equity Views_ Lowering our S&P 500 EPS and valuation forecasts as the _Maleficent 7_ pushes the index to the brink of corr....pdf"
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found")
        exit(1)

    extract_equity_analysis(pdf_file, api_key)
