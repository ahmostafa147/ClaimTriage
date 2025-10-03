# How to Run ClaimTriage with Pathway Integration

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
# Start Streamlit app
streamlit run app.py
```

### Step 3: Enable Pathway Streaming

In the Streamlit UI:
1. Look at the **left sidebar**
2. Find the checkbox: ☑️ **"Use Pathway Streaming"**
3. Check it to enable real-time streaming
4. The app will restart automatically with Pathway enabled

You should see: **🔄 Real-time streaming enabled with Pathway**

---

## 📋 Detailed Instructions

### Option A: Using the UI (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install system dependency for PDF viewer (optional but recommended)
#    macOS:
brew install poppler
#    Ubuntu:
sudo apt-get install poppler-utils

# 3. Start the app
streamlit run app.py

# 4. In the browser:
#    - Sidebar → Check "Use Pathway Streaming"
#    - Drop PDF files in demo_data/inbox/
#    - Watch them process automatically with PDF preview!
```

### Option B: Using Environment Variables

```bash
# 1. Set environment variables
export USE_PATHWAY=true
export APP_MODE=MOCK

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py

# The app will start with Pathway enabled automatically
```

### Option C: Command Line (One-liner)

```bash
USE_PATHWAY=true streamlit run app.py
```

---

## 🎯 What to Expect

### When Pathway is Enabled:

1. **Sidebar shows:**
   ```
   ☑️ Use Pathway Streaming
   🔄 Real-time streaming enabled with Pathway
   ```

2. **Console shows:**
   ```
   Using Pathway streaming pipeline
   ```

3. **Behavior:**
   - Files in `demo_data/inbox/` are processed automatically
   - No need to click "Process Inbox" button
   - Sub-second latency for new files
   - Real-time metrics updates

### When Pathway is Disabled:

1. **Sidebar shows:**
   ```
   ☐ Use Pathway Streaming
   ```

2. **Behavior:**
   - Standard batch processing mode
   - Click "Process Inbox" to process files manually
   - Uses in-memory pipeline

---

## 📁 File Workflow

### 1. Generate Mock Data (First Time)

In the Streamlit UI:
```
Sidebar → Click "Generate Mock Documents"
```

This creates sample PDFs in `demo_data/inbox/`

### 2. Process Files

**With Pathway (Automatic):**
- Just drop PDF files in `demo_data/inbox/`
- They're processed automatically in real-time
- Watch the UI update instantly

**Without Pathway (Manual):**
- Drop PDF files in `demo_data/inbox/`
- Click "Process Inbox" button
- UI updates after processing

### 3. View Results

- **Center panel**: View processed claims
- **Right panel**: See routing decisions and evidence
- **Top metrics**: Check processing latency (P50, P95)
- **Queue sizes**: Monitor claim distribution by route

---

## 🔧 Troubleshooting

### Issue: "Pathway not available"

**Solution:**
```bash
pip install pathway==0.9.0
```

### Issue: "No module named 'pydantic'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Files not processing with Pathway

**Check:**
1. Pathway checkbox is enabled ☑️
2. Files are in `demo_data/inbox/`
3. Files have `.pdf` extension
4. Console shows "Using Pathway streaming pipeline"

**Debug:**
```bash
# Run validation script
python3 validate_pathway.py
```

### Issue: Port 8501 already in use

**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### Issue: Disk space error during pip install

**Solution:**
```bash
# Install only core dependencies
pip install streamlit pydantic PyYAML pathway

# Or clean pip cache
pip cache purge
```

---

## 💡 Usage Tips

### Comparing Standard vs Pathway

Run the app twice side-by-side:

**Terminal 1 (Standard):**
```bash
USE_PATHWAY=false streamlit run app.py --server.port 8501
```

**Terminal 2 (Pathway):**
```bash
USE_PATHWAY=true streamlit run app.py --server.port 8502
```

