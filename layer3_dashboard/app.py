"""LushProtein Layer 3 Customer Recommendation Dashboard."""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go

from l3_engine import DEMO_TODAY, LOOKBACK_DAYS, get_eligible_customer_ids, lookup_customer

st.set_page_config(
    page_title="LushProtein Layer 3 Dashboard",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1C2B3A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #64748B;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    .card-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.75rem;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94A3B8;
    }
    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #1C2B3A;
    }
    .disclaimer {
        background: #FFF7ED;
        border: 1px solid #FDBA74;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #9A3412;
        font-size: 0.85rem;
    }
    .pill {
        display: inline-block;
        background: #E8F5EE;
        color: #2A7F7F;
        border-radius: 999px;
        padding: 0.2rem 0.75rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_timeline(result: dict) -> None:
    purchase_day = 0
    email_day = result["email_day"]
    sample_day = result["time_to_send_sample_days"]
    reorder_day = result["estimated_reorder_days"]

    events = [
        ("Purchase", purchase_day, "#E8603C"),
        ("Cross-sell Email", email_day, "#3B6EA5"),
        ("Sample Ships", sample_day, "#F0A500"),
        ("Expected Reorder", reorder_day, "#2A7F7F"),
    ]

    fig = go.Figure()
    xs = [e[1] for e in events]
    labels = [f"{e[0]}<br>Day {e[1]}" for e in events]
    colors = [e[2] for e in events]

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=[0] * len(xs),
            mode="markers+lines+text",
            line=dict(color="#CBD5E1", width=2),
            marker=dict(size=16, color=colors),
            text=labels,
            textposition="top center",
            textfont=dict(size=11, color="#1C2B3A"),
            hovertemplate="Day %{x}<extra></extra>",
        )
    )
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(title="Days after first delivery", showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(visible=False, range=[-0.6, 0.9]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.markdown('<p class="main-header">LushProtein Layer 3 Customer Recommendation Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Post-purchase intelligence for first-time buyers — recommend, sample, and time outreach before reorder</p>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Demo Controls")
        st.markdown(
            f'<span class="pill">Reference date: {DEMO_TODAY.strftime("%d %b %Y")}</span>',
            unsafe_allow_html=True,
        )
        st.caption(f"Eligible pool: first-time buyers with 1 order in last {LOOKBACK_DAYS} days")

        eligible = get_eligible_customer_ids()
        st.metric("Eligible customers", len(eligible))

        st.markdown("---")
        st.markdown("**Quick lookup**")
        if eligible:
            sample_id = st.selectbox(
                "Pick a demo Customer ID",
                options=eligible,
                format_func=lambda x: x,
                label_visibility="collapsed",
            )
        else:
            sample_id = None
            st.warning("No demo data found. Run build_demo_data.py first.")

        st.markdown("---")
        st.markdown(
            """
            **Layer 3 actions**
            - Cross-sell email after delivery
            - Physical sample before reorder window
            - Subscribe trigger after order 2
            """
        )

    st.markdown(
        '<div class="disclaimer">Demo environment — customer names and areas are anonymised. '
        "Lookup only returns data for eligible first-time buyers. Do not use for production CRM.</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    if "lookup_id" not in st.session_state:
        st.session_state["lookup_id"] = sample_id or ""

    col_search, col_btn = st.columns([4, 1])
    with col_search:
        customer_input = st.text_input(
            "Enter Customer ID",
            value=st.session_state.get("lookup_id", ""),
            placeholder="e.g. 6329694552319",
            help="Use the full Customer ID from the sidebar. Shopify Excel exports may truncate IDs in scientific notation.",
            key="customer_id_input",
        )
    with col_btn:
        st.write("")
        st.write("")
        search = st.button("Look up customer", type="primary", use_container_width=True)

    if not search and not customer_input:
        st.info("Enter a Customer ID above or pick one from the sidebar to generate Layer 3 CRM actions.")
        if eligible:
            st.markdown("#### Sample eligible IDs")
            preview = eligible[:8]
            cols = st.columns(4)
            for i, cid in enumerate(preview):
                with cols[i % 4]:
                    if st.button(cid, key=f"btn_{cid}"):
                        st.session_state["lookup_id"] = cid
                        st.rerun()
        return

    if not search:
        return

    st.session_state["lookup_id"] = customer_input

    result = lookup_customer(customer_input)
    if not result.get("found"):
        st.error(result.get("error", "Customer not found."))
        return

    st.success(f"Layer 3 recommendation generated for {result['name']}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="card-title">Customer Profile</div>', unsafe_allow_html=True)
        st.markdown(f"**Name:** {result['name']}")
        st.markdown(f"**Customer ID:** `{result['customer_id_display']}`")
        st.markdown(f"**Area:** {result['address_area']}")
        st.markdown(f"**Last purchase:** {result['last_product']}")
        st.markdown(f"**Transaction date:** {result['transaction_date']}")
        st.markdown(f"**Order count:** {result['order_count']} (first-time buyer)")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card"><div class="card-title">Layer 3 Recommendation</div>', unsafe_allow_html=True)
        st.markdown(f"**Recommended product:** {result['recommended_product']}")
        st.markdown(f"**Sample to ship:** {result['sample_to_ship']}")
        st.markdown(f"**Send sample on day:** {result['time_to_send_sample_days']} after delivery")
        st.markdown(f"**Estimated reorder window:** {result['estimated_reorder_days']} days")
        st.markdown(f"**Cross-sell email on day:** {result['email_day']} after delivery")
        st.caption(result["co_purchase_note"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### CRM Action Timeline")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Days until sample", result["days_until_sample"])
    m2.metric("Days until reorder", result["days_until_reorder"])
    m3.metric("Sample ships", result["sample_date"])
    m4.metric("Expected reorder", result["reorder_date"])

    render_timeline(result)

    st.markdown("#### CRM Action Summary")
    summary = {
        "Customer ID": result["customer_id_display"],
        "Name": result["name"],
        "Last Bought Product": result["last_product"],
        "Transaction Date": result["transaction_date"],
        "Recommended Product": result["recommended_product"],
        "Sample To Ship": result["sample_to_ship"],
        "Time To Send Sample (days)": result["time_to_send_sample_days"],
        "Estimated Time Till Reorder (days)": result["estimated_reorder_days"],
        "Cross-sell Email Date": result["email_date"],
        "Sample Ship Date": result["sample_date"],
        "Expected Reorder Date": result["reorder_date"],
    }
    st.table(summary)


if __name__ == "__main__":
    main()
