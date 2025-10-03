# API Data Summary - Claims Triage Pro

## Overview
This directory contains the actual API responses and schemas from the Claims Triage Pro system for manual verification.

## Files Captured

### 1. **schemas.json** - Data Structure Definitions
- **StructuredClaim**: 13 fields including claimant_name, policy_id, claim_amount_total_usd, etc.
- **RoutingDecision**: 10 fields including route, rule_fired, rationale, evidence_pointers, etc.

### 2. **claims.json** - Current Claims Data
- **Total Claims**: 2
- **Claim 1**: 
  - ID: `3b721189-a80d-4a56-8c07-cbb7779a555b`
  - Filename: `7c32af63_claim_severe_002.pdf`
  - Claimant: Emily Davis
  - Amount: $87,500 (severe injury)
  - Route: Should be "litigation" (high amount)
- **Claim 2**:
  - ID: `6ff420d2-7b23-4dca-8edd-62451887ed6a`
  - Filename: `fa4c60fe_8b6aac31_test_claim.pdf`
  - Claimant: John Smith
  - Amount: $3,200 (minor injury)
  - Route: Should be "adjuster_junior" (low amount)

### 3. **decision_1.json** - Routing Decision for Claim 1
- **Route**: "litigation" ✅
- **Rule Fired**: "litigation_high_amount"
- **Rationale**: ["High amount >= $30k triggers litigation review"]
- **Evidence**: Points to claim_amount_total_usd field
- **Safety**: No flags, good confidence

### 4. **decision_2.json** - Routing Decision for Claim 2
- **Route**: "adjuster_junior" ✅
- **Rule Fired**: "default"
- **Rationale**: ["No risk signals, standard processing"]
- **Safety**: No flags, good confidence

### 5. **metrics.json** - System Performance
- Shows extraction and routing latency metrics
- Queue sizes and processing statistics

### 6. **rules.json** - Current Routing Rules
- Contains the YAML rules configuration
- Shows litigation threshold at $30k
- Default route for standard claims

### 7. **backtest.json** - Backtest Results
- Performance metrics against gold labels
- Accuracy, precision, recall, F1 scores

## Key Findings

### ✅ **API is Working Correctly**
1. **Claims are being processed**: 2 claims successfully uploaded and processed
2. **Decisions are being generated**: Both claims have routing decisions
3. **Rules are being applied**: High-value claim ($87.5k) → litigation, Low-value claim ($3.2k) → adjuster_junior
4. **Data structure is consistent**: Claims have proper IDs, filenames, amounts, etc.

### 🔍 **Frontend Issue Identified**
The problem is NOT with the API - it's with the frontend claim selection:

1. **Claims are loaded**: Frontend receives 2 claims correctly
2. **Decisions exist**: Both claims have valid routing decisions
3. **Selection issue**: Frontend may not be properly handling the click events or displaying the selected state

### 📋 **Data Structure Verification**
- **Claim ID**: Used for decision lookup (e.g., `3b721189-a80d-4a56-8c07-cbb7779a555b`)
- **Filename**: Used for display (e.g., `7c32af63_claim_severe_002.pdf`)
- **Decision ID**: Separate from claim ID (e.g., `b156cf59-a764-4e9d-be4c-16f785bcca21`)

## Next Steps
1. ✅ API data verified - all endpoints working correctly
2. 🔧 Frontend claim selection needs debugging
3. 🎯 Focus on UI interaction and state management

## Test Commands Used
```bash
# Get all claims
curl -s http://localhost:8000/api/claims

# Get specific decision
curl -s http://localhost:8000/api/decisions/3b721189-a80d-4a56-8c07-cbb7779a555b

# Run backtest
curl -s -X POST http://localhost:8000/api/backtest
```

---
*Generated: $(date)*
*System Status: API ✅ Working | Frontend 🔧 Needs Fix*
