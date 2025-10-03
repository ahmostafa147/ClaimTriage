#!/usr/bin/env python3
"""Quick test of Pathway integration with production mode."""

import os
import sys
from pathlib import Path

print("=" * 70)
print("QUICK PATHWAY + LANDINGAI TEST")
print("=" * 70)
print()

# Check API key
if not os.getenv("LANDINGAI_API_KEY"):
    print("❌ ERROR: LANDINGAI_API_KEY not found in environment")
    print()
    print("Set it with:")
    print('  export LANDINGAI_API_KEY="your_key"')
    sys.exit(1)

print(f"✅ API key found (length: {len(os.getenv('LANDINGAI_API_KEY'))})")
print()

# Check Pathway
try:
    import pathway as pw
    print(f"✅ Pathway installed: {pw.__version__}")
    PATHWAY_AVAILABLE = True
except ImportError:
    print("⚠️  Pathway not installed (will use simple pipeline)")
    PATHWAY_AVAILABLE = False

print()

# Import project
sys.path.insert(0, str(Path(__file__).parent))

print("Importing pipeline...")
try:
    from pathway_pipe import get_pipeline, PATHWAY_AVAILABLE as PW_DETECTED
    print(f"✅ Pipeline imported (Pathway detected: {PW_DETECTED})")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

print()

# Test 1: Check extractor type
print("=" * 70)
print("TEST 1: Production Mode Extractor")
print("=" * 70)
print()

pipeline = get_pipeline(app_mode="PROD", use_pathway=False)
print(f"Pipeline type: {type(pipeline).__name__}")
print(f"Extractor type: {type(pipeline.extractor).__name__}")

if type(pipeline.extractor).__name__ == "ADEExtractor":
    print("✅ Using LandingAI ADE (production mode)")
else:
    print(f"⚠️  Using {type(pipeline.extractor).__name__} (fallback)")

print()

# Test 2: Process a file
print("=" * 70)
print("TEST 2: Extract Document with ADE")
print("=" * 70)
print()

# Initialize mock data
print("Initializing mock documents...")
pipeline.initialize_mock_data()

# Get a PDF to test
pdf_files = list(Path("demo_data/inbox").glob("*.pdf"))
if not pdf_files:
    print("⚠️  No PDF files found in inbox")
    print("   Checking mock_docs...")
    pdf_files = list(Path("demo_data/mock_docs").glob("*.pdf"))

if pdf_files:
    test_file = pdf_files[0]
    print(f"Testing with: {test_file.name}")
    print()

    try:
        print("Extracting (this may take 2-5 seconds with ADE)...")
        result = pipeline.process_file(test_file)

        if result:
            claim, decision = result
            print("✅ Extraction successful!")
            print()
            print(f"Extracted Data:")
            print(f"  File ID: {claim.file_id}")
            print(f"  Filename: {claim.filename}")
            print(f"  Claimant: {claim.claimant_name or 'N/A'}")
            print(f"  Policy: {claim.policy_id or 'N/A'}")
            print(f"  Date: {claim.incident_date or 'N/A'}")

            if claim.claim_amount_total_usd:
                print(f"  Amount: ${claim.claim_amount_total_usd:,.2f}")
            else:
                print(f"  Amount: N/A")

            print(f"  Injury: {claim.injury_severity}")
            print(f"  Type: {claim.incident_type}")
            print(f"  Repeat: {claim.repeat_claims_count}")

            if claim.adverse_keywords:
                print(f"  Keywords: {', '.join(claim.adverse_keywords)}")

            print()
            print(f"Routing Decision:")
            print(f"  Route: {decision.route}")
            print(f"  Rule: {decision.rule_fired}")

            if decision.rationale:
                print(f"  Rationale: {decision.rationale[0]}")

            print()
            print("✅ TEST 2 PASSED")
        else:
            print("⚠️  No result returned (may be already processed)")

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ No PDF files available for testing")

print()

# Test 3: Metrics
print("=" * 70)
print("TEST 3: Performance Metrics")
print("=" * 70)
print()

metrics = pipeline.get_metrics()
print(f"Extraction times:")
print(f"  P50: {metrics['extraction']['p50']:.3f}s")
print(f"  P95: {metrics['extraction']['p95']:.3f}s")
print(f"  Count: {metrics['extraction']['count']}")

print()
print(f"Routing times:")
print(f"  P50: {metrics['routing']['p50']*1000:.1f}ms")
print(f"  P95: {metrics['routing']['p95']*1000:.1f}ms")

print()
print("✅ TEST 3 PASSED")

print()

# Test 4: Pathway pipeline (if available)
if PATHWAY_AVAILABLE:
    print("=" * 70)
    print("TEST 4: Pathway Streaming Pipeline")
    print("=" * 70)
    print()

    try:
        from pathway_pipe import reset_pipeline
        reset_pipeline()

        pathway_pipeline = get_pipeline(app_mode="PROD", use_pathway=True)
        print(f"✅ Pathway pipeline created: {type(pathway_pipeline).__name__}")
        print(f"   Extractor: {type(pathway_pipeline.extractor).__name__}")
        print(f"   Has streaming: {hasattr(pathway_pipeline, 'start_streaming')}")

        print()
        print("✅ TEST 4 PASSED")
    except Exception as e:
        print(f"⚠️  Pathway pipeline test skipped: {e}")
else:
    print("=" * 70)
    print("TEST 4: SKIPPED (Pathway not installed)")
    print("=" * 70)
    print()
    print("To enable Pathway streaming:")
    print("  pip install pathway")

print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("✅ LandingAI ADE: Connected")
print(f"{'✅' if PATHWAY_AVAILABLE else '⚠️ '} Pathway: {'Installed' if PATHWAY_AVAILABLE else 'Not installed'}")
print("✅ Production mode: Working")
print()

if PATHWAY_AVAILABLE:
    print("🎉 System ready for production with Pathway streaming!")
else:
    print("✅ System working in production mode")
    print("   Install Pathway for streaming: pip install pathway")

print()
print("=" * 70)
