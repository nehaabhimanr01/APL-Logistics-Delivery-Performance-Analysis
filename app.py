import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# APL LOGISTICS - PROJECT 3
# Delivery Performance, Delay Risk & Logistics Efficiency
# ============================================================

st.set_page_config(
    page_title="APL Logistics | Delivery Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CONFIGURATION
# ============================================================

DATA_URL = (
    "https://github.com/nehaabhimanr01/"
    "APL-Logistics-Delivery-Performance-Analysis/"
    "releases/download/v1.0/APL_Logistics.csv"
)

REQUIRED_COLUMNS = [
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Late_delivery_risk",
    "Shipping Mode",
    "Order Region",
    "Market",
    "Customer Segment",
    "Benefit per order"
]

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #F7F9FC;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .hero {
        background: linear-gradient(135deg, #0D1B2A, #1B4965);
        padding: 1.5rem 1.7rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 1.2rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2rem;
    }

    .hero p {
        margin-top: 0.4rem;
        color: #D9E6EF;
        font-size: 1rem;
    }

    .insight {
        background: white;
        color: #0D1B2A !important;
        border-left: 5px solid #2A9D8F;
        padding: 0.9rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 1px 5px rgba(0,0,0,0.06);
    }

    .insight b {
        color: #0D1B2A !important;
    }

    div[data-testid="stMetric"] {
        background-color: white !important;
        color: #0D1B2A !important;
        padding: 0.8rem;
        border-radius: 10px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.06);
    }

    div[data-testid="stMetric"] label {
        color: #0D1B2A !important;
    }

    div[data-testid="stMetric"] label p {
        color: #0D1B2A !important;
    }

    div[data-testid="stMetricValue"] {
        color: #0D1B2A !important;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 0.8rem;
        border-radius: 10px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.06);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_data(data):

    data = data.copy()

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    data = data[REQUIRED_COLUMNS].copy()

    numeric_columns = [
        "Days for shipping (real)",
        "Days for shipment (scheduled)",
        "Late_delivery_risk",
        "Benefit per order"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Delivery variance
    # Positive = late
    # Negative = early
    # Zero = exactly on schedule
    # --------------------------------------------------------

    data["Delivery Variance"] = (
        data["Days for shipping (real)"]
        - data["Days for shipment (scheduled)"]
    )

    # --------------------------------------------------------
    # Delivery status
    # --------------------------------------------------------

    data["Delivery Status"] = np.where(
        data["Late_delivery_risk"].fillna(0).astype(int) == 1,
        "At Risk / Late",
        "On Time / Not at Risk"
    )

    # --------------------------------------------------------
    # Delay category
    # --------------------------------------------------------

    data["Delay Category"] = pd.cut(
        data["Delivery Variance"],
        bins=[
            -np.inf,
            -1,
            0,
            1,
            np.inf
        ],
        labels=[
            "Early",
            "On Schedule",
            "1 Day Late",
            "2+ Days Late"
        ]
    )

    return data


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(show_spinner="Loading APL Logistics dataset...")
def load_data():

    data = pd.read_csv(DATA_URL)

    return prepare_data(data)


try:

    df = load_data()
    source_name = "GitHub v1.0 Release"

except Exception as error:

    st.sidebar.warning(
        "The GitHub dataset could not be loaded."
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload APL_Logistics.csv",
        type=["csv"]
    )

    if uploaded_file is None:

        st.title("APL Logistics Delivery Intelligence")

        st.error(
            "Dataset could not be loaded automatically. "
            "Please upload APL_Logistics.csv using the sidebar."
        )

        st.stop()

    try:

        df = prepare_data(
            pd.read_csv(uploaded_file)
        )

        source_name = "Uploaded CSV"

    except Exception as upload_error:

        st.error(
            f"Unable to process the uploaded file: {upload_error}"
        )

        st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🚚 APL Logistics")
st.sidebar.caption(
    "Project 3 | Delivery Intelligence"
)

st.sidebar.markdown("---")

st.sidebar.success(
    f"Data source: {source_name}"
)

st.sidebar.caption(
    f"Records: {len(df):,}"
)

st.sidebar.markdown("---")

st.sidebar.subheader("Dashboard Filters")

shipping_modes = sorted(
    df["Shipping Mode"].dropna().unique().tolist()
)

regions = sorted(
    df["Order Region"].dropna().unique().tolist()
)

markets = sorted(
    df["Market"].dropna().unique().tolist()
)

segments = sorted(
    df["Customer Segment"].dropna().unique().tolist()
)

selected_modes = st.sidebar.multiselect(
    "Shipping Mode",
    shipping_modes,
    default=shipping_modes
)

selected_regions = st.sidebar.multiselect(
    "Order Region",
    regions,
    default=regions
)

selected_markets = st.sidebar.multiselect(
    "Market",
    markets,
    default=markets
)

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    segments,
    default=segments
)

# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df[
    df["Shipping Mode"].isin(selected_modes)
    & df["Order Region"].isin(selected_regions)
    & df["Market"].isin(selected_markets)
    & df["Customer Segment"].isin(selected_segments)
].copy()

if filtered_df.empty:

    st.warning(
        "No records match the selected filters. "
        "Please broaden your selections."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        🚚 APL Logistics | Delivery Intelligence
        <br>
        <small>
        Delivery Performance • Delay Risk • Logistics Efficiency
        </small>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} records"
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_shipments = len(filtered_df)

late_shipments = int(
    filtered_df["Late_delivery_risk"].sum()
)

late_risk_rate = (
    late_shipments / total_shipments * 100
)

avg_actual_days = filtered_df[
    "Days for shipping (real)"
].mean()

avg_scheduled_days = filtered_df[
    "Days for shipment (scheduled)"
].mean()

avg_variance = filtered_df[
    "Delivery Variance"
].mean()

avg_benefit = filtered_df[
    "Benefit per order"
].mean()


# ============================================================
# KPI DASHBOARD
# ============================================================

st.subheader("📊 Executive KPI Overview")

# KPI Row 1
k1, k2, k3 = st.columns(3)

k1.metric(
    "Total Shipments",
    f"{total_shipments:,}"
)

k2.metric(
    "At-Risk Shipments",
    f"{late_shipments:,}"
)

k3.metric(
    "Late-Risk Rate",
    f"{late_risk_rate:.1f}%"
)

# KPI Row 2
k4, k5, k6 = st.columns(3)

k4.metric(
    "Avg Actual Days",
    f"{avg_actual_days:.2f}"
)

k5.metric(
    "Avg Scheduled Days",
    f"{avg_scheduled_days:.2f}"
)

k6.metric(
    "Avg Benefit / Order",
    f"{avg_benefit:,.2f}"
)

# ============================================================
# EXECUTIVE INSIGHTS
# ============================================================

st.subheader("💡 Executive Insights")

if avg_variance > 0:

    schedule_message = (
        f"Shipments are averaging "
        f"{avg_variance:.2f} day(s) beyond the scheduled time."
    )

elif avg_variance < 0:

    schedule_message = (
        f"Shipments are averaging "
        f"{abs(avg_variance):.2f} day(s) ahead of schedule."
    )

else:

    schedule_message = (
        "Shipments are averaging exactly on the scheduled time."
    )


risk_level = (
    "High"
    if late_risk_rate >= 50
    else "Moderate"
    if late_risk_rate >= 25
    else "Lower"
)

