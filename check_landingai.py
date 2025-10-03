#!/usr/bin/env python3
"""Check LandingAI SDK installation and available modules."""

import sys

print("=" * 70)
print("LANDINGAI SDK CHECK")
print("=" * 70)
print()

# Check if any landingai package is installed
try:
    import landingai
    print(f"✅ landingai package found")
    print(f"   Location: {landingai.__file__}")
    print(f"   Version: {getattr(landingai, '__version__', 'unknown')}")
    print()
except ImportError:
    print("❌ landingai package not found")
    print()
    print("Install with:")
    print("  pip install landingai")
    print("  # OR")
    print("  pip install landingai-python")
    sys.exit(1)

# Check available modules
print("Checking available modules...")
print()

modules_to_check = [
    "landingai.predict",
    "landingai.ade",
    "landingai.vision_agent",
    "landingai.pipeline",
]

found_modules = []
for module_name in modules_to_check:
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        found_modules.append(module_name)
    except ImportError as e:
        print(f"❌ {module_name} - {e}")

print()

if "landingai.predict" in found_modules:
    print("✅ Recommended: Use Predictor API")
    print()
    print("Example usage:")
    print("  from landingai.predict import Predictor")
    print("  predictor = Predictor(endpoint_id='...', api_key='...')")
    print()

elif "landingai.ade" in found_modules:
    print("✅ Available: ADE API")
    print()
    print("Example usage:")
    print("  from landingai.ade import ADEClient")
    print("  client = ADEClient(api_key='...')")
    print()

else:
    print("⚠️  No usable LandingAI API found")
    print()
    print("You may need a different version or package.")
    print("Try:")
    print("  pip install --upgrade landingai")

print("=" * 70)
