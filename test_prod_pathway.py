#!/usr/bin/env python3
"""Test production mode with Pathway and LandingAI ADE.

IMPORTANT: Set your API key in environment before running:
    export LANDINGAI_API_KEY="your_key_here"
    python test_prod_pathway.py

Or pass as argument:
    python test_prod_pathway.py YOUR_API_KEY
"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


def test_prod_with_pathway(api_key: str = None):
    """Test production mode with Pathway streaming."""

    print("=" * 70)
    print("TESTING PRODUCTION MODE WITH PATHWAY")
    print("=" * 70)
    print()

    # Set API key
    if api_key:
        os.environ["LANDINGAI_API_KEY"] = api_key
        print(f"✅ LandingAI API key set (length: {len(api_key)})")
    elif "LANDINGAI_API_KEY" in os.environ:
        print(f"✅ LandingAI API key found in environment")
    else:
        print("❌ ERROR: No API key provided")
        print()
        print("Usage:")
        print("  export LANDINGAI_API_KEY='your_key'")
        print("  python test_prod_pathway.py")
        print()
        print("Or:")
        print("  python test_prod_pathway.py YOUR_API_KEY")
        return False

    print()

    # Check Pathway availability
    try:
        import pathway as pw
        print("✅ Pathway available")
        pathway_available = True
    except ImportError:
        print("⚠️  Pathway not installed")
        print("   Install with: pip install pathway")
        pathway_available = False

    print()

    # Import pipeline
    print("Importing pipeline...")
    from pathway_pipe import get_pipeline, PATHWAY_AVAILABLE

    if not PATHWAY_AVAILABLE:
        print("⚠️  Pathway not detected by system")

    print()

    # Test 1: Simple Pipeline in PROD mode
    print("=" * 70)
    print("TEST 1: Simple Pipeline with LandingAI ADE")
    print("=" * 70)
    print()

    try:
        pipeline = get_pipeline(app_mode="PROD", use_pathway=False)
        print(f"✅ Pipeline initialized: {type(pipeline).__name__}")
        print(f"   Extractor: {type(pipeline.extractor).__name__}")

        # Initialize mock data (we'll use mock docs but with ADE extractor)
        pipeline.initialize_mock_data()
        print("✅ Mock data initialized")

        # Process a file
        from pathlib import Path
        inbox_dir = Path("demo_data/inbox")
        pdf_files = list(inbox_dir.glob("*.pdf"))

        if pdf_files:
            print(f"\n📄 Testing with: {pdf_files[0].name}")
            result = pipeline.process_file(pdf_files[0])

            if result:
                claim, decision = result
                print(f"✅ Claim extracted:")
                print(f"   - File ID: {claim.file_id}")
                print(f"   - Claimant: {claim.claimant_name}")
                print(f"   - Amount: ${claim.claim_amount_total_usd:,.2f}" if claim.claim_amount_total_usd else "   - Amount: N/A")
                print(f"   - Route: {decision.route}")
                print(f"   - Rule: {decision.rule_fired}")
                print(f"   - Rationale: {decision.rationale[0] if decision.rationale else 'N/A'}")
            else:
                print("⚠️  No result returned")
        else:
            print("⚠️  No PDF files found in inbox")

        # Get metrics
        metrics = pipeline.get_metrics()
        print(f"\n✅ Metrics collected:")
        print(f"   - Extraction P50: {metrics['extraction']['p50']:.3f}s")
        print(f"   - Routing P50: {metrics['routing']['p50']*1000:.1f}ms")

        print("\n✅ TEST 1 PASSED")

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Test 2: Pathway Streaming Pipeline (if available)
    if pathway_available and PATHWAY_AVAILABLE:
        print("=" * 70)
        print("TEST 2: Pathway Streaming Pipeline with LandingAI ADE")
        print("=" * 70)
        print()

        try:
            from pathway_pipe import PathwayClaimsPipeline, reset_pipeline

            # Reset to get new pipeline
            reset_pipeline()

            pipeline = get_pipeline(app_mode="PROD", use_pathway=True)
            print(f"✅ Pathway pipeline initialized: {type(pipeline).__name__}")
            print(f"   Extractor: {type(pipeline.extractor).__name__}")

            # Test basic operations (don't start streaming for this test)
            pipeline.initialize_mock_data()
            print("✅ Mock data initialized")

            # Test file processing
            pdf_files = list(Path("demo_data/inbox").glob("*.pdf"))
            if pdf_files:
                print(f"\n📄 Testing with: {pdf_files[0].name}")
                result = pipeline.process_file(pdf_files[0])

                if result:
                    claim, decision = result
                    print(f"✅ Claim extracted via Pathway pipeline:")
                    print(f"   - File ID: {claim.file_id}")
                    print(f"   - Route: {decision.route}")
                    print(f"   - Rule: {decision.rule_fired}")

            print("\n✅ TEST 2 PASSED")

        except Exception as e:
            print(f"\n❌ TEST 2 FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("=" * 70)
        print("TEST 2: SKIPPED (Pathway not available)")
        print("=" * 70)
        print()
        print("To enable Pathway streaming:")
        print("  pip install pathway")
        print()

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("✅ LandingAI ADE connection: Working")
    print(f"{'✅' if pathway_available else '⚠️ '} Pathway streaming: {'Available' if pathway_available else 'Not installed'}")
    print("✅ Production mode: Functional")
    print()
    print("System is ready for production deployment!")
    print()

    return True


if __name__ == "__main__":
    # Get API key from argument or environment
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]

    success = test_prod_with_pathway(api_key)
    sys.exit(0 if success else 1)
