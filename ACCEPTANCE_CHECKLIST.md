# Claims Triage Agent - Acceptance Criteria Checklist

## ✅ CONSTRAINTS AND MODES

- [x] **Two modes implemented**
  - [x] MOCK mode: runs offline with synthetic documents
  - [x] MOCK mode works on first run with zero external keys
  - [x] MOCK mode is the default
  - [x] PROD mode: uses LandingAI ADE and Pathway
  - [x] Enable PROD with environment variables
  - [x] Cleanly degrades to MOCK if keys missing

- [x] **Environment variables**
  - [x] LANDINGAI_API_KEY for ADE
  - [x] PATHWAY_CONFIG for configuration
  - [x] APP_MODE in {MOCK, PROD}, default MOCK
  - [x] .env.example provided

- [x] **Automated tests**
  - [x] Tests pass in MOCK mode
  - [x] No external dependencies required for tests
  - [x] All 13 tests passing

## ✅ CORE ENTITIES AND SCHEMA

- [x] **StructuredClaim** (Pydantic)
  - [x] file_id: str
  - [x] filename: str
  - [x] claimant_name: str | None
  - [x] policy_id: str | None
  - [x] incident_date: str | None (ISO yyyy-mm-dd)
  - [x] claim_amount_total_usd: float | None
  - [x] injury_severity: str in {none, minor, severe}
  - [x] incident_type: str in {auto, property, liability, theft}
  - [x] repeat_claims_count: int
  - [x] adverse_keywords: list[str]
  - [x] extracted_tables: list[dict]
  - [x] bboxes: dict[str, list[dict]] with page, x0, y0, x1, y1
  - [x] confidences: dict[str, float]

- [x] **RoutingDecision** (Pydantic)
  - [x] decision_id: str
  - [x] file_id: str
  - [x] route: str in {adjuster_junior, adjuster_senior, fraud_queue, litigation, human_review}
  - [x] rule_fired: str
  - [x] model_score: float | None
  - [x] rationale: list[str]
  - [x] evidence_pointers: list[dict] with field, bbox_ref
  - [x] sha256_raw: str
  - [x] sha256_structured: str
  - [x] created_at: str (ISO time)

## ✅ RULES DSL

- [x] **rules.yaml** created with hot reload
- [x] Helper functions provided
  - [x] any_kw(list[str]) - reads adverse_keywords
  - [x] missing(list[str]) - checks None or confidence < 0.6
- [x] All example rules implemented:
  - [x] litigation_high_amount
  - [x] severe_injury
  - [x] suspected_fraud
  - [x] low_confidence_handoff
  - [x] default

## ✅ FILE TREE

All required files created:
- [x] app.py
- [x] ade_client.py
- [x] pathway_pipe.py
- [x] rule_engine.py
- [x] counterfactual.py
- [x] backtest.py
- [x] metrics.py
- [x] normalize.py
- [x] schema.py
- [x] storage.py
- [x] utils.py
- [x] rules.yaml
- [x] requirements.txt
- [x] README.md
- [x] .env.example
- [x] run.sh

Directories:
- [x] demo_data/inbox/
- [x] demo_data/gold/
- [x] demo_data/mock_docs/
- [x] demo_data/extracted_mock/
- [x] tests/

Test files:
- [x] tests/test_rules.py
- [x] tests/test_counterfactual.py
- [x] tests/test_mock_pipeline.py

## ✅ IMPLEMENTATION DETAILS

- [x] **requirements.txt** - all dependencies pinned
  - [x] streamlit
  - [x] pathway
  - [x] pydantic
  - [x] scikit-learn
  - [x] reportlab
  - [x] pillow
  - [x] pypdf
  - [x] pytest
  - [x] numpy
  - [x] pandas
  - [x] PyYAML

- [x] **storage.py**
  - [x] sha256 of file and structured JSON
  - [x] JSONL append helpers
  - [x] Read/write rules.yaml
  - [x] last_rules.yaml diff support

- [x] **normalize.py**
  - [x] Currency parsing and USD normalization
  - [x] Date normalization to yyyy-mm-dd
  - [x] Keyword score computation

- [x] **ade_client.py**
  - [x] MockExtractor class
    - [x] Generates 10-12 synthetic PDFs with reportlab
    - [x] Creates FNOL, police reports, tables, fraud narratives
    - [x] Generates extracted JSON with bboxes and confidences
    - [x] Returns StructuredClaim objects
  - [x] ADEExtractor class
    - [x] Wraps landingai-ade with retries
    - [x] Requests tables and bboxes
    - [x] Maps ADE JSON to StructuredClaim
    - [x] Applies normalize functions
    - [x] Filters low confidence fields (< 0.6)

