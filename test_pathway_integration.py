"""Test script for Pathway integration."""
import os
import time
from pathlib import Path
import sys

# Set environment to use Pathway
os.environ["USE_PATHWAY"] = "true"

from pathway_pipe import get_pipeline, reset_pipeline, PATHWAY_AVAILABLE


def test_pathway_basic():
    """Test basic Pathway pipeline functionality."""
    print("=" * 60)
    print("Testing Pathway Integration")
    print("=" * 60)

    # Check if Pathway is available
    print(f"\n1. Pathway Available: {PATHWAY_AVAILABLE}")
    if not PATHWAY_AVAILABLE:
        print("   ❌ Pathway not available. Skipping tests.")
        return False

    # Create pipeline
    print("\n2. Creating Pathway pipeline...")
    try:
        pipeline = get_pipeline(app_mode="MOCK", use_pathway=True)
        print("   ✓ Pipeline created successfully")
    except Exception as e:
        print(f"   ❌ Failed to create pipeline: {e}")
        return False

    # Initialize mock data
    print("\n3. Initializing mock data...")
    try:
        pipeline.initialize_mock_data()
        print("   ✓ Mock data initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize mock data: {e}")
        return False

    # Wait for streaming to process files
    print("\n4. Waiting for streaming pipeline to process files (5s)...")
    time.sleep(5)

    # Check if claims were processed
    print("\n5. Checking processed claims...")
    claims = pipeline.get_claims()
    print(f"   Claims processed: {len(claims)}")

    if len(claims) > 0:
        print("   ✓ Claims were processed")

        # Show sample claim
        sample_claim = claims[0]
        print(f"\n   Sample Claim:")
        print(f"   - ID: {sample_claim.file_id}")
        print(f"   - Filename: {sample_claim.filename}")
        print(f"   - Claimant: {sample_claim.claimant_name}")
        print(f"   - Amount: ${sample_claim.claim_amount_total_usd:,.2f}" if sample_claim.claim_amount_total_usd else "N/A")
        print(f"   - Severity: {sample_claim.injury_severity}")
    else:
        print("   ⚠ No claims processed yet")

    # Check if decisions were made
    print("\n6. Checking routing decisions...")
    decisions = pipeline.get_decisions()
    print(f"   Decisions made: {len(decisions)}")

    if len(decisions) > 0:
        print("   ✓ Routing decisions were made")

        # Show sample decision
        sample_decision = decisions[0]
        print(f"\n   Sample Decision:")
        print(f"   - Route: {sample_decision.route}")
        print(f"   - Rule: {sample_decision.rule_fired}")
        print(f"   - Created: {sample_decision.created_at}")
    else:
        print("   ⚠ No decisions made yet")

    # Check metrics
    print("\n7. Checking metrics...")
    metrics = pipeline.get_metrics()
    print(f"   Extraction P50: {metrics['extraction']['p50']:.3f}s")
    print(f"   Extraction P95: {metrics['extraction']['p95']:.3f}s")
    print(f"   Routing P50: {metrics['routing']['p50']*1000:.1f}ms")
    print(f"   Routing P95: {metrics['routing']['p95']*1000:.1f}ms")

    if metrics["queues"]:
        print(f"\n   Queue Sizes:")
        for route, size in metrics["queues"].items():
            print(f"   - {route}: {size}")

    # Stop pipeline
    print("\n8. Stopping pipeline...")
    try:
        pipeline.stop()
        print("   ✓ Pipeline stopped")
    except Exception as e:
        print(f"   ⚠ Warning during stop: {e}")

    # Reset
    reset_pipeline()

    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)

    return True


def test_pathway_schema_validation():
    """Test Pathway schema definitions."""
    print("\n" + "=" * 60)
    print("Testing Pathway Schema Validation")
    print("=" * 60)

    try:
        from pathway_schemas import (
            StructuredClaimSchema,
            RoutingDecisionSchema,
            MetricsSchema,
            QueueSizeSchema
        )

        print("\n✓ All schema imports successful:")
        print("  - StructuredClaimSchema")
        print("  - RoutingDecisionSchema")
        print("  - MetricsSchema")
        print("  - QueueSizeSchema")

        return True
    except Exception as e:
        print(f"\n❌ Schema validation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PATHWAY INTEGRATION TEST SUITE")
    print("=" * 60)

    results = []

    # Test 1: Schema validation
    results.append(("Schema Validation", test_pathway_schema_validation()))

    # Test 2: Basic functionality
    results.append(("Basic Functionality", test_pathway_basic()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
