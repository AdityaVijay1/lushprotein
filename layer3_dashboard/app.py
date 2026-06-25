"""LushProtein Layer 3 Customer Recommendation Dashboard."""

from __future__ import annotations

import html as html_lib

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from l3_engine import (
    DEMO_TODAY,
    LOOKBACK_DAYS,
    get_demo_customer_summaries,
    get_eligible_customer_ids,
    lookup_customer,
)

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


def esc(text: object) -> str:
    return html_lib.escape(str(text) if text is not None else "")


def init_session() -> None:
    if "lookup_id" not in st.session_state:
        st.session_state.lookup_id = ""
    if "do_search" not in st.session_state:
        st.session_state.do_search = False


def trigger_lookup(customer_id: str) -> None:
    st.session_state.lookup_id = customer_id
    st.session_state.do_search = True
    st.rerun()


def sidebar_label(row: pd.Series) -> str:
    tail = str(row["customer_id"])[-4:]
    return f"{row['name']} - {row['product_category']} (...{tail})"


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


def render_context_metrics() -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("One-and-done rate", "77.3%")
    c2.metric("Single category", "65%")
    c3.metric("Subscriber repeat gap", "3.6×")
    c4.metric("L3 prize (conservative)", "S$17–30K/yr")


def render_timeline(result: dict) -> None:
    events = [
        ("Purchase", 0, COLORS["coral"], result["transaction_date"]),
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
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


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
        st.markdown(f'<div class="field-label">{esc(label)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{esc(value)}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_recommendation_card(result: dict) -> None:
    st.markdown('<div class="card card-rec">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Layer 3 Recommendation</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-label">Recommended Product</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="field-value-lg">{esc(result["recommended_product"])}</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-label">Sample To Ship</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="field-value">{esc(result["sample_to_ship"])}</div>', unsafe_allow_html=True)
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
        f"Day {result['email_day']}: Send cross-sell email recommending <strong>{esc(result['recommended_product'])}</strong>",
        f"Day {result['time_to_send_sample_days']}: Dispatch <strong>{esc(result['sample_to_ship'])}</strong> (separate shipment, not in first order box)",
        f"Day {result['estimated_reorder_days']}: Customer enters expected reorder window — monitor for conversion",
        "After Order 2: Trigger Subscribe & Save offer (SUB-01) at Day 48",
    ]
    for step in steps:
        st.markdown(f'<div class="action-step">{step}</div>', unsafe_allow_html=True)


def render_sidebar(summaries: pd.DataFrame, eligible: list[str]) -> None:
    id_to_label = {row["customer_id"]: sidebar_label(row) for _, row in summaries.iterrows()}

    with st.sidebar:
        st.markdown("### Demo Controls")
        st.metric("Eligible customers", len(eligible))
        st.caption(f"First order in last {LOOKBACK_DAYS} days · reference {DEMO_TODAY.strftime('%d %b %Y')}")

        st.markdown("---")
        st.markdown("**Quick lookup**")
        if eligible:
            sample_id = st.selectbox(
                "Pick a demo customer",
                options=eligible,
                format_func=lambda x: id_to_label.get(x, f"{int(x):,}"),
                label_visibility="collapsed",
            )
            if st.button("Load selected customer", use_container_width=True, type="primary"):
                trigger_lookup(sample_id)
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
        st.info("Try **Aditya Vijay — Clear Protein** for the 54-day reorder / 44-day sample demo.")


def render_landing(summaries: pd.DataFrame, eligible: list[str]) -> None:
    st.markdown("### Getting started")
    st.markdown(
        "Enter a **Customer ID** above or select one from the sidebar, then click **Look up** "
        "to generate Layer 3 CRM actions for a first-time buyer."
    )

    if not eligible:
        return

    st.markdown("#### Quick demo by category")
    featured_cats = ["Clear Protein", "Lean Protein", "Collagen Glow", "Accessories", "Other"]
    picks: list[pd.Series] = []
    for cat in featured_cats:
        rows = summaries[summaries["product_category"] == cat]
        if not rows.empty:
            picks.append(rows.iloc[0])

    if picks:
        cols = st.columns(len(picks))
        for col, row in zip(cols, picks):
            short = row["product_category"].replace(" Protein", "")
            label = f"{row['name'].split()[0]} · {short}"
            with col:
                if st.button(label, key=f"quick_{row['customer_id']}", use_container_width=True):
                    trigger_lookup(row["customer_id"])


def main() -> None:
    init_session()
    summaries = get_demo_customer_summaries()
    eligible = get_eligible_customer_ids()

    render_hero()
    render_context_metrics()
    render_sidebar(summaries, eligible)

    st.markdown(
        '<div class="disclaimer">Demo environment — names and areas are anonymised. '
        "Lookup only returns eligible first-time buyers. Not for production CRM.</div>",
        unsafe_allow_html=True,
    )

    search_col, btn_col = st.columns([5, 1])
    with search_col:
        customer_input = st.text_input(
            "Enter Customer ID",
            value=st.session_state.lookup_id,
            placeholder="e.g. 8906250879231",
            help="Use the full numeric ID from the sidebar dropdown.",
        )
    with btn_col:
        st.write("")
        st.write("")
        search_clicked = st.button("Look up", type="primary", use_container_width=True)

    if search_clicked:
        trigger_lookup(customer_input.strip())

    if not st.session_state.do_search:
        render_landing(summaries, eligible)
        return

    result = lookup_customer(st.session_state.lookup_id)
    if not result.get("found"):
        st.error(result.get("error", "Customer not found."))
        st.session_state.do_search = False
        render_landing(summaries, eligible)
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