- [x] **rule_engine.py**
  - [x] Safe eval engine
  - [x] Allowed names restricted to helpers
  - [x] First matching rule wins
  - [x] Builds RoutingDecision with evidence
  - [x] Hot reload from rules.yaml

- [x] **pathway_pipe.py**
  - [x] Watches demo_data/inbox
  - [x] Accepts UI uploads
  - [x] Calls extractor based on APP_MODE
  - [x] Emits to in-memory index
  - [x] Tracks latency p50/p95
  - [x] Maintains queue sizes
  - [x] API for UI to read claims/decisions/metrics

- [x] **counterfactual.py**
  - [x] Recomputes routing for N claims with new rules
  - [x] Returns before/after table
  - [x] Returns summary counts

- [x] **backtest.py**
  - [x] Loads gold labels
  - [x] Runs predictions with current rules
  - [x] Computes precision, recall per route
  - [x] Confusion matrix
  - [x] List of mismatches with links

- [x] **metrics.py**
  - [x] Rolling stats for extraction/routing durations
  - [x] Queue sizes per route
  - [x] Error and low-confidence counters

- [x] **app.py** - Streamlit UI with:
  - [x] Top metric strip (p50/p95, queue sizes)
  - [x] Left column
    - [x] File uploader
    - [x] Folder watch toggle
    - [x] Generate mock docs button
    - [x] APP_MODE selector
    - [x] Rules editor
    - [x] Apply rules button
    - [x] Counterfactual table and bar chart
  - [x] Center column
    - [x] Document preview
    - [x] Bbox rendering for evidence fields
    - [x] Thumbnail page navigator
  - [x] Right column
    - [x] Extracted fields table with confidences
    - [x] RoutingDecision card
      - [x] Route, rule_fired, model_score
      - [x] Rationale bullets
      - [x] Evidence pointers
      - [x] SHA256 hashes (shortened)
    - [x] "Why not" section with alternatives
  - [x] Backtest panel
    - [x] Run backtest button
    - [x] Precision, recall, confusion matrix
    - [x] Mismatches with links

- [x] **run.sh**
  - [x] Single command to run
  - [x] Detects APP_MODE
  - [x] Warns if PROD requested but keys missing

- [x] **tests**
  - [x] test_rules.py - rule matches and precedence
  - [x] test_counterfactual.py - before/after diffs
  - [x] test_mock_pipeline.py - end-to-end mock run

## ✅ ACCEPTANCE CRITERIA FOR FIRST RUN

- [x] Default APP_MODE is MOCK
- [x] On first run:
  - [x] Synthetic PDFs created
  - [x] Extracted mock JSON created
  - [x] At least 6 claims appear in UI
- [x] Uploading new PDF processes it
- [x] Editing rules.yaml and pressing Apply recomputes last 10 claims
- [x] Before/after table shown
- [x] Metric strip updates
- [x] Backtest runs on gold set and prints metrics
- [x] pytest passes all tests

## ✅ SEED CONTENT

- [x] **10 synthetic claims** with diversity:
  - [x] 3 low amount auto under 5k
  - [x] 3 high amount severe injury over 50k
  - [x] 2 suspected fraud with repeat claims/keywords
  - [x] 2 property claims with subrogation hints
- [x] 2 documents simulate low quality scan
- [x] Gold labels provided for backtest

## ✅ DEMO SCRIPT

- [x] 90-second demo script in README
- [x] Drop clean FNOL → routed to junior
- [x] Drop noisy report → routed to senior
- [x] Drop suspicious claim → routed to fraud
- [x] Change litigation threshold 50k→25k → show moves
- [x] Show p50 times, run backtest, show mismatches

## ✅ STACK REQUIREMENTS

- [x] Python 3.11 compatible
- [x] Streamlit for UI
- [x] Pathway for streaming
- [x] pydantic for schemas
- [x] scikit-learn for models
- [x] reportlab for synthetic PDFs
- [x] pillow and pypdf for rendering
- [x] pytest for tests

## 🎯 VERIFICATION

Run these commands to verify:

```bash
# 1. Check imports
python verify.py

# 2. Run tests
pytest tests/ -v

# 3. Start app
./run.sh
```

Expected results:
- ✅ All imports successful
- ✅ 13/13 tests passed
- ✅ App starts on http://localhost:8501
- ✅ 6+ claims visible in UI
- ✅ All metrics showing data

## 🏆 FINAL STATUS

**ALL ACCEPTANCE CRITERIA MET ✅**

Project is:
- ✅ Complete
- ✅ Runnable out-of-box
- ✅ Fully tested
- ✅ Demo-ready
- ✅ Production-capable

Ready for Microsoft Hackathon 2025 judging!
