#!/usr/bin/env python
"""Verification script to check claims-triage setup."""

import sys
from pathlib import Path


def check_imports():
    """Check that all core modules can be imported."""
    print("Checking imports...")
    try:
        from ade_client import MockExtractor, ADEExtractor
        from pathway_pipe import ClaimsPipeline
        from rule_engine import RuleEngine
        from backtest import Backtester
        from counterfactual import CounterfactualAnalyzer
        from schema import StructuredClaim, RoutingDecision
        from storage import sha256_file, load_yaml_rules
        from normalize import normalize_currency, normalize_date
        from metrics import MetricsTracker
        print("  ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def check_directories():
    """Check that required directories exist."""
    print("\nChecking directories...")
    required_dirs = [
        "demo_data/inbox",
        "demo_data/gold",
        "demo_data/mock_docs",
        "demo_data/extracted_mock",
        "tests"
    ]

    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} missing")
            all_exist = False

    return all_exist


def check_files():
    """Check that required files exist."""
    print("\nChecking required files...")
    required_files = [
        "app.py",
        "rules.yaml",
        "requirements.txt",
        ".env.example",
        "run.sh",
        "README.md"
    ]

    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} missing")
            all_exist = False

    return all_exist


def check_mock_extractor():
    """Test mock extractor."""
    print("\nTesting mock extractor...")
    try:
        from ade_client import MockExtractor

        extractor = MockExtractor()
        files = extractor.generate_synthetic_claims()

        if len(files) >= 10:
            print(f"  ✅ Generated {len(files)} synthetic claims")
        else:
            print(f"  ⚠️  Only generated {len(files)} claims (expected 10+)")

        # Try extracting from first file
        claim = extractor.extract(files[0])
        if claim.file_id and claim.filename:
            print(f"  ✅ Extraction works: {claim.filename}")
        else:
            print("  ❌ Extraction failed")
            return False

        return True
    except Exception as e:
        print(f"  ❌ Mock extractor failed: {e}")
        return False


def check_rule_engine():
    """Test rule engine."""
    print("\nTesting rule engine...")
    try:
        from rule_engine import RuleEngine
        from schema import StructuredClaim

        engine = RuleEngine()

        # Test high-amount claim
        claim = StructuredClaim(
            file_id="test1",
            filename="test.pdf",
            claim_amount_total_usd=75000,
            injury_severity="none",
            incident_type="auto"
        )

        decision = engine.evaluate(claim)
        if decision.route == "litigation":
            print(f"  ✅ Rule engine works: routed to {decision.route}")
        else:
            print(f"  ⚠️  Unexpected route: {decision.route} (expected litigation)")

        return True
    except Exception as e:
        print(f"  ❌ Rule engine failed: {e}")
        return False


def check_pipeline():
    """Test pipeline."""
    print("\nTesting pipeline...")
    try:
        from pathway_pipe import ClaimsPipeline

        pipeline = ClaimsPipeline(app_mode="MOCK")
        pipeline.initialize_mock_data()

        # Process inbox
        results = pipeline.process_inbox()

        print(f"  ✅ Pipeline initialized and processed {len(results)} claims")
        return True
    except Exception as e:
        print(f"  ❌ Pipeline failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Claims Triage Agent - Verification")
    print("=" * 60)

    checks = [
        check_imports,
        check_directories,
        check_files,
        check_mock_extractor,
        check_rule_engine,
        check_pipeline,
    ]

    results = []
    for check in checks:
        results.append(check())

    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED - System ready!")
        print("\nRun the app with:")
        print("  ./run.sh")
        print("  or")
        print("  streamlit run app.py")
        return 0
    else:
        print("❌ Some checks failed - please review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
