import streamlit as st

CUSTOM_CSS = """
<style>
/* ============================================================
   SKYLARK SIGNAL — Premium Executive Intelligence Platform
   Design System v3.0 — Dark SaaS / Boardroom-Grade
   ============================================================ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Remove Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* App background */
.stApp {
    background: #060B14;
}

/* Main content area */
section[data-testid="stSidebar"] {
    background: #0A1628 !important;
    border-right: 1px solid rgba(56, 189, 248, 0.08) !important;
}

/* ── Hero Section ─────────────────────────────────────────── */
.hero-container {
    position: relative;
    background: linear-gradient(135deg, #0D1B2E 0%, #0F2240 40%, #0A1628 100%);
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 20px;
    padding: 36px 40px 28px 40px;
    margin-bottom: 28px;
    overflow: hidden;
    box-shadow:
        0 0 0 1px rgba(56, 189, 248, 0.05),
        0 25px 50px -12px rgba(0, 0, 0, 0.6),
        inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.hero-container::before {
    content: '';
    position: absolute;
    top: -60px;
    right: -40px;
    width: 300px;
    height: 300px;
    background: radial-gradient(ellipse, rgba(56, 189, 248, 0.06) 0%, transparent 70%);
    pointer-events: none;
}

.hero-container::after {
    content: '';
    position: absolute;
    bottom: -40px;
    left: 20%;
    width: 200px;
    height: 200px;
    background: radial-gradient(ellipse, rgba(99, 102, 241, 0.05) 0%, transparent 70%);
    pointer-events: none;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 100px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: 600;
    color: #38BDF8;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.hero-wordmark {
    font-size: 34px;
    font-weight: 800;
    color: #F0F8FF;
    letter-spacing: -1.2px;
    margin-bottom: 6px;
    line-height: 1.1;
}

.hero-wordmark .accent {
    background: linear-gradient(90deg, #38BDF8, #818CF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-tagline {
    font-size: 14px;
    font-weight: 400;
    color: #64748B;
    margin-bottom: 20px;
    max-width: 540px;
    line-height: 1.6;
}

.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
}

/* ── Status Pills ─────────────────────────────────────────── */
.pill-live {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #34D399;
    padding: 5px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

.pill-live::before {
    content: '';
    width: 7px;
    height: 7px;
    background: #34D399;
    border-radius: 50%;
    box-shadow: 0 0 6px #34D399;
    animation: pulse-dot 2s ease-in-out infinite;
}

.pill-fallback {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.25);
    color: #FBBF24;
    padding: 5px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
}

.pill-trust {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.25);
    color: #A5B4FC;
    padding: 5px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
}

.pill-provider {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(148, 163, 184, 0.06);
    border: 1px solid rgba(148, 163, 184, 0.15);
    color: #94A3B8;
    padding: 5px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 500;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px #34D399; }
    50% { opacity: 0.6; box-shadow: 0 0 12px #34D399; }
}

/* ── Section Headers ─────────────────────────────────────── */
.view-header {
    display: flex;
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(56, 189, 248, 0.08);
}

.view-title {
    font-size: 22px;
    font-weight: 700;
    color: #F0F8FF;
    letter-spacing: -0.5px;
    margin: 0;
}

.view-subtitle {
    font-size: 13px;
    color: #475569;
    font-weight: 400;
    margin: 0;
}

/* ── Premium Cards ─────────────────────────────────────────  */
.saas-card {
    background: linear-gradient(145deg, #0F1C2E, #0A1628);
    border: 1px solid rgba(56, 189, 248, 0.1);
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.03);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.saas-card:hover {
    border-color: rgba(56, 189, 248, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(56, 189, 248, 0.05);
}

.card-kpi {
    background: linear-gradient(145deg, #0D1B2E, #0A1422);
    border: 1px solid rgba(56, 189, 248, 0.08);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}

.card-win {
    background: linear-gradient(145deg, rgba(16, 185, 129, 0.06), rgba(6, 95, 70, 0.04));
    border: 1px solid rgba(16, 185, 129, 0.15);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 14px;
}

.card-risk {
    background: linear-gradient(145deg, rgba(239, 68, 68, 0.06), rgba(127, 29, 29, 0.04));
    border: 1px solid rgba(239, 68, 68, 0.15);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 14px;
}

.card-info {
    background: linear-gradient(145deg, rgba(56, 189, 248, 0.05), rgba(14, 116, 144, 0.03));
    border: 1px solid rgba(56, 189, 248, 0.12);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
}

.card-clarification {
    background: linear-gradient(145deg, rgba(245, 158, 11, 0.08), rgba(120, 53, 15, 0.06));
    border: 1px solid rgba(245, 158, 11, 0.2);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 14px;
}

/* ── Metric Cards ─────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #0F1C2E, #0A1422);
    border: 1px solid rgba(56, 189, 248, 0.08);
    border-radius: 14px;
    padding: 18px 20px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.03);
    transition: border-color 0.25s ease, transform 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    border-color: rgba(56, 189, 248, 0.22);
    transform: translateY(-2px);
}

div[data-testid="stMetricLabel"] > div {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}

div[data-testid="stMetricValue"] > div {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #F0F8FF !important;
    letter-spacing: -0.5px !important;
}

div[data-testid="stMetricDelta"] > div {
    font-size: 12px !important;
    font-weight: 500 !important;
}

/* ── Priority Badges ─────────────────────────────────────── */
.badge-p1 {
    background: rgba(127, 29, 29, 0.4);
    color: #FCA5A5;
    border: 1px solid rgba(239, 68, 68, 0.3);
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.badge-p2 {
    background: rgba(120, 53, 15, 0.4);
    color: #FDE68A;
    border: 1px solid rgba(245, 158, 11, 0.3);
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.badge-p3 {
    background: rgba(30, 58, 138, 0.4);
    color: #93C5FD;
    border: 1px solid rgba(59, 130, 246, 0.3);
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.badge-p4 {
    background: rgba(20, 83, 45, 0.4);
    color: #86EFAC;
    border: 1px solid rgba(34, 197, 94, 0.3);
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Status Badges (Health) ─────────────────────────────── */
.status-green {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #34D399;
    padding: 6px 18px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.status-amber {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.25);
    color: #FBBF24;
    padding: 6px 18px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.status-red {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.25);
    color: #F87171;
    padding: 6px 18px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* ── Attention Queue Cards ──────────────────────────────── */
.attention-card {
    background: linear-gradient(145deg, #0F1C2E, #0A1628);
    border: 1px solid rgba(56, 189, 248, 0.08);
    border-left: 3px solid rgba(56, 189, 248, 0.3);
    border-radius: 0 14px 14px 0;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s ease;
}

.attention-card.p1 {
    border-left-color: #EF4444;
    background: linear-gradient(145deg, rgba(127, 29, 29, 0.06), #0A1628);
}

.attention-card.p2 {
    border-left-color: #F59E0B;
    background: linear-gradient(145deg, rgba(120, 53, 15, 0.06), #0A1628);
}

.attention-card.p3 {
    border-left-color: #3B82F6;
}

.attention-card.p4 {
    border-left-color: #22C55E;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    background: rgba(56, 189, 248, 0.08) !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    color: #38BDF8 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: rgba(56, 189, 248, 0.15) !important;
    border-color: rgba(56, 189, 248, 0.4) !important;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.12) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Primary / action button override for download */
.stDownloadButton > button {
    background: rgba(99, 102, 241, 0.1) !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    color: #A5B4FC !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
}

.stDownloadButton > button:hover {
    background: rgba(99, 102, 241, 0.18) !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
}

/* ── Form Inputs ─────────────────────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div > div > div {
    background: #0A1628 !important;
    border: 1px solid rgba(56, 189, 248, 0.12) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
}

.stTextInput > div > div > input:focus {
    border-color: rgba(56, 189, 248, 0.35) !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.06) !important;
}

textarea {
    background: #0A1628 !important;
    border: 1px solid rgba(56, 189, 248, 0.12) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
}

/* ── Tabs / Radio Nav ─────────────────────────────────────  */
.stRadio > label {
    color: #64748B !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}

/* ── Expanders ───────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: rgba(15, 28, 46, 0.5) !important;
    border: 1px solid rgba(56, 189, 248, 0.08) !important;
    border-radius: 10px !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

.streamlit-expanderContent {
    background: rgba(10, 22, 40, 0.5) !important;
    border: 1px solid rgba(56, 189, 248, 0.06) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── Alerts / Info ───────────────────────────────────────── */
.stAlert {
    border-radius: 12px !important;
}

div[data-testid="stInfo"] {
    background: rgba(56, 189, 248, 0.06) !important;
    border: 1px solid rgba(56, 189, 248, 0.15) !important;
    border-radius: 12px !important;
    color: #BAE6FD !important;
}

div[data-testid="stWarning"] {
    background: rgba(245, 158, 11, 0.08) !important;
    border: 1px solid rgba(245, 158, 11, 0.2) !important;
    border-radius: 12px !important;
    color: #FDE68A !important;
}

div[data-testid="stSuccess"] {
    background: rgba(16, 185, 129, 0.08) !important;
    border: 1px solid rgba(16, 185, 129, 0.2) !important;
    border-radius: 12px !important;
    color: #A7F3D0 !important;
}

div[data-testid="stError"] {
    background: rgba(239, 68, 68, 0.08) !important;
    border: 1px solid rgba(239, 68, 68, 0.2) !important;
    border-radius: 12px !important;
    color: #FCA5A5 !important;
}

/* ── DataFrames ──────────────────────────────────────────── */
.dataframe {
    background: #0A1422 !important;
    border: 1px solid rgba(56, 189, 248, 0.08) !important;
    border-radius: 12px !important;
}

/* ── Sidebar Elements ────────────────────────────────────── */
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] div {
    color: #94A3B8 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #E2E8F0 !important;
}

/* ── Divider ─────────────────────────────────────────────── */
hr {
    border-color: rgba(56, 189, 248, 0.07) !important;
    margin: 18px 0 !important;
}

/* ── Trust Badge ─────────────────────────────────────────── */
.trust-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(99, 102, 241, 0.08);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    color: #A5B4FC;
}

.trust-bar-track {
    background: rgba(99, 102, 241, 0.15);
    border-radius: 4px;
    height: 4px;
    margin-top: 4px;
}

.trust-bar-fill {
    height: 4px;
    border-radius: 4px;
    background: linear-gradient(90deg, #6366F1, #38BDF8);
}

/* ── Code Blocks ─────────────────────────────────────────── */
code, pre {
    font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    background: rgba(10, 20, 34, 0.8) !important;
    border: 1px solid rgba(56, 189, 248, 0.08) !important;
    border-radius: 8px !important;
}

/* ── Caption / Small Text ────────────────────────────────── */
.stCaption > p,
small, caption {
    color: #475569 !important;
    font-size: 12px !important;
}

/* ── Spinner ─────────────────────────────────────────────── */
.stSpinner > div {
    border-top-color: #38BDF8 !important;
}

/* ── Executive Score Ring (decorative) ───────────────────── */
.score-ring-container {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 4px;
}

.score-value-large {
    font-size: 36px;
    font-weight: 800;
    color: #38BDF8;
    letter-spacing: -1.5px;
    line-height: 1;
}

.score-label-small {
    font-size: 11px;
    font-weight: 500;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ── Responsive Tweaks ───────────────────────────────────── */
@media (max-width: 768px) {
    .hero-container { padding: 22px 18px; }
    .hero-wordmark { font-size: 24px; }
}

/* ── Plotly Chart Background Override ────────────────────── */
.js-plotly-plot .plotly, .js-plotly-plot .plotly div {
    background: transparent !important;
}

</style>
"""


def inject_custom_styles():
    """Injects premium Skylark Signal SaaS dark-mode styles into Streamlit DOM."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
