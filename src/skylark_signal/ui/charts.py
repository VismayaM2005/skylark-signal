import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Any

# ── Consistent Dark Theme for all charts ──────────────────────
_BG = "rgba(10,20,34,0)"      # transparent — app background shows through
_GRID = "rgba(56,189,248,0.06)"
_FONT_COLOR = "#94A3B8"
_TITLE_COLOR = "#E2E8F0"

PLOTLY_LAYOUT_DEFAULTS = dict(
    paper_bgcolor=_BG,
    plot_bgcolor=_BG,
    font=dict(color=_FONT_COLOR, family="Inter, -apple-system, sans-serif", size=12),
    title_font=dict(color=_TITLE_COLOR, size=14, family="Inter, sans-serif"),
    margin=dict(l=20, r=20, t=48, b=20),
    xaxis=dict(
        gridcolor=_GRID,
        zerolinecolor=_GRID,
        linecolor="rgba(56,189,248,0.08)",
        tickfont=dict(color=_FONT_COLOR, size=11),
    ),
    yaxis=dict(
        gridcolor=_GRID,
        zerolinecolor=_GRID,
        linecolor="rgba(56,189,248,0.08)",
        tickfont=dict(color=_FONT_COLOR, size=11),
    ),
    legend=dict(
        bgcolor="rgba(10,20,34,0.4)",
        bordercolor="rgba(56,189,248,0.1)",
        borderwidth=1,
        font=dict(color=_FONT_COLOR, size=11),
    ),
)

# Premium chart color palettes
_PALETTE_BLUE = ["#0EA5E9", "#38BDF8", "#7DD3FC", "#BAE6FD", "#0284C7"]
_PALETTE_RISK = ["#EF4444", "#F59E0B", "#3B82F6"]
_PALETTE_SECTOR = px.colors.sequential.Blues_r


def create_pipeline_by_stage_chart(deals: List[Any]) -> go.Figure:
    """Generates a premium horizontal bar chart of open pipeline value by stage."""
    stages: dict = {}
    for d in deals:
        stg = str(getattr(d, "stage", "Unknown") or "Unknown").strip()
        if "Closed" not in stg:
            val = float(getattr(d, "deal_value", 0.0) or 0.0)
            stages[stg] = stages.get(stg, 0.0) + val

    df = pd.DataFrame([{"Stage": k, "Pipeline Value (₹)": v} for k, v in stages.items()])
    if df.empty:
        df = pd.DataFrame([{"Stage": "Open Pipeline", "Pipeline Value (₹)": 0.0}])

    df = df.sort_values(by="Pipeline Value (₹)", ascending=True)
    df["Pipeline (₹ Cr)"] = (df["Pipeline Value (₹)"] / 1e7).round(2)

    # Build colored bars (gradient from lighter to darker blue by rank)
    n = len(df)
    colors = [_PALETTE_BLUE[i % len(_PALETTE_BLUE)] for i in range(n)]

    fig = go.Figure(
        go.Bar(
            x=df["Pipeline Value (₹)"],
            y=df["Stage"],
            orientation="h",
            marker=dict(
                color=df["Pipeline Value (₹)"],
                colorscale=[[0, "#0F2240"], [0.5, "#0284C7"], [1, "#38BDF8"]],
                line=dict(color="rgba(56,189,248,0.2)", width=1),
            ),
            text=[f"₹{v/1e7:.1f} Cr" for v in df["Pipeline Value (₹)"]],
            textposition="outside",
            textfont=dict(color="#E2E8F0", size=11),
            hovertemplate="<b>%{y}</b><br>Pipeline: ₹%{x:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Open Pipeline Value by Stage",
        **PLOTLY_LAYOUT_DEFAULTS,
    )
    fig.update_xaxes(showticklabels=False, showgrid=False)
    return fig


def create_revenue_at_risk_donut(risk_breakdown: dict) -> go.Figure:
    """Generates a premium donut chart of revenue at risk by category."""
    label_map = {
        "overdue_active_work_orders": "Overdue Work Orders",
        "stale_late_stage_deals": "Stale Late-Stage Deals",
        "high_value_missing_prob": "Missing Probability Deals",
    }

    labels = []
    values = []
    for k, v in risk_breakdown.items():
        if v > 0:
            labels.append(label_map.get(k, k))
            values.append(v)

    if not values:
        labels = ["No Active Risk Items"]
        values = [1.0]
        colors = ["rgba(56,189,248,0.15)"]
    else:
        colors = _PALETTE_RISK[: len(values)]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker=dict(
                colors=colors,
                line=dict(color="#060B14", width=3),
            ),
            textposition="inside",
            textinfo="percent+label",
            textfont=dict(color="#F0F8FF", size=11),
            hovertemplate="<b>%{label}</b><br>Risk Exposure: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>",
        )
    )

    # Center annotation
    total_risk = sum(values)
    fig.add_annotation(
        text=f"₹{total_risk/1e7:.1f}Cr<br><span style='font-size:10px; color:#64748B;'>Total Risk</span>",
        x=0.5, y=0.5,
        font=dict(size=16, color="#F0F8FF", family="Inter, sans-serif"),
        showarrow=False,
    )

    layout = dict(**PLOTLY_LAYOUT_DEFAULTS)
    layout["title"] = "Revenue at Risk Categories"
    layout.pop("xaxis", None)
    layout.pop("yaxis", None)
    layout["legend"] = dict(
        orientation="v",
        x=1.0, y=0.5,
        bgcolor="rgba(10,20,34,0.4)",
        bordercolor="rgba(56,189,248,0.1)",
        borderwidth=1,
        font=dict(color=_FONT_COLOR, size=11),
    )
    fig.update_layout(**layout)
    return fig


