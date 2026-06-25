"""LushProtein Layer 3 Customer Recommendation Dashboard."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from l3_engine import DEMO_TODAY, LOOKBACK_DAYS, get_eligible_customer_ids, lookup_customer

st.set_page_config(
    page_title="LushProtein | Layer 3 CRM",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {
    "dark": "#1C2B3A",
    "teal": "#2A7F7F",
    "coral": "#E8603C",
    "gold": "#F0A500",
    "blue": "#3B6EA5",
    "green": "#4CAF7D",
    "bg": "#F8FAFC",
    "border": "#E2E8F0",
}

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}
    .hero {{
        background: linear-gradient(135deg, {COLORS['dark']} 0%, #2A3F54 55%, {COLORS['teal']} 100%);
        border-radius: 16px;
        padding: 1.75rem 2rem;
        color: white;
        margin-bottom: 1.25rem;
        box-shadow: 0 8px 24px rgba(28,43,58,0.18);
    }}
    .hero h1 {{
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0 0 0.35rem 0;
        color: white;
    }}
    .hero p {{
        margin: 0;
        opacity: 0.92;
        font-size: 0.95rem;
    }}
    .hero-badge {{
        display: inline-block;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.75rem;
        margin-right: 0.5rem;
    }}
    .card {{
        background: #FFFFFF;
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 2px 8px rgba(15,23,42,0.04);
        height: 100%;
    }}
    .card-accent {{
        border-top: 4px solid {COLORS['teal']};
    }}
    .card-rec {{
        border-top: 4px solid {COLORS['coral']};
    }}
    .card-title {{
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.85rem;
    }}
    .field-label {{
        font-size: 0.78rem;
        color: #94A3B8;
        margin-bottom: 0.1rem;
    }}
    .field-value {{
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS['dark']};
        margin-bottom: 0.75rem;
    }}
    .field-value-lg {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {COLORS['teal']};
    }}
    .disclaimer {{
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        color: #92400E;
        font-size: 0.82rem;
        margin-bottom: 1rem;
    }}
    .action-step {{
        background: {COLORS['bg']};
        border-left: 4px solid {COLORS['teal']};
        border-radius: 0 10px 10px 0;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
    }}
    .action-step strong {{
        color: {COLORS['dark']};
    }}
    div[data-testid="stMetric"] {{
        background: white;
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 0.75rem 1rem;
        box-shadow: 0 1px 4px rgba(15,23,42,0.04);
    }}
    div[data-testid="stSidebar"] {{
        background: #F1F5F9;
    }}
    .stButton > button[kind="primary"] {{
        background: {COLORS['teal']};
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>LushProtein Layer 3 Customer Recommendation Dashboard</h1>
            <p>Post-purchase CRM intelligence — who to recommend, what sample to ship, and when to act before reorder</p>
            <span class="hero-badge">Layer 3 · Sequential Timed Journey</span>
            <span class="hero-badge">First-time buyers · Last {LOOKBACK_DAYS} days</span>
            <span class="hero-badge">Demo · {DEMO_TODAY.strftime('%d %b %Y')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_timeline(result: dict) -> None:
    events = [
        ("Purchase", 0, COLORS["coral"], "Order fulfilled"),
        ("Cross-sell Email", result["email_day"], COLORS["blue"], result["email_date"]),
        ("Sample Ships", result["time_to_send_sample_days"], COLORS["gold"], result["sample_date"]),
        ("Expected Reorder", result["estimated_reorder_days"], COLORS["teal"], result["reorder_date"]),
    ]

    fig = go.Figure()
    xs = [e[1] for e in events]
    colors = [e[2] for e in events]
    hover = [f"<b>{e[0]}</b><br>Day {e[1]}<br>{e[3]}" for e in events]

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=[0] * len(xs),
            mode="markers+lines+text",
            line=dict(color="#CBD5E1", width=3),
            marker=dict(size=20, color=colors, line=dict(width=2, color="white")),
            text=[f"<b>{e[0]}</b><br>Day {e[1]}" for e in events],
            textposition="top center",
            textfont=dict(size=11, color=COLORS["dark"]),
            hovertext=hover,
            hoverinfo="text",
        )
    )

    buffer_start = max(0, result["estimated_reorder_days"] - 10)
    fig.add_vrect(
        x0=buffer_start,
        x1=result["estimated_reorder_days"],
        fillcolor="rgba(42,127,127,0.08)",
        line_width=0,
        annotation_text="Reorder window",
        annotation_position="top left",
        annotation_font_size=10,
        annotation_font_color=COLORS["teal"],
    )

    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(title="Days after first delivery", showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        yaxis=dict(visible=False, range=[-0.75, 1.0]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_profile_card(result: dict) -> None:
    st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Customer Profile</div>', unsafe_allow_html=True)
    fields = [
        ("Name", result["name"]),
        ("Customer ID", result["customer_id_display"]),
        ("Area", result["address_area"]),
        ("Last Purchase", result["last_product"]),
        ("Category", result["last_product_category"]),
        ("Transaction Date", result["transaction_date"]),
        ("Order Count", f"{result['order_count']} — first-time buyer"),
    ]
    for label, value in fields:
        st.markdown(f'<div class="field-label">{label}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{value}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_recommendation_card(result: dict) -> None:
    st.markdown('<div class="card card-rec">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Layer 3 Recommendation</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-label">Recommended Product</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="field-value-lg">{result["recommended_product"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-label">Sample To Ship</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="field-value">{result["sample_to_ship"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="field-label">Timing</div>'
        f'<div class="field-value">Email Day {result["email_day"]} · '
        f'Sample Day {result["time_to_send_sample_days"]} · '
        f'Reorder Day {result["estimated_reorder_days"]}</div>',
        unsafe_allow_html=True,
    )
    st.caption(result["co_purchase_note"])
    st.markdown("</div>", unsafe_allow_html=True)


def render_action_checklist(result: dict) -> None:
    steps = [
        f"Day {result['email_day']}: Send cross-sell email recommending <strong>{result['recommended_product']}</strong>",
        f"Day {result['time_to_send_sample_days']}: Dispatch <strong>{result['sample_to_ship']}</strong> (separate shipment, not in first order box)",
        f"Day {result['estimated_reorder_days']}: Customer enters expected reorder window — monitor for conversion",
        "After Order 2: Trigger Subscribe & Save offer (SUB-01) at Day 48",
    ]
    for step in steps:
        st.markdown(f'<div class="action-step">{step}</div>', unsafe_allow_html=True)


def main() -> None:
    render_hero()

    eligible = get_eligible_customer_ids()

    with st.sidebar:
        st.markdown("### Demo Controls")
        st.metric("Eligible customers", len(eligible))
        st.caption(f"First order in last {LOOKBACK_DAYS} days · reference {DEMO_TODAY.strftime('%d %b %Y')}")

        st.markdown("---")
        st.markdown("**Quick lookup**")
        sample_id = None
        if eligible:
            sample_id = st.selectbox(
                "Pick a demo Customer ID",
                options=eligible,
                format_func=lambda x: f"{int(x):,}",
                label_visibility="collapsed",
            )
            if st.button("Load selected ID", use_container_width=True):
                st.session_state["lookup_id"] = sample_id
                st.session_state["do_search"] = True
                st.rerun()
        else:
            st.warning("Run `python scripts/build_demo_data.py` to create demo data.")

        st.markdown("---")
        st.markdown("**Layer 3 actions**")
        st.markdown(
            """
            1. Cross-sell email after delivery  
            2. Physical sample before reorder  
            3. Subscribe trigger after order 2
            """
        )
        st.markdown("---")
        st.markdown("**Live demo tip**")
        st.info("Pick a Clear Protein buyer to show the 54-day reorder / 44-day sample story.")

    st.markdown(
        '<div class="disclaimer">Demo environment — names and areas are anonymised. '
        "Lookup only returns eligible first-time buyers. Not for production CRM.</div>",
        unsafe_allow_html=True,
    )

    if "lookup_id" not in st.session_state:
        st.session_state["lookup_id"] = sample_id or ""
    if "do_search" not in st.session_state:
        st.session_state["do_search"] = False

    search_col, btn_col = st.columns([5, 1])
    with search_col:
        customer_input = st.text_input(
            "Enter Customer ID",
            value=st.session_state.get("lookup_id", ""),
            placeholder="e.g. 8906250879231",
            help="Use the full numeric ID from the sidebar dropdown.",
            key="customer_id_input",
        )
    with btn_col:
        st.write("")
        st.write("")
        search_clicked = st.button("Look up", type="primary", use_container_width=True)

    if search_clicked:
        st.session_state["lookup_id"] = customer_input
        st.session_state["do_search"] = True

    if not st.session_state.get("do_search"):
        st.markdown("### Getting started")
        st.markdown(
            "Enter a **Customer ID** above or select one from the sidebar, then click **Look up** "
            "to generate Layer 3 CRM actions for a first-time buyer."
        )
        if eligible:
            st.markdown("#### Sample customers")
            preview = eligible[:6]
            cols = st.columns(3)
            for i, cid in enumerate(preview):
                with cols[i % 3]:
                    if st.button(f"Demo: {int(cid):,}", key=f"quick_{cid}", use_container_width=True):
                        st.session_state["lookup_id"] = cid
                        st.session_state["do_search"] = True
                        st.rerun()
        return

    result = lookup_customer(st.session_state.get("lookup_id", customer_input))
    if not result.get("found"):
        st.error(result.get("error", "Customer not found."))
        st.session_state["do_search"] = False
        return

    st.success(f"Layer 3 recommendation ready for **{result['name']}**")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Days until sample", result["days_until_sample"])
    m2.metric("Days until reorder", result["days_until_reorder"])
    m3.metric("Sample ships", result["sample_date"])
    m4.metric("Expected reorder", result["reorder_date"])

    left, right = st.columns(2)
    with left:
        render_profile_card(result)
    with right:
        render_recommendation_card(result)

    st.markdown("### CRM Journey Timeline")
    render_timeline(result)

    st.markdown("### Recommended CRM Actions")
    render_action_checklist(result)

    with st.expander("Full CRM action summary", expanded=False):
        summary = pd.DataFrame(
            {
                "Field": [
                    "Customer ID",
                    "Name",
                    "Last Bought Product",
                    "Transaction Date",
                    "Recommended Product",
                    "Sample To Ship",
                    "Time To Send Sample (days)",
                    "Estimated Time Till Reorder (days)",
                    "Cross-sell Email Date",
                    "Sample Ship Date",
                    "Expected Reorder Date",
                ],
                "Value": [
                    result["customer_id_display"],
                    result["name"],
                    result["last_product"],
                    result["transaction_date"],
                    result["recommended_product"],
                    result["sample_to_ship"],
                    result["time_to_send_sample_days"],
                    result["estimated_reorder_days"],
                    result["email_date"],
                    result["sample_date"],
                    result["reorder_date"],
                ],
            }
        )
        st.dataframe(summary, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    main()
