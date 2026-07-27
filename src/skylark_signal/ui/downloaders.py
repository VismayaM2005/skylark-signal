import streamlit as st
from skylark_signal.reporting.export import (
    export_leadership_brief_markdown,
    export_attention_queue_csv,
    export_evidence_bundle_csv,
    export_analytics_snapshot_json
)

def render_download_buttons(bundle: dict):
    """Renders 4 export download buttons."""
    st.subheader("📥 Export Deliverables")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        md_text = export_leadership_brief_markdown(bundle)
        st.download_button(
            label="📄 Leadership Brief (.md)",
            data=md_text,
            file_name="leadership_brief.md",
            mime="text/markdown"
        )
        
    with col2:
        att_csv = export_attention_queue_csv(bundle)
        st.download_button(
            label="📊 Attention Queue (.csv)",
            data=att_csv,
            file_name="attention_queue.csv",
            mime="text/csv"
        )

    with col3:
        evi_csv = export_evidence_bundle_csv(bundle)
        st.download_button(
            label="🔍 Evidence Bundle (.csv)",
            data=evi_csv,
            file_name="evidence_bundle.csv",
            mime="text/csv"
        )

    with col4:
        snap_json = export_analytics_snapshot_json(bundle)
        st.download_button(
            label="📦 Analytics Snapshot (.json)",
            data=snap_json,
            file_name="analytics_snapshot.json",
            mime="application/json"
        )