def create_sector_matrix_chart(deals: List[Any], work_orders: List[Any]) -> go.Figure:
    """Generates a premium grouped bar chart: sector pipeline vs active operations."""
    sectors: dict = {}

    for d in deals:
        sec = getattr(d, "sector", "Unassigned") or "Unassigned"
        if sec not in sectors:
            sectors[sec] = {"Pipeline": 0.0, "Active Work Orders": 0}
        stg = str(getattr(d, "stage", "") or "").strip()
        if "Closed" not in stg:
            val = float(getattr(d, "deal_value", 0.0) or 0.0)
            sectors[sec]["Pipeline"] += val

    for w in work_orders:
        sec = getattr(w, "sector", "Unassigned") or "Unassigned"
        if sec not in sectors:
            sectors[sec] = {"Pipeline": 0.0, "Active Work Orders": 0}
        w_st = str(getattr(w, "completion_status", getattr(w, "status", "")) or "").strip()
        if "Completed" not in w_st:
            sectors[sec]["Active Work Orders"] += 1

    df_rows = [
        {
            "Sector": s,
            "Pipeline (₹ Cr)": round(data["Pipeline"] / 1e7, 2),
            "Active Projects": data["Active Work Orders"],
        }
        for s, data in sectors.items()
    ]
    df = pd.DataFrame(df_rows) if df_rows else pd.DataFrame([{"Sector": "General", "Pipeline (₹ Cr)": 0.0, "Active Projects": 0}])

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Pipeline (₹ Cr)",
            x=df["Sector"],
            y=df["Pipeline (₹ Cr)"],
            marker=dict(
                color="#0EA5E9",
                opacity=0.85,
                line=dict(color="rgba(56,189,248,0.3)", width=1),
            ),
            text=[f"₹{v:.1f}Cr" for v in df["Pipeline (₹ Cr)"]],
            textposition="outside",
            textfont=dict(color="#E2E8F0", size=11),
            hovertemplate="<b>%{x}</b><br>Pipeline: ₹%{y:.2f} Cr<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            name="Active Projects",
            x=df["Sector"],
            y=df["Active Projects"],
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#F59E0B", width=2, dash="dot"),
            marker=dict(color="#F59E0B", size=8, symbol="circle", line=dict(color="#0A1628", width=2)),
            hovertemplate="<b>%{x}</b><br>Active Projects: %{y}<extra></extra>",
        )
    )

    layout = dict(**PLOTLY_LAYOUT_DEFAULTS)
    layout["title"] = "Sector Pipeline Value vs Active Operations"
    layout["barmode"] = "group"
    layout["yaxis"] = dict(
        title=dict(text="Pipeline (₹ Cr)", font=dict(color=_FONT_COLOR, size=12)),
        gridcolor=_GRID,
        zerolinecolor=_GRID,
        tickfont=dict(color=_FONT_COLOR, size=11),
    )
    layout["yaxis2"] = dict(
        title=dict(text="Active Projects", font=dict(color="#F59E0B", size=12)),
        overlaying="y",
        side="right",
        gridcolor="rgba(0,0,0,0)",
        tickfont=dict(color="#F59E0B", size=11),
    )
    layout["margin"] = dict(l=20, r=60, t=48, b=20)
    fig.update_layout(**layout)
    return fig
