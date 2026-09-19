import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# APL Logistics | Project 3
# Delivery Performance, Delay Risk & Logistics Efficiency
# ---------------------------------------------------------

st.set_page_config(
    page_title="APL Logistics | Delivery Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme / CSS ----------
st.markdown("""
<style>
    .main { background-color: #f6f9fb; }
    .block-container { padding-top: 1.2rem; }
    .hero {
        background: linear-gradient(135deg, #0D1B2A 0%, #17344A 100%);
        padding: 1.5rem 1.7rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0; font-size: 2rem; }
    .hero p { margin: .35rem 0 0; color: #d9e6ed; }
    .section-title {
        color: #0D1B2A;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: .7rem;
        margin-bottom: .5rem;
    }
    .note {
        background: #eaf7f5;
        border-left: 5px solid #2A9D8F;
        padding: .75rem 1rem;
        border-radius: 8px;
        color: #18344A;
    }
    .warning {
        background: #fff7e7;
        border-left: 5px solid #F4A623;
        padding: .75rem 1rem;
        border-radius: 8px;
        color: #5d4a1b;
    }
    .small { color: #607486; font-size: .82rem; }
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #dbe5ea;
        padding: .8rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(13,27,42,.04);
    }
</style>
""", unsafe_allow_html=True)

# ---------- Data ----------
@st.cache_data
def load_data():
    path = "data/APL_Logistics.csv"
    df = pd.read_csv(path, encoding="latin1")

    required = [
        "Days for shipping (real)",
        "Days for shipment (scheduled)",
        "Late_delivery_risk",
        "Shipping Mode",
        "Order Region",
        "Market",
        "Customer Segment",
        "Delivery Status",
        "Order Country",
        "Order City",
        "Benefit per order",
        "Sales",
        "Order Profit Per Order",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns are missing: {missing}")

    df["Delivery Gap"] = (
        pd.to_numeric(df["Days for shipping (real)"], errors="coerce")
        - pd.to_numeric(df["Days for shipment (scheduled)"], errors="coerce")
    )

    df["Delay Class"] = np.select(
        [
            df["Delivery Gap"] > 0,
            df["Delivery Gap"] < 0,
        ],
        ["Delayed", "Early"],
        default="On-time",
    )

    df["Late_delivery_risk"] = pd.to_numeric(
        df["Late_delivery_risk"], errors="coerce"
    ).fillna(0)

    return df


try:
    df = load_data()
except Exception as e:
    st.error("The dashboard could not load the supplied dataset.")
    st.exception(e)
    st.stop()

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>🚚 APL Logistics — Delivery Intelligence Dashboard</h1>
    <p>Project 3 • Delivery Performance, Delay Risk & Logistics Efficiency Analysis</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar filters ----------
st.sidebar.header("Dashboard Filters")

def options(col):
    return sorted(df[col].dropna().astype(str).unique().tolist())

selected_modes = st.sidebar.multiselect(
    "Shipping Mode",
    options("Shipping Mode"),
    default=options("Shipping Mode"),
)
selected_regions = st.sidebar.multiselect(
    "Order Region",
    options("Order Region"),
    default=options("Order Region"),
)
selected_markets = st.sidebar.multiselect(
    "Market",
    options("Market"),
    default=options("Market"),
)
selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    options("Customer Segment"),
    default=options("Customer Segment"),
)

filtered = df[
    df["Shipping Mode"].astype(str).isin(selected_modes)
    & df["Order Region"].astype(str).isin(selected_regions)
    & df["Market"].astype(str).isin(selected_markets)
    & df["Customer Segment"].astype(str).isin(selected_segments)
].copy()

if filtered.empty:
    st.warning("No records match the selected filters. Please widen the filters.")
    st.stop()

# ---------- KPI calculations ----------
total = len(filtered)
delayed = (filtered["Delivery Gap"] > 0).mean() * 100
on_time = (filtered["Delivery Gap"] <= 0).mean() * 100
avg_gap = filtered["Delivery Gap"].mean()
risk_ratio = filtered["Late_delivery_risk"].mean() * 100
actual_avg = filtered["Days for shipping (real)"].mean()
scheduled_avg = filtered["Days for shipment (scheduled)"].mean()
benefit_avg = filtered["Benefit per order"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Records", f"{total:,}")
c2.metric("On-time / Early", f"{on_time:.1f}%")
c3.metric("Delayed", f"{delayed:.1f}%")
c4.metric("Avg Delivery Gap", f"{avg_gap:.2f} days")
c5.metric("Late-risk Ratio", f"{risk_ratio:.1f}%")

st.markdown(
    '<div class="small">Delivery Gap = actual shipping days − scheduled shipping days. '
    'Delayed = gap &gt; 0; On-time = gap = 0; Early = gap &lt; 0.</div>',
    unsafe_allow_html=True,
)

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "⚠️ Delay Risk", "🚚 Shipping Mode", "🌍 Geography", "👥 Customer Segment"]
)

