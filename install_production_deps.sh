#!/bin/bash
# Install production dependencies for Pathway and LandingAI integration

echo "========================================="
echo "Installing Production Dependencies"
echo "========================================="
echo ""

# Use the correct Python
PYTHON=/opt/anaconda3/bin/python
PIP=/opt/anaconda3/bin/pip

echo "Using Python: $PYTHON"
$PYTHON --version
echo ""

echo "Installing Pathway..."
$PIP install pathway

echo ""
echo "Installing LandingAI SDK..."
$PIP install landingai-python

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""

echo "Verifying installations..."
$PYTHON -c "
try:
    import pathway as pw
    print('✅ Pathway installed:', pw.__version__)
except ImportError:
    print('❌ Pathway installation failed')

try:
    import landingai
    print('✅ LandingAI SDK installed')
except ImportError:
    print('❌ LandingAI SDK installation failed')
"

echo ""
echo "You can now run the tests again:"
echo "  $PYTHON test_prod_pathway.py"
