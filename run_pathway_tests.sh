#!/bin/bash
# Run Pathway Production Tests
# Uses LANDINGAI_API_KEY from environment

set -e

echo "========================================================================"
echo "PATHWAY PRODUCTION TESTS"
echo "========================================================================"
echo ""

# Check API key
if [ -z "$LANDINGAI_API_KEY" ]; then
    echo "❌ ERROR: LANDINGAI_API_KEY not set in environment"
    echo ""
    echo "Please set it:"
    echo "  export LANDINGAI_API_KEY='your_key_here'"
    exit 1
fi

echo "✅ LANDINGAI_API_KEY found in environment (length: ${#LANDINGAI_API_KEY})"
echo ""

# Check if we're in the right directory
if [ ! -f "test_prod_pathway.py" ]; then
    echo "❌ ERROR: test_prod_pathway.py not found"
    echo "Please run from ClaimTriage directory"
    exit 1
fi

# Check Python
echo "Checking Python..."
python3 --version
echo ""

# Check Pathway
echo "Checking Pathway..."
python3 -c "
try:
    import pathway as pw
    print('✅ Pathway installed:', pw.__version__)
except ImportError:
    print('⚠️  Pathway not installed')
    print('   Install with: pip install pathway')
"
echo ""

# Run the test
echo "========================================================================"
echo "Running production tests..."
echo "========================================================================"
echo ""

python3 test_prod_pathway.py

echo ""
echo "========================================================================"
echo "TESTS COMPLETE"
echo "========================================================================"
