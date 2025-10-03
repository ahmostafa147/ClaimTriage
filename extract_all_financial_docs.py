#!/usr/bin/env python3.11
"""
Unified Financial Document Extraction Script
Processes all financial documents in the ok/ folder and extracts structured data
for the Pathway RAG pipeline
"""
import json
import os
import sys
from pathlib import Path
import requests

# Import individual extractors
from extract_financial_outlook import extract_financial_outlook
from extract_equity_analysis import extract_equity_analysis
from extract_market_drivers import extract_market_drivers


def detect_document_type(pdf_path: str) -> str:
    """
    Detect the type of financial document based on filename
    Returns: 'outlook', 'equity', or 'drivers'
    """
    filename = os.path.basename(pdf_path).lower()

    if 'outlook' in filename or 'summary' in filename:
        return 'outlook'
    elif 'equity' in filename or 'views' in filename or 'valuation' in filename:
        return 'equity'
    elif 'drivers' in filename or 'market drivers' in filename or 'weekly' in filename:
        return 'drivers'
    else:
        # Default to market drivers for general reports
        return 'drivers'


def process_all_pdfs(input_dir: str = "ok", output_dir: str = "extracted_data"):
    """
    Process all PDFs in the input directory and extract structured data
    """
    # Get API key
    api_key = os.getenv("LANDINGAI_API_KEY")
    if not api_key:
        print("Error: LANDINGAI_API_KEY environment variable not set")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all PDFs in the input directory
    pdf_files = list(Path(input_dir).glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {input_dir}/")
        return

    print(f"Found {len(pdf_files)} PDF files to process")
    print("-" * 80)

    results = []

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")

        # Detect document type
        doc_type = detect_document_type(str(pdf_file))
        print(f"  Document type: {doc_type}")

        # Set output path
        output_file = Path(output_dir) / f"{pdf_file.stem}_extracted.json"

        try:
            # Extract based on document type
            if doc_type == 'outlook':
                result = extract_financial_outlook(str(pdf_file), api_key, str(output_file))
            elif doc_type == 'equity':
                result = extract_equity_analysis(str(pdf_file), api_key, str(output_file))
            else:  # drivers
                result = extract_market_drivers(str(pdf_file), api_key, str(output_file))

            results.append({
                "file": str(pdf_file),
                "type": doc_type,
                "output": str(output_file),
                "status": "success"
            })

            print(f"  ✓ Successfully extracted to: {output_file}")

        except Exception as e:
            print(f"  ✗ Error processing {pdf_file.name}: {str(e)}")
            results.append({
                "file": str(pdf_file),
                "type": doc_type,
                "status": "error",
                "error": str(e)
            })

    # Save processing summary
    summary_file = Path(output_dir) / "extraction_summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "total_files": len(pdf_files),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }, f, indent=2)

    print("\n" + "=" * 80)
    print(f"Processing complete!")
    print(f"  Total files: {len(pdf_files)}")
    print(f"  Successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"  Failed: {sum(1 for r in results if r['status'] == 'error')}")
    print(f"  Summary saved to: {summary_file}")
    print("=" * 80)


if __name__ == "__main__":
    # Allow custom input/output directories via command line
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "ok"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_data"

    process_all_pdfs(input_dir, output_dir)
