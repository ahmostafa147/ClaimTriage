"""Streamlit UI for Claims Triage Agent."""
import os
import streamlit as st
from pathlib import Path
import shutil
import pandas as pd

from pathway_pipe import get_pipeline, reset_pipeline
from counterfactual import CounterfactualAnalyzer
from backtest import Backtester
from schema import StructuredClaim, RoutingDecision


# Page config
st.set_page_config(
    page_title="Claims Triage Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "app_mode" not in st.session_state:
    st.session_state.app_mode = os.getenv("APP_MODE", "MOCK")
if "pipeline_initialized" not in st.session_state:
    st.session_state.pipeline_initialized = False
if "selected_claim_id" not in st.session_state:
    st.session_state.selected_claim_id = None
if "rules_content" not in st.session_state:
    rules_path = Path("rules.yaml")
    if rules_path.exists():
        with open(rules_path) as f:
            st.session_state.rules_content = f.read()
    else:
        st.session_state.rules_content = ""


def initialize_pipeline():
    """Initialize pipeline and load data."""
    pipeline = get_pipeline(st.session_state.app_mode)

    if not st.session_state.pipeline_initialized:
        # Initialize mock data if needed
        pipeline.initialize_mock_data()

        # Process inbox
        pipeline.process_inbox()

        st.session_state.pipeline_initialized = True

    return pipeline


def main():
    """Main application."""
    st.title("📋 Claims Triage Agent")
    st.markdown("**Intelligent claim routing with transparent proofs and live metrics**")

    # Initialize pipeline
    pipeline = initialize_pipeline()

    # Top metrics strip
    st.markdown("---")
    metrics = pipeline.get_metrics()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Extraction P50", f"{metrics['extraction']['p50']:.2f}s")
    with col2:
        st.metric("Extraction P95", f"{metrics['extraction']['p95']:.2f}s")
    with col3:
        st.metric("Routing P50", f"{metrics['routing']['p50']*1000:.1f}ms")
    with col4:
        st.metric("Routing P95", f"{metrics['routing']['p95']*1000:.1f}ms")
    with col5:
        total_claims = len(pipeline.get_claims())
        st.metric("Total Claims", total_claims)
    with col6:
        queues = metrics["queues"]
        st.metric("Queues", len(queues))

    # Queue sizes
    if queues:
        queue_cols = st.columns(len(queues))
        for i, (route, size) in enumerate(queues.items()):
            with queue_cols[i]:
                st.metric(route.replace("_", " ").title(), size)

    st.markdown("---")

    # Main layout
    left_col, center_col, right_col = st.columns([1, 2, 1])

    # LEFT COLUMN - Controls
    with left_col:
        st.subheader("Controls")

        # File uploader
        uploaded_file = st.file_uploader("Upload Claim PDF", type=["pdf"])
        if uploaded_file:
            # Save to inbox
            inbox_path = Path("demo_data/inbox") / uploaded_file.name
            with open(inbox_path, "wb") as f:
                f.write(uploaded_file.read())

            # Process
            result = pipeline.process_file(inbox_path)
            if result:
                st.success(f"Processed: {uploaded_file.name}")
                st.session_state.selected_claim_id = result[0].file_id
                st.rerun()

        # Generate mock docs
        if st.button("Generate Mock Documents"):
            from ade_client import MockExtractor
            extractor = MockExtractor()
            files = extractor.generate_synthetic_claims()
            st.success(f"Generated {len(files)} mock documents")

        # Mode selector
        new_mode = st.selectbox("App Mode", ["MOCK", "PROD"], index=0 if st.session_state.app_mode == "MOCK" else 1)
        if new_mode != st.session_state.app_mode:
            st.session_state.app_mode = new_mode
            st.session_state.pipeline_initialized = False
            reset_pipeline()
            st.rerun()

        # Process inbox button
        if st.button("Process Inbox"):
            results = pipeline.process_inbox()
            st.success(f"Processed {len(results)} files")
            st.rerun()

        st.markdown("---")

        # Rules editor
        st.subheader("Rules Editor")

        rules_editor = st.text_area(
            "Edit rules.yaml",
            value=st.session_state.rules_content,
            height=300,
            key="rules_editor"
        )

        if st.button("Apply Rules & Recompute"):
            # Save rules
            with open("rules.yaml", "w") as f:
                f.write(rules_editor)
            st.session_state.rules_content = rules_editor

            # Reload rules
            pipeline.reload_rules()

            # Counterfactual analysis
            recent_claims = pipeline.get_recent_claims(10)
            if recent_claims:
                analyzer = CounterfactualAnalyzer()
                result = analyzer.analyze(recent_claims, rules_editor)

                st.subheader("Counterfactual Analysis")
                st.write(f"**Changes:** {result['changed_count']} / {result['total_claims']}")

                if result["changes"]:
                    df = pd.DataFrame(result["changes"])
                    st.dataframe(df[["filename", "from_route", "to_route", "new_rule"]])

                    # Bar chart
                    moved_counts = {}
                    for change in result["changes"]:
                        key = f"{change['from_route']} → {change['to_route']}"
                        moved_counts[key] = moved_counts.get(key, 0) + 1

                    if moved_counts:
                        st.bar_chart(pd.DataFrame(list(moved_counts.items()), columns=["Route Change", "Count"]).set_index("Route Change"))

            st.success("Rules applied and claims recomputed!")

    # CENTER COLUMN - Document viewer
    with center_col:
        st.subheader("Document Viewer")

        claims = pipeline.get_claims()
        if not claims:
            st.info("No claims processed yet. Upload a PDF or process the inbox.")
        else:
            # Claim selector
            claim_options = {f"{c.filename} ({c.file_id[:8]})": c.file_id for c in claims}
            selected_display = st.selectbox("Select Claim", list(claim_options.keys()))
            selected_id = claim_options[selected_display]

            if selected_id:
                st.session_state.selected_claim_id = selected_id

                claim = pipeline.get_claim_by_id(selected_id)
                decision = pipeline.get_decision_by_id(selected_id)

                if claim:
                    # Show PDF preview
                    pdf_path = None

                    # Try to find PDF
                    possible_paths = [
                        Path("demo_data/inbox") / claim.filename,
                        Path("demo_data/mock_docs") / claim.filename
                    ]

                    for path in possible_paths:
                        if path.exists():
                            pdf_path = path
                            break

                    if pdf_path:
                        # Display PDF info
                        st.write(f"**File:** {claim.filename}")

                        # Show bboxes used in decision
                        if decision:
                            st.write(f"**Route:** {decision.route}")
                            st.write(f"**Rule:** {decision.rule_fired}")

                            # Show evidence
                            if decision.evidence_pointers:
                                st.write("**Evidence fields:**")
                                evidence_fields = [e["field"] for e in decision.evidence_pointers]
                                st.write(", ".join(set(evidence_fields)))

                        # PDF rendering would go here
                        st.info("PDF preview: Install pdf2image for page rendering")

                    else:
                        st.warning("PDF file not found")

    # RIGHT COLUMN - Extracted fields and decision
    with right_col:
        st.subheader("Claim Details")

        if st.session_state.selected_claim_id:
            claim = pipeline.get_claim_by_id(st.session_state.selected_claim_id)
            decision = pipeline.get_decision_by_id(st.session_state.selected_claim_id)

            if claim:
                # Extracted fields
                st.markdown("**Extracted Fields**")

                fields_data = {
                    "Claimant": claim.claimant_name or "N/A",
                    "Policy ID": claim.policy_id or "N/A",
                    "Date": claim.incident_date or "N/A",
                    "Amount": f"${claim.claim_amount_total_usd:,.0f}" if claim.claim_amount_total_usd else "N/A",
                    "Injury": claim.injury_severity,
                    "Type": claim.incident_type,
                    "Repeat Claims": str(claim.repeat_claims_count)
                }

                for field, value in fields_data.items():
                    conf = claim.confidences.get(field.lower().replace(" ", "_"), None)
                    conf_str = f" ({conf:.0%})" if conf else ""
                    st.text(f"{field}: {value}{conf_str}")

                if claim.adverse_keywords:
                    st.markdown("**Adverse Keywords:**")
                    st.write(", ".join(claim.adverse_keywords))

                st.markdown("---")

                # Routing decision
                if decision:
                    st.markdown("**Routing Decision**")

                    # Route badge
                    route_color = {
                        "adjuster_junior": "🟢",
                        "adjuster_senior": "🟡",
                        "fraud_queue": "🔴",
                        "litigation": "🟠",
                        "human_review": "⚪"
                    }.get(decision.route, "⚪")

                    st.markdown(f"### {route_color} {decision.route.replace('_', ' ').title()}")

                    st.write(f"**Rule:** {decision.rule_fired}")

                    if decision.model_score is not None:
                        st.write(f"**Model Score:** {decision.model_score:.3f}")

                    if decision.rationale:
                        st.markdown("**Rationale:**")
                        for r in decision.rationale:
                            st.write(f"- {r}")

                    if decision.evidence_pointers:
                        st.markdown("**Evidence:**")
                        for ev in decision.evidence_pointers[:3]:
                            st.write(f"- {ev['field']} (page {ev['page']})")

                    # Hashes
                    st.markdown("**Chain of Custody:**")
                    st.text(f"Raw: {decision.sha256_raw[:16]}...")
                    st.text(f"Structured: {decision.sha256_structured[:16]}...")
                    st.text(f"Created: {decision.created_at}")

                    st.markdown("---")

                    # Why not section
                    st.markdown("**Why Not?**")
                    alternatives = pipeline.rule_engine.get_alternative_routes(claim)

                    for alt in alternatives[:3]:
                        st.write(f"❌ **{alt['route']}**: {alt['reason']}")

        else:
            st.info("Select a claim to view details")

    # BOTTOM PANEL - Backtest
    st.markdown("---")
    st.subheader("Backtest")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("Run Backtest"):
            backtester = Backtester()
            claims = pipeline.get_claims()
            decisions = pipeline.get_decisions()

            results = backtester.run_backtest(claims, decisions)

            st.session_state.backtest_results = results

    with col2:
        if "backtest_results" in st.session_state:
            results = st.session_state.backtest_results
            metrics = results["metrics"]

            # Metrics
            st.write(f"**Accuracy:** {metrics['overall_accuracy']:.1%} ({metrics['correct']}/{metrics['total_predictions']})")

            # Per-route metrics
            if metrics["by_route"]:
                df = pd.DataFrame(metrics["by_route"]).T
                st.dataframe(df)

            # Confusion matrix
            if results["confusion_matrix"]:
                st.markdown("**Confusion Matrix:**")
                st.json(results["confusion_matrix"])

            # Mismatches
            if results["mismatches"]:
                st.markdown(f"**Mismatches ({len(results['mismatches'])}):**")
                mismatch_df = pd.DataFrame(results["mismatches"])
                st.dataframe(mismatch_df[["filename", "expected", "actual", "rule_fired"]])


if __name__ == "__main__":
    main()