# ---------- Overview ----------
with tab1:
    st.markdown('<div class="section-title">Delivery Performance Overview</div>', unsafe_allow_html=True)

    a, b = st.columns(2)

    with a:
        cls = (
            filtered["Delay Class"]
            .value_counts()
            .reindex(["Delayed", "On-time", "Early"], fill_value=0)
            .reset_index()
        )
        cls.columns = ["Delay Class", "Orders"]
        fig = px.bar(
            cls,
            x="Delay Class",
            y="Orders",
            text="Orders",
            color="Delay Class",
            color_discrete_map={
                "Delayed": "#D94B4B",
                "On-time": "#2A9D8F",
                "Early": "#F4A623",
            },
            title="Orders by Delivery Classification",
        )
        fig.update_layout(showlegend=False, height=360, plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with b:
        comparison = pd.DataFrame({
            "Measure": ["Scheduled", "Actual"],
            "Days": [scheduled_avg, actual_avg],
        })
        fig = px.bar(
            comparison,
            x="Measure",
            y="Days",
            text_auto=".2f",
            color="Measure",
            color_discrete_sequence=["#2A9D8F", "#F4A623"],
            title="Average Scheduled vs Actual Shipping Time",
        )
        fig.update_layout(showlegend=False, height=360, plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f'<div class="note"><b>Current filtered view:</b> {total:,} records with an average '
        f'delivery gap of <b>{avg_gap:.2f} days</b>. Average benefit per order is '
        f'<b>${benefit_avg:.2f}</b>.</div>',
        unsafe_allow_html=True,
    )

# ---------- Delay Risk ----------
with tab2:
    st.markdown('<div class="section-title">Delay Risk Analysis</div>', unsafe_allow_html=True)

    a, b = st.columns(2)

    with a:
        fig = px.histogram(
            filtered,
            x="Delivery Gap",
            nbins=30,
            color_discrete_sequence=["#2A9D8F"],
            title="Distribution of Delivery Gap",
        )
        fig.add_vline(x=0, line_dash="dash", line_color="#D94B4B")
        fig.update_layout(height=380, plot_bgcolor="white", xaxis_title="Delivery Gap (days)")
        st.plotly_chart(fig, use_container_width=True)

    with b:
        risk_by_class = (
            filtered.groupby("Delay Class")["Late_delivery_risk"]
            .mean()
            .mul(100)
            .reindex(["Delayed", "On-time", "Early"])
            .reset_index()
        )
        risk_by_class.columns = ["Delay Class", "Risk %"]
        fig = px.bar(
            risk_by_class,
            x="Delay Class",
            y="Risk %",
            text_auto=".1f",
            color="Delay Class",
            color_discrete_map={
                "Delayed": "#D94B4B",
                "On-time": "#2A9D8F",
                "Early": "#F4A623",
            },
            title="Late-delivery-risk by Delay Class",
        )
        fig.update_layout(showlegend=False, height=380, plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    delayed_records = filtered[filtered["Delivery Gap"] > 0]
    if len(delayed_records):
        alignment = delayed_records["Late_delivery_risk"].mean() * 100
    else:
        alignment = 0

    st.markdown(
        f'<div class="warning"><b>Risk alignment:</b> {alignment:.1f}% of delayed-gap '
        f'records in the current view have Late_delivery_risk = 1. Keep the calculated '
        f'Delivery Gap and the supplied risk flag as separate KPIs when building alerts.</div>',
        unsafe_allow_html=True,
    )

# ---------- Shipping Mode ----------
with tab3:
    st.markdown('<div class="section-title">Shipping Mode Efficiency</div>', unsafe_allow_html=True)

    mode_perf = (
        filtered.groupby("Shipping Mode")
        .agg(
            Orders=("Delivery Gap", "size"),
            Delay_Rate=("Delivery Gap", lambda x: (x > 0).mean() * 100),
            Avg_Gap=("Delivery Gap", "mean"),
            Risk=("Late_delivery_risk", "mean"),
        )
        .reset_index()
        .sort_values("Delay_Rate", ascending=False)
    )

    a, b = st.columns(2)
    with a:
        fig = px.bar(
            mode_perf,
            x="Shipping Mode",
            y="Delay_Rate",
            text_auto=".1f",
            color="Delay_Rate",
            color_continuous_scale=["#2A9D8F", "#F4A623", "#D94B4B"],
            title="Delay Rate by Shipping Mode",
        )
        fig.update_layout(height=400, plot_bgcolor="white", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with b:
        fig = px.bar(
            mode_perf,
            x="Shipping Mode",
            y="Avg_Gap",
            text_auto=".2f",
            color="Avg_Gap",
            color_continuous_scale=["#2A9D8F", "#F4A623"],
            title="Average Delivery Gap by Shipping Mode",
        )
        fig.update_layout(height=400, plot_bgcolor="white", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    display_mode = mode_perf.copy()
    display_mode["Delay Rate"] = display_mode["Delay_Rate"].map(lambda x: f"{x:.1f}%")
    display_mode["Avg Gap"] = display_mode["Avg_Gap"].map(lambda x: f"{x:.2f} d")
    display_mode["Risk"] = display_mode["Risk"].map(lambda x: f"{x*100:.1f}%")
    display_mode = display_mode[["Shipping Mode", "Orders", "Delay Rate", "Avg Gap", "Risk"]]
    st.dataframe(display_mode, use_container_width=True, hide_index=True)

# ---------- Geography ----------
with tab4:
    st.markdown('<div class="section-title">Regional & Market Diagnostics</div>', unsafe_allow_html=True)

    geo = (
        filtered.groupby("Order Region")
        .agg(
            Orders=("Delivery Gap", "size"),
            Delay_Rate=("Delivery Gap", lambda x: (x > 0).mean() * 100),
            Avg_Gap=("Delivery Gap", "mean"),
        )
        .reset_index()
        .sort_values("Delay_Rate", ascending=False)
    )

    market = (
        filtered.groupby("Market")
        .agg(
            Orders=("Delivery Gap", "size"),
            Delay_Rate=("Delivery Gap", lambda x: (x > 0).mean() * 100),
        )
        .reset_index()
        .sort_values("Delay_Rate", ascending=False)
    )

    a, b = st.columns(2)
    with a:
        fig = px.bar(
            geo.head(12),
            x="Delay_Rate",
            y="Order Region",
            orientation="h",
            text_auto=".1f",
            color="Delay_Rate",
            color_continuous_scale=["#2A9D8F", "#F4A623", "#D94B4B"],
            title="Highest Regional Delay Rates",
        )
        fig.update_layout(height=460, plot_bgcolor="white", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with b:
        fig = px.bar(
            market,
            x="Market",
            y="Delay_Rate",
            text_auto=".1f",
            color="Delay_Rate",
            color_continuous_scale=["#2A9D8F", "#F4A623", "#D94B4B"],
            title="Delay Rate by Market",
        )
        fig.update_layout(height=460, plot_bgcolor="white", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "The supplied dataset contains latitude/longitude fields, but this first dashboard version "
        "uses region and market aggregations rather than exposing customer-level location details."
    )

# ---------- Customer Segment ----------
with tab5:
    st.markdown('<div class="section-title">Customer Segment Impact</div>', unsafe_allow_html=True)

    seg = (
        filtered.groupby("Customer Segment")
        .agg(
            Orders=("Delivery Gap", "size"),
            Delay_Rate=("Delivery Gap", lambda x: (x > 0).mean() * 100),
            Avg_Gap=("Delivery Gap", "mean"),
            Avg_Benefit=("Benefit per order", "mean"),
        )
        .reset_index()
        .sort_values("Delay_Rate", ascending=False)
    )

    a, b = st.columns(2)
    with a:
        fig = px.bar(
            seg,
            x="Customer Segment",
            y="Delay_Rate",
            text_auto=".1f",
            color="Delay_Rate",
            color_continuous_scale=["#2A9D8F", "#F4A623", "#D94B4B"],
            title="Delay Rate by Customer Segment",
        )
        fig.update_layout(height=390, plot_bgcolor="white", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with b:
        fig = px.bar(
            seg,
            x="Customer Segment",
            y="Avg_Gap",
            text_auto=".2f",
            color="Avg_Gap",
            color_continuous_scale=["#2A9D8F", "#F4A623"],
            title="Average Delivery Gap by Segment",
        )
        fig.update_layout(height=390, plot_bgcolor="white", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        seg.assign(
            Delay_Rate=seg["Delay_Rate"].map(lambda x: f"{x:.1f}%"),
            Avg_Gap=seg["Avg_Gap"].map(lambda x: f"{x:.2f} d"),
            Avg_Benefit=seg["Avg_Benefit"].map(lambda x: f"${x:.2f}"),
        )[["Customer Segment", "Orders", "Delay_Rate", "Avg_Gap", "Avg_Benefit"]],
        use_container_width=True,
        hide_index=True,
    )

# ---------- Footer ----------
st.markdown("---")
st.markdown(
    '<div class="small"><b>Project 3:</b> Delivery Performance, Delay Risk & Logistics Efficiency Analysis • '
    'Built from the supplied APL Logistics dataset. Customer names, streets and ZIP codes are intentionally '
    'not displayed in the dashboard.</div>',
    unsafe_allow_html=True,
)
