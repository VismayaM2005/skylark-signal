import streamlit as st
from typing import List, Any, Tuple

def render_filter_bar(deals: List[Any], work_orders: List[Any]) -> Tuple[List[Any], List[Any]]:
    """
    Renders filter dropdown widgets and filters deals and work_orders lists.
    """
    sectors = set()
    for d in deals:
        if d.sector: sectors.add(d.sector)
    for w in work_orders:
        if w.sector: sectors.add(w.sector)
        
    sector_options = ["All Sectors"] + sorted(list(sectors))

    owners = set()
    for d in deals:
        if d.owner: owners.add(d.owner)
    for w in work_orders:
        if w.owner: owners.add(w.owner)
        
    owner_options = ["All Owners"] + sorted(list(owners))

    col1, col2, col3 = st.columns(3)
    with col1:
        sel_sector = st.selectbox("Sector Filter", sector_options, index=0)
    with col2:
        sel_owner = st.selectbox("Owner Filter", owner_options, index=0)
    with col3:
        sel_status = st.selectbox("Deal Status Filter", ["All Statuses", "Open", "Won", "Dead"], index=0)

    filtered_deals = deals
    filtered_wo = work_orders

    if sel_sector != "All Sectors":
        filtered_deals = [d for d in filtered_deals if d.sector == sel_sector]
        filtered_wo = [w for w in filtered_wo if w.sector == sel_sector]

    if sel_owner != "All Owners":
        filtered_deals = [d for d in filtered_deals if d.owner == sel_owner]
        filtered_wo = [w for w in filtered_wo if w.owner == sel_owner]

    if sel_status != "All Statuses":
        if sel_status == "Open":
            filtered_deals = [d for d in filtered_deals if (d.status or "").lower() in ("open", "")]
        elif sel_status == "Won":
            filtered_deals = [d for d in filtered_deals if (d.status or "").lower() in ("won", "closed won")]
        elif sel_status == "Dead":
            filtered_deals = [d for d in filtered_deals if (d.status or "").lower() in ("dead", "lost", "closed lost")]

    return filtered_deals, filtered_wo
