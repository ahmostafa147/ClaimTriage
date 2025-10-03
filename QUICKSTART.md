# Claims Triage Agent - Quick Start Guide

## 🚀 Get Running in 60 Seconds

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# 1. Navigate to project
cd claims-triage

# 2. Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file
cp .env.example .env

# 5. Run the app
./run.sh
# Or: streamlit run app.py
```

### First Run

The app will:
1. ✅ Generate 10 synthetic claim PDFs in `demo_data/mock_docs/`
2. ✅ Process 6 claims automatically
3. ✅ Open UI at http://localhost:8501

### What You'll See

**Metrics Strip:**
- Extraction P50/P95: ~0.05s in mock mode
- Routing P50/P95: ~2ms
- Queue sizes per route

**Main UI:**
- **Left Panel**: Upload PDFs, edit rules, run counterfactual analysis
- **Center Panel**: Document viewer with evidence bboxes
- **Right Panel**: Extracted fields, routing decision, chain of custody

**Bottom Panel:**
- Backtest results with precision/recall/confusion matrix

## 🎯 Try These Demo Actions

### 1. Browse Different Claims
- Select different claims from dropdown
- Notice routing differences:
  - `claim_auto_001.pdf` → Junior Adjuster (low amount)
  - `claim_severe_001.pdf` → Litigation ($75k+)
  - `claim_fraud_001.pdf` → Fraud Queue (repeat claims)

### 2. Edit Rules Live
```yaml
# Change litigation threshold from 50000 to 25000
- name: litigation_high_amount
  when: "claim_amount_total_usd is not None and claim_amount_total_usd >= 25000"
  route: "litigation"
```
- Click **Apply Rules & Recompute**
- Watch counterfactual table show routing changes

### 3. Run Backtest
- Click **Run Backtest**
- See accuracy metrics
- View confusion matrix
- Click mismatches to investigate

### 4. Upload New Claim
- Click **Upload Claim PDF**
- Instantly routed and added to queue

## 🔧 Switch to Production Mode

Edit `.env`:
```bash
APP_MODE=PROD
LANDINGAI_API_KEY=your_key_here
```

Restart:
```bash
./run.sh
```

System will use LandingAI ADE for real document extraction.

## ✅ Verify Installation

```bash
# Run tests
pytest tests/ -v

# Should see: 13 passed
```

## 📊 Key Features

1. **Transparent Proofs**: Every decision shows rule, rationale, evidence, and hashes
2. **Hot Reload Rules**: Change rules and see before/after routing instantly
3. **Live Metrics**: Real-time P50/P95 for extraction and routing
4. **Backtest**: Evaluate against gold labels
5. **Mock Mode**: Works out-of-box with no API keys

## 🐛 Troubleshooting

**No claims showing?**
```bash
# Click "Generate Mock Documents" then "Process Inbox"
```

**Import errors?**
```bash
pip install -r requirements.txt --upgrade
```

**Port in use?**
```bash
streamlit run app.py --server.port 8502
```

## 📚 Next Steps

- Read full [README.md](README.md) for architecture details
- Check `rules.yaml` to understand rule DSL
- Explore `demo_data/gold/gold_labels.jsonl` for backtest format
- Review test files in `tests/` for usage examples

---

**Built for Microsoft Hackathon 2025**
