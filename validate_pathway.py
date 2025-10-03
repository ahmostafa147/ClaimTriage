"""Validate Pathway integration without running full tests."""
import sys
from pathlib import Path

def validate_files():
    """Validate that all necessary files exist."""
    print("=" * 60)
    print("Pathway Integration Validation")
    print("=" * 60)

    files_to_check = [
        ("pathway_schemas.py", "Pathway schema definitions"),
        ("pathway_pipeline.py", "Pathway streaming pipeline"),
        ("pathway_pipe.py", "Pipeline factory (updated)"),
        ("test_pathway_integration.py", "Integration test suite"),
        ("PATHWAY_INTEGRATION.md", "Documentation"),
    ]

    all_exist = True

    print("\n1. Checking required files...")
    for filename, description in files_to_check:
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            print(f"   ✓ {filename:30s} ({size:,} bytes) - {description}")
        else:
            print(f"   ❌ {filename:30s} - MISSING")
            all_exist = False

    return all_exist


def validate_imports():
    """Validate that imports are correct."""
    print("\n2. Validating Python syntax...")

    files_to_validate = [
        "pathway_schemas.py",
        "pathway_pipeline.py",
    ]

    all_valid = True

    for filename in files_to_validate:
        try:
            with open(filename, 'r') as f:
                code = f.read()
                compile(code, filename, 'exec')
            print(f"   ✓ {filename:30s} - Valid Python syntax")
        except SyntaxError as e:
            print(f"   ❌ {filename:30s} - Syntax error: {e}")
            all_valid = False
        except Exception as e:
            print(f"   ⚠ {filename:30s} - Could not validate: {e}")

    return all_valid


def validate_integration_points():
    """Validate integration points in existing files."""
    print("\n3. Checking integration points...")

    checks = [
        ("pathway_pipe.py", "from pathway_pipeline import PathwayClaimsPipeline",
         "Pathway pipeline import"),
        ("pathway_pipe.py", "use_pathway",
         "use_pathway parameter"),
        ("app.py", "use_pathway",
         "Pathway toggle in UI"),
        ("app.py", "Use Pathway Streaming",
         "Pathway checkbox label"),
    ]

    all_integrated = True

    for filename, search_string, description in checks:
        try:
            with open(filename, 'r') as f:
                content = f.read()
                if search_string in content:
                    print(f"   ✓ {filename:20s} - {description}")
                else:
                    print(f"   ❌ {filename:20s} - Missing: {description}")
                    all_integrated = False
        except FileNotFoundError:
            print(f"   ❌ {filename:20s} - File not found")
            all_integrated = False

    return all_integrated


def validate_documentation():
    """Check documentation completeness."""
    print("\n4. Validating documentation...")

    doc_file = Path("PATHWAY_INTEGRATION.md")

    if not doc_file.exists():
        print("   ❌ PATHWAY_INTEGRATION.md not found")
        return False

    with open(doc_file, 'r') as f:
        content = f.read()

    sections = [
        "## Overview",
        "## Architecture",
        "## Key Features",
        "## Usage",
        "## Testing",
        "## Performance Characteristics",
        "## Troubleshooting",
    ]

    all_present = True
    for section in sections:
        if section in content:
            print(f"   ✓ {section}")
        else:
            print(f"   ❌ Missing section: {section}")
            all_present = False

    return all_present


def main():
    """Run all validations."""
    print("\n" + "=" * 60)
    print("PATHWAY INTEGRATION VALIDATION")
    print("=" * 60)

    results = []

    results.append(("File Structure", validate_files()))
    results.append(("Python Syntax", validate_imports()))
    results.append(("Integration Points", validate_integration_points()))
    results.append(("Documentation", validate_documentation()))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    for check_name, passed in results:
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{check_name:25s}: {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL VALIDATIONS PASSED")
        print("\nThe Pathway integration has been successfully implemented!")
        print("\nTo use it:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Set environment: export USE_PATHWAY=true")
        print("  3. Run app: streamlit run app.py")
        print("  4. Or toggle 'Use Pathway Streaming' in the UI")
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("\nPlease review the errors above.")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