st.markdown(
    f"""
    <div class="insight">
        <b>Delivery Risk:</b>
        {late_risk_rate:.1f}% of shipments are flagged as
        late-delivery risk. Current risk level: <b>{risk_level}</b>.
    </div>

    <div class="insight">
        <b>Schedule Adherence:</b>
        {schedule_message}
    </div>

    <div class="insight">
        <b>Commercial Indicator:</b>
        Average benefit per order is
        <b>{avg_benefit:,.2f}</b>.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DELIVERY PERFORMANCE
# ============================================================

st.subheader("📦 Delivery Performance Analysis")

col1, col2 = st.columns(2)

# ------------------------------------------------------------
# Risk Distribution
# ------------------------------------------------------------

with col1:

    status_data = (
        filtered_df[
            "Delivery Status"
        ]
        .value_counts()
        .rename_axis("Delivery Status")
        .reset_index(name="Shipments")
    )

    fig_status = px.pie(
        status_data,
        names="Delivery Status",
        values="Shipments",
        hole=0.55,
        title="Delivery Risk Distribution"
    )

    fig_status.update_layout(
        margin=dict(
            l=10,
            r=10,
            t=55,
            b=10
        )
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )


# ------------------------------------------------------------
# Delay Profile
# ------------------------------------------------------------

with col2:

    delay_order = [
        "Early",
        "On Schedule",
        "1 Day Late",
        "2+ Days Late"
    ]

    delay_data = (
        filtered_df[
            "Delay Category"
        ]
        .value_counts()
        .reindex(
            delay_order,
            fill_value=0
        )
        .rename_axis("Delay Category")
        .reset_index(name="Shipments")
    )

    fig_delay = px.bar(
        delay_data,
        x="Delay Category",
        y="Shipments",
        title="Delivery Delay Profile",
        text_auto=".2s"
    )

    fig_delay.update_layout(
        xaxis_title="Delivery Status",
        yaxis_title="Number of Shipments"
    )

    st.plotly_chart(
        fig_delay,
        use_container_width=True
    )


# ============================================================
# SHIPPING MODE ANALYSIS
# ============================================================

st.subheader("🚢 Shipping Mode Efficiency")

mode_summary = (
    filtered_df
    .groupby("Shipping Mode", as_index=False)
    .agg(
        Shipments=("Shipping Mode", "size"),
        Late_Risk_Rate=(
            "Late_delivery_risk",
            "mean"
        ),
        Avg_Actual_Days=(
            "Days for shipping (real)",
            "mean"
        ),
        Avg_Scheduled_Days=(
            "Days for shipment (scheduled)",
            "mean"
        ),
        Avg_Variance=(
            "Delivery Variance",
            "mean"
        ),
        Avg_Benefit=(
            "Benefit per order",
            "mean"
        )
    )
)

mode_summary["Late_Risk_Rate"] *= 100

fig_mode = px.bar(
    mode_summary.sort_values(
        "Late_Risk_Rate",
        ascending=False
    ),
    x="Shipping Mode",
    y="Late_Risk_Rate",
    text=mode_summary.sort_values(
        "Late_Risk_Rate",
        ascending=False
    )["Late_Risk_Rate"].map(
        lambda value: f"{value:.1f}%"
    ),
    title="Late-Delivery Risk by Shipping Mode"
)

fig_mode.update_layout(
    xaxis_title="Shipping Mode",
    yaxis_title="Late-Risk Rate (%)"
)

st.plotly_chart(
    fig_mode,
    use_container_width=True
)

st.dataframe(
    mode_summary.style.format(
        {
            "Late_Risk_Rate": "{:.1f}%",
            "Avg_Actual_Days": "{:.2f}",
            "Avg_Scheduled_Days": "{:.2f}",
            "Avg_Variance": "{:.2f}",
            "Avg_Benefit": "{:,.2f}"
        }
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MARKET ANALYSIS
# ============================================================

st.subheader("🌍 Market-Level Risk Analysis")

market_summary = (
    filtered_df
    .groupby("Market", as_index=False)
    .agg(
        Shipments=("Market", "size"),
        Late_Risk_Rate=(
            "Late_delivery_risk",
            "mean"
        ),
        Avg_Variance=(
            "Delivery Variance",
            "mean"
        ),
        Avg_Benefit=(
            "Benefit per order",
            "mean"
        )
    )
)

market_summary["Late_Risk_Rate"] *= 100

fig_market = px.bar(
    market_summary.sort_values(
        "Late_Risk_Rate",
        ascending=False
    ),
    x="Market",
    y="Late_Risk_Rate",
    text=market_summary.sort_values(
        "Late_Risk_Rate",
        ascending=False
    )["Late_Risk_Rate"].map(
        lambda value: f"{value:.1f}%"
    ),
    title="Late-Delivery Risk by Market"
)

fig_market.update_layout(
    xaxis_title="Market",
    yaxis_title="Late-Risk Rate (%)"
)

st.plotly_chart(
    fig_market,
    use_container_width=True
)

st.dataframe(
    market_summary.style.format(
        {
            "Late_Risk_Rate": "{:.1f}%",
            "Avg_Variance": "{:.2f}",
            "Avg_Benefit": "{:,.2f}"
        }
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# REGIONAL ANALYSIS
# ============================================================

st.subheader("🗺️ Regional Delivery Risk")

region_summary = (
    filtered_df
    .groupby("Order Region", as_index=False)
    .agg(
        Shipments=("Order Region", "size"),
        Late_Risk_Rate=(
            "Late_delivery_risk",
            "mean"
        ),
        Avg_Variance=(
            "Delivery Variance",
            "mean"
        ),
        Avg_Benefit=(
            "Benefit per order",
            "mean"
        )
    )
)

region_summary["Late_Risk_Rate"] *= 100

region_chart = (
    region_summary
    .sort_values(
        "Late_Risk_Rate",
        ascending=False
    )
    .head(15)
)

fig_region = px.bar(
    region_chart,
    x="Late_Risk_Rate",
    y="Order Region",
    orientation="h",
    text=region_chart[
        "Late_Risk_Rate"
    ].map(
        lambda value: f"{value:.1f}%"
    ),
    title="Highest-Risk Order Regions"
)

fig_region.update_layout(
    xaxis_title="Late-Risk Rate (%)",
    yaxis_title="Order Region"
)

st.plotly_chart(
    fig_region,
    use_container_width=True
)


# ============================================================
# CUSTOMER SEGMENT ANALYSIS
# ============================================================

st.subheader("👥 Customer Segment Analysis")

segment_summary = (
    filtered_df
    .groupby("Customer Segment", as_index=False)
    .agg(
        Shipments=("Customer Segment", "size"),
        Late_Risk_Rate=(
            "Late_delivery_risk",
            "mean"
        ),
        Avg_Variance=(
            "Delivery Variance",
            "mean"
        ),
        Avg_Benefit=(
            "Benefit per order",
            "mean"
        )
    )
)

segment_summary["Late_Risk_Rate"] *= 100

fig_segment = px.bar(
    segment_summary,
    x="Customer Segment",
    y="Late_Risk_Rate",
    text=segment_summary[
        "Late_Risk_Rate"
    ].map(
        lambda value: f"{value:.1f}%"
    ),
    title="Late-Delivery Risk by Customer Segment"
)

fig_segment.update_layout(
    xaxis_title="Customer Segment",
    yaxis_title="Late-Risk Rate (%)"
)

st.plotly_chart(
    fig_segment,
    use_container_width=True
)

st.dataframe(
    segment_summary.style.format(
        {
            "Late_Risk_Rate": "{:.1f}%",
            "Avg_Variance": "{:.2f}",
            "Avg_Benefit": "{:,.2f}"
        }
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DELAY VS BENEFIT
# ============================================================

st.subheader("📈 Delivery Variance vs. Benefit per Order")

relationship_data = (
    filtered_df
    .groupby(
        "Delivery Variance",
        as_index=False
    )
    .agg(
        Shipments=(
            "Delivery Variance",
            "size"
        ),
        Avg_Benefit=(
            "Benefit per order",
            "mean"
        )
    )
    .sort_values("Delivery Variance")
)

fig_relationship = px.scatter(
    relationship_data,
    x="Delivery Variance",
    y="Avg_Benefit",
    size="Shipments",
    hover_data=["Shipments"],
    title="Average Benefit by Delivery Variance"
)

fig_relationship.add_vline(
    x=0,
    line_dash="dash"
)

fig_relationship.update_layout(
    xaxis_title=(
        "Delivery Variance "
        "(Actual Days − Scheduled Days)"
    ),
    yaxis_title="Average Benefit per Order"
)

st.plotly_chart(
    fig_relationship,
    use_container_width=True
)


# ============================================================
# OPERATIONAL RISK MATRIX
# ============================================================

st.subheader("⚠️ Operational Risk Monitor")

risk_matrix = (
    filtered_df
    .groupby(
        [
            "Shipping Mode",
            "Market"
        ],
        as_index=False
    )
    .agg(
        Shipments=(
            "Shipping Mode",
            "size"
        ),
        Late_Risk_Rate=(
            "Late_delivery_risk",
            "mean"
        ),
        Avg_Variance=(
            "Delivery Variance",
            "mean"
        ),
        Avg_Benefit=(
            "Benefit per order",
            "mean"
        )
    )
)

risk_matrix["Late_Risk_Rate"] *= 100

risk_matrix = risk_matrix.sort_values(
    [
        "Late_Risk_Rate",
        "Shipments"
    ],
    ascending=[
        False,
        False
    ]
)

st.dataframe(
    risk_matrix.head(20).style.format(
        {
            "Late_Risk_Rate": "{:.1f}%",
            "Avg_Variance": "{:.2f}",
            "Avg_Benefit": "{:,.2f}"
        }
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DATA-DRIVEN RECOMMENDATIONS
# ============================================================

st.subheader("🎯 Data-Driven Action Areas")

highest_risk_mode_row = mode_summary.loc[
    mode_summary["Late_Risk_Rate"].idxmax()
]

highest_risk_market_row = market_summary.loc[
    market_summary["Late_Risk_Rate"].idxmax()
]

highest_risk_region_row = region_summary.loc[
    region_summary["Late_Risk_Rate"].idxmax()
]

st.markdown(
    f"""
    <div class="insight">
        <b>1. Shipping Mode:</b>
        <b>{highest_risk_mode_row['Shipping Mode']}</b>
        has the highest observed late-risk rate among the
        selected shipping modes at
        <b>{highest_risk_mode_row['Late_Risk_Rate']:.1f}%</b>.
    </div>

    <div class="insight">
        <b>2. Market:</b>
        <b>{highest_risk_market_row['Market']}</b>
        has the highest observed late-risk rate among the
        selected markets at
        <b>{highest_risk_market_row['Late_Risk_Rate']:.1f}%</b>.
    </div>

    <div class="insight">
        <b>3. Region:</b>
        <b>{highest_risk_region_row['Order Region']}</b>
        shows the highest observed late-risk rate among the
        selected regions at
        <b>{highest_risk_region_row['Late_Risk_Rate']:.1f}%</b>.
    </div>

    <div class="insight">
        <b>4. Schedule Variance:</b>
        Monitor areas where actual shipping time consistently
        exceeds scheduled shipping time and investigate the
        underlying operational bottlenecks.
    </div>

    <div class="insight">
        <b>5. Customer Experience:</b>
        Compare delay risk across customer segments before
        adjusting service levels, routing policies or
        shipping-mode allocation.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATASET METHODOLOGY
# ============================================================

with st.expander("🔎 Dataset & Methodology"):

    st.write(
        "The dashboard uses the sanitized APL Logistics dataset "
        "provided for Project 3."
    )

    st.write(
        f"**Records analysed:** {len(df):,}"
    )

    st.write(
        f"**Columns:** {', '.join(REQUIRED_COLUMNS)}"
    )

    st.write(
        "**Delivery Variance:** Actual shipping days "
        "minus scheduled shipping days."
    )

    st.write(
        "**Late-Risk Rate:** Percentage of records where "
        "`Late_delivery_risk = 1`."
    )

    st.write(
        "**Positive variance:** Shipment took longer than scheduled."
    )

    st.write(
        "**Negative variance:** Shipment was completed earlier "
        "than scheduled."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "APL Logistics | Project 3 — Delivery Performance, "
    "Delay Risk & Logistics Efficiency Analysis"
)
