# Testing Production Mode with Pathway

## 🔒 Security Note

**IMPORTANT:** Never commit API keys to git or store them in files. Always use environment variables.

## Testing Options

### Option 1: Using Test Script (Recommended)

The project includes a test script that safely handles API keys:

```bash
cd "/Users/ahmostafa/Desktop/Microsoft Hackathon/ClaimTriage"

# Method 1: Environment variable (most secure)
export LANDINGAI_API_KEY="YOUR_KEY_HERE"
python test_prod_pathway.py

# Method 2: Command line argument
python test_prod_pathway.py YOUR_KEY_HERE
```

### Option 2: Manual Testing

```bash
# 1. Install Pathway (optional but recommended)
pip install pathway

# 2. Set environment variables
export LANDINGAI_API_KEY="YOUR_KEY_HERE"
export APP_MODE="PROD"
export USE_PATHWAY_STREAMING="true"

# 3. Run the app
streamlit run app.py
```

### Option 3: Quick Python Test

```python
import os

# Set API key
os.environ["LANDINGAI_API_KEY"] = "YOUR_KEY_HERE"
os.environ["APP_MODE"] = "PROD"

# Import and test
from pathway_pipe import get_pipeline

# Test simple pipeline with ADE
pipeline = get_pipeline(app_mode="PROD", use_pathway=False)
pipeline.initialize_mock_data()
results = pipeline.process_inbox()

print(f"Processed {len(results)} claims")
for claim, decision in results[:3]:
    print(f"  - {claim.filename}: {decision.route}")
```

## What Gets Tested

### Test 1: Simple Pipeline + LandingAI ADE
- ✅ API key authentication
- ✅ Document extraction via ADE
- ✅ Field extraction quality
- ✅ Routing decisions
- ✅ Performance metrics

### Test 2: Pathway Streaming + LandingAI ADE
- ✅ Pathway initialization
- ✅ Real-time file watching
- ✅ Streaming extraction
- ✅ Background processing
- ✅ Output connectors

## Expected Output

```
======================================================================
TESTING PRODUCTION MODE WITH PATHWAY
======================================================================

✅ LandingAI API key set (length: 67)
✅ Pathway available

Importing pipeline...

======================================================================
TEST 1: Simple Pipeline with LandingAI ADE
======================================================================

✅ Pipeline initialized: ClaimsPipeline
   Extractor: ADEExtractor

✅ Mock data initialized

📄 Testing with: claim_auto_001.pdf
✅ Claim extracted:
   - File ID: abc-123-def
   - Claimant: John Smith
   - Amount: $3,200.00
   - Route: adjuster_junior
   - Rule: default
   - Rationale: No risk signals, standard processing

✅ Metrics collected:
   - Extraction P50: 2.345s
   - Routing P50: 2.1ms

✅ TEST 1 PASSED

======================================================================
TEST 2: Pathway Streaming Pipeline with LandingAI ADE
======================================================================

✅ Pathway pipeline initialized: PathwayClaimsPipeline
   Extractor: ADEExtractor

✅ Mock data initialized

📄 Testing with: claim_auto_001.pdf
✅ Claim extracted via Pathway pipeline:
   - File ID: abc-123-def
   - Route: adjuster_junior
   - Rule: default

✅ TEST 2 PASSED

======================================================================
SUMMARY
======================================================================

✅ LandingAI ADE connection: Working
✅ Pathway streaming: Available
✅ Production mode: Functional

System is ready for production deployment!
```

## Troubleshooting

### API Key Issues

**Error:** `LANDINGAI_API_KEY not found`
```bash
# Solution: Set the key
export LANDINGAI_API_KEY="your_key_here"
```

**Error:** `Authentication failed`
```bash
# Check key format (should be base64-like string)
echo $LANDINGAI_API_KEY | wc -c  # Should be ~60-70 characters
```

### Pathway Issues

**Warning:** `Pathway not available`
```bash
# Solution: Install Pathway
pip install pathway

# Or for full features:
pip install pathway[all]
```

**Error:** `ModuleNotFoundError: No module named 'pathway'`
```bash
# Make sure you're in the right environment
pip list | grep pathway

# Reinstall if needed
pip install --upgrade pathway
```

### Performance Issues

If extraction is slow:
- Check network connection to LandingAI
- Verify API rate limits
- Consider caching for demo purposes

## Performance Expectations

### With LandingAI ADE (Production)

| Metric | Expected Value |
|--------|---------------|
| Extraction time | 2-5 seconds per document |
| Routing time | <10 milliseconds |
| Accuracy | 90-95% for clean documents |
| Accuracy | 70-85% for noisy scans |

### With Pathway Streaming

| Metric | Expected Value |
|--------|---------------|
| Latency | <100ms after extraction |
| Throughput | 10-20 claims/min (limited by ADE) |
| Stream lag | <1 second |

## Demo Mode vs Production

### Demo (MOCK Mode)
```bash
APP_MODE=MOCK
# Fast, reliable, works offline
# Extraction: 0.05s
# Good for presentations
```

### Production (PROD Mode)
```bash
APP_MODE=PROD
LANDINGAI_API_KEY=your_key
# Real document extraction
# Extraction: 2-5s
# Production quality
```

## Verification Checklist

Before demo/production:

- [ ] API key set and valid
- [ ] Pathway installed (optional but recommended)
- [ ] Test script passes
- [ ] Can process at least 3 different document types
- [ ] Routing decisions look reasonable
- [ ] Metrics are being tracked
- [ ] No error messages in logs

## Quick Commands

```bash
# Full test with Pathway
export LANDINGAI_API_KEY="your_key"
pip install pathway
python test_prod_pathway.py

# Quick UI test
export LANDINGAI_API_KEY="your_key"
export APP_MODE=PROD
streamlit run app.py

# Check status
python -c "from pathway_pipe import PATHWAY_AVAILABLE; print(f'Pathway: {PATHWAY_AVAILABLE}')"
```

## Security Best Practices

1. **Never commit .env with real keys**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment variables**
   ```bash
   export LANDINGAI_API_KEY="key"  # Temporary
   # Or add to ~/.bashrc for persistence
   ```

3. **Rotate keys regularly**
   - Use separate keys for dev/prod
   - Rotate after demos
   - Revoke test keys

4. **Clear after testing**
   ```bash
   unset LANDINGAI_API_KEY
   ```

## Integration Tests

Run all tests including production mode:

```bash
# Set API key
export LANDINGAI_API_KEY="your_key"

# Run all tests
pytest tests/ -v

# Run only Pathway tests
pytest tests/test_pathway.py -v

# Run production test
python test_prod_pathway.py
```

## Support

If you encounter issues:

1. Check this guide
2. Review logs in terminal
3. Verify API key format
4. Test with MOCK mode first
5. Check LandingAI dashboard for API status

---

**Ready for production testing!** 🚀

Use the test script to safely verify LandingAI ADE + Pathway integration.
