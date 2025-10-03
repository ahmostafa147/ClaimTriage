# ClaimTriage Setup Quick Reference

## 🚀 Installation (3 Steps)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install poppler (for PDF viewer)
brew install poppler  # macOS
# OR
sudo apt-get install poppler-utils  # Ubuntu

# 3. Run the app
streamlit run app.py
```

**That's it!** Open browser at http://localhost:8501

---

## ⚡ Quick Commands

### Start App
```bash
streamlit run app.py
```

### With Pathway Enabled
```bash
USE_PATHWAY=true streamlit run app.py
```

### Validate Installation
```bash
python3 validate_pathway.py
```

### Run Tests
```bash
python test_pathway_integration.py
```

---

## 🎛️ UI Controls

### Sidebar
- ☑️ **Use Pathway Streaming** - Enable real-time processing
- 🎲 **Generate Mock Documents** - Create sample PDFs
- 📤 **Upload Claim PDF** - Upload your own files
- 🔄 **Process Inbox** - Manual processing (without Pathway)
- 📝 **Rules Editor** - Edit routing rules

### Center Panel (PDF Viewer)
- 📄 **Claim Selector** - Choose which claim to view
- ➡️ **Page Slider** - Navigate multi-page PDFs
- 🎨 **Quality** - Adjust DPI (100/150/200)
- 🔍 **Highlight Evidence** - Show bounding boxes

### Right Panel
- 📊 **Claim Details** - Extracted fields
- 🎯 **Routing Decision** - Route, rule, evidence
- ❓ **Why Not?** - Alternative routes

---

## 📁 Key Directories

```
ClaimTriage/
├── demo_data/
│   ├── inbox/          ← Drop PDFs here
│   └── mock_docs/      ← Generated samples
├── venv/               ← Virtual environment
└── *.py                ← Application code
```

---

## 🎯 Feature Toggle

| Feature | Enable Via | Default |
|---------|-----------|---------|
| Pathway Streaming | UI checkbox OR `USE_PATHWAY=true` | Off |
| PDF Viewer | Auto (if pdf2image installed) | On |
| Mock Mode | `APP_MODE=MOCK` | On |
| Production | `APP_MODE=PROD` + API key | Off |

---

## 🔧 Dependencies

### Required
- Python 3.10+
- streamlit
- pydantic
- PyYAML
- pathway

### Optional (but recommended)
- pdf2image (for PDF viewer)
- poppler (system dependency for pdf2image)

---

## 📊 Metrics Dashboard

Top bar shows:
- **Extraction P50/P95** - Time to extract claims
- **Routing P50/P95** - Time to route claims
- **Total Claims** - Number processed
- **Queue Sizes** - Claims by route

---

## 🎨 Evidence Colors

When "Highlight Evidence" is enabled:
- 🔴 **Claimant Name** - Red
- 🔵 **Policy ID** - Cyan
- 🟢 **Incident Date** - Blue
- 🟡 **Claim Amount** - Yellow
- 🟠 **Injury Severity** - Orange
- ⚫ **Incident Type** - Gray

---

## 🐛 Common Issues

### PDF won't render
```bash
brew install poppler  # macOS
sudo apt-get install poppler-utils  # Ubuntu
```

### "Pathway not available"
```bash
pip install pathway==0.9.0
```

### Dependencies missing
```bash
pip install -r requirements.txt
```

### Port 8501 in use
```bash
streamlit run app.py --server.port 8502
```

---

## 📚 Documentation

- **Setup**: `RUN_PATHWAY.md`
- **Pathway Integration**: `PATHWAY_INTEGRATION.md`
- **PDF Viewer**: `PDF_VIEWER_SETUP.md`
- **Quick Start**: `QUICKSTART_PATHWAY.md`
- **Full Summary**: `PATHWAY_IMPLEMENTATION_SUMMARY.md`

---

## ✅ Verify Installation

```bash
# Check Pathway
python3 -c "import pathway; print('✓ Pathway')"

# Check PDF viewer
python3 -c "from pdf2image import convert_from_path; print('✓ PDF viewer')"

# Run validation
python3 validate_pathway.py
```

---

## 🎓 Example Workflow

1. **Start app**: `streamlit run app.py`
2. **Enable Pathway**: Check sidebar checkbox
3. **Generate data**: Click "Generate Mock Documents"
4. **Select claim**: Choose from dropdown
5. **View PDF**: See rendered document with evidence
6. **Edit rules**: Update rules in sidebar
7. **Recompute**: Click "Apply Rules & Recompute"
8. **See changes**: Watch counterfactual analysis

---

## 🚀 Production Deployment

```bash
# Set environment
export APP_MODE=PROD
export USE_PATHWAY=true
export LANDINGAI_API_KEY=your_key_here

# Run with production settings
streamlit run app.py --server.address 0.0.0.0
```

---

## 💡 Pro Tips

1. **Pathway Streaming** - Best for real-time processing
2. **Standard Mode** - Better for batch processing
3. **Lower DPI** - Faster PDF rendering
4. **Evidence Highlighting** - Great for verification
5. **Rules Editor** - Live updates with Pathway

---

**Need help?** Check the full documentation or run `python3 validate_pathway.py`
