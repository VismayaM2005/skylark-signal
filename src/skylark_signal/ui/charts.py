import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

def create_pipeline_funnel_chart(pipeline_by_stage: Dict[str, float]) -> go.Figure:
    """Creates a bar chart of open pipeline by stage."""
    stages = list(pipeline_by_stage.keys())
    values = list(pipeline_by_stage.values())

    fig = go.Figure(go.Bar(
        x=values,
        y=stages,
        orientation='h',
        marker=dict(color='#0F52BA', line=dict(color='#E6EDF3', width=1)),
        text=[f"₹{v:,.0f}" for v in values],
        textposition='auto'
    ))

    fig.update_layout(
        title="<b>Open Pipeline by Stage (INR)</b>",
        xaxis_title="Pipeline Value (INR)",
        yaxis_title="Stage",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350
    )
    return fig

def create_revenue_at_risk_chart(risk_breakdown: Dict[str, float]) -> go.Figure:
    """Creates a donut chart of revenue at risk breakdown."""
    categories = [c.replace('_', ' ').title() for c in risk_breakdown.keys()]
    values = list(risk_breakdown.values())

    fig = go.Figure(go.Pie(
        labels=categories,
        values=values,
        hole=0.45,
        marker=dict(colors=['#FF6B6B', '#FFD166', '#4EA8DE', '#70E000'])
    ))

    fig.update_layout(
        title="<b>Revenue at Risk Breakdown</b>",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350
    )
    return fig

def create_sector_matrix_chart(sector_comparison: Dict[str, Dict[str, float]]) -> go.Figure:
    """Creates a grouped bar chart comparing Deals Value vs Work Orders Value by Sector."""
    sectors = list(sector_comparison.keys())
    deals_vals = [sector_comparison[s]["deals_value"] for s in sectors]
    wo_vals = [sector_comparison[s]["work_orders_value"] for s in sectors]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Deals Booked',
        x=sectors,
        y=deals_vals,
        marker_color='#0F52BA'
    ))
    fig.add_trace(go.Bar(
        name='Work Orders Contracted',
        x=sectors,
        y=wo_vals,
        marker_color='#70E000'
    ))

    fig.update_layout(
        title="<b>Sector Sales vs Execution Matrix (INR)</b>",
        barmode='group',
        xaxis_title="Sector",
        yaxis_title="Value (INR)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=380
    )
    return fig