Drop the same PDF in `demo_data/inbox/` and compare:
- Processing latency
- Real-time updates
- Queue tracking

### Testing Performance

```bash
# 1. Enable Pathway
# 2. Generate mock docs (creates 6 PDFs)
# 3. Watch the metrics:
#    - Extraction P50/P95
#    - Routing P50/P95
#    - Queue distribution
```

### Editing Rules

1. In sidebar, edit the rules in "Rules Editor"
2. Click "Apply Rules & Recompute"
3. With Pathway: Only changed claims reprocess (incremental)
4. Without Pathway: All claims reprocess (full)

---

## 📊 Monitoring

### Check if Pathway is Running

Look for these indicators:

**In UI:**
- ✅ Checkbox: "Use Pathway Streaming" is checked
- ✅ Message: "🔄 Real-time streaming enabled with Pathway"

**In Console:**
```
Using Pathway streaming pipeline
```

**In Metrics:**
- Metrics update in real-time as files arrive
- No manual refresh needed

### Performance Metrics

After processing files, check:

```
Top Metrics Bar:
├─ Extraction P50: ~0.05s (with Pathway)
├─ Extraction P95: ~0.10s (with Pathway)
├─ Routing P50: ~2ms (with Pathway)
├─ Routing P95: ~5ms (with Pathway)
├─ Total Claims: Count
└─ Queue Sizes: By route
```

---

## 🧪 Testing the Integration

### Quick Test (No Dependencies)

```bash
python3 validate_pathway.py
```

Expected output:
```
✓ ALL VALIDATIONS PASSED
```

### Full Test (Requires Dependencies)

```bash
pip install -r requirements.txt
python test_pathway_integration.py
```

This will:
1. Create a Pathway pipeline
2. Generate mock data
3. Process claims
4. Verify routing decisions
5. Check metrics

---

## 🎓 Example Session

```bash
# Terminal
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ streamlit run app.py

  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501

# Browser opens at http://localhost:8501
# 1. Sidebar: Check ☑️ "Use Pathway Streaming"
# 2. Click "Generate Mock Documents"
# 3. Watch claims appear in real-time!
# 4. Try uploading your own PDF
# 5. Edit rules and see instant updates
```

---

## 📱 Access URLs

After running `streamlit run app.py`:

- **Local**: http://localhost:8501
- **Network**: http://YOUR_IP:8501

To share on network:
```bash
streamlit run app.py --server.address 0.0.0.0
```

---

## 🛑 Stopping the App

**In Terminal:**
- Press `Ctrl + C`

**In Browser:**
- Just close the tab (server keeps running)
- Use `Ctrl + C` in terminal to fully stop

---

## 🔄 Switching Modes

### Enable Pathway
```
UI: Check ☑️ "Use Pathway Streaming"
ENV: export USE_PATHWAY=true
```

### Disable Pathway
```
UI: Uncheck ☐ "Use Pathway Streaming"
ENV: export USE_PATHWAY=false
```

The app restarts automatically when toggling.

---

## 📚 Additional Resources

- **Quick Start**: `QUICKSTART_PATHWAY.md`
- **Full Documentation**: `PATHWAY_INTEGRATION.md`
- **Implementation Summary**: `PATHWAY_IMPLEMENTATION_SUMMARY.md`
- **Pathway Docs**: https://pathway.com/developers/documentation/

---

## ✅ Checklist

Before running:
- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Directory exists: `demo_data/inbox/`

To use Pathway:
- [ ] Pathway checkbox enabled in UI, OR
- [ ] Environment variable: `USE_PATHWAY=true`

To verify:
- [ ] Run `python3 validate_pathway.py` (should pass)
- [ ] UI shows "🔄 Real-time streaming enabled"
- [ ] Console shows "Using Pathway streaming pipeline"

---

**Ready to run!** 🎉

Start with: `streamlit run app.py` and enable Pathway in the UI.
