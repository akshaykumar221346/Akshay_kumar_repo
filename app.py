# %% [markdown]
# # AI Supply Chain Risk Intelligence Platform
# Streamlit dashboard for Step 6.

# %%
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.business_insights import (
    calculate_kpis,
    generate_business_insights,
    generate_business_recommendations,
    get_category_performance,
    get_country_performance,
    get_customer_segment_performance,
    get_discount_analysis,
    get_fraud_analysis,
    get_high_risk_regions,
    get_loss_making_products,
    get_market_performance,
    get_monthly_performance,
    get_product_performance,
    get_shipping_performance,
    get_top_customers,
)
from src.database import read_supply_chain_data


# %%
st.set_page_config(
    page_title=(
        "AI Supply Chain Risk Intelligence Platform"
    ),
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.4rem;
        }

        .dashboard-title {
            font-size: 2.25rem;
            font-weight: 750;
            margin-bottom: 0.2rem;
        }

        .dashboard-subtitle {
            color: #6b7280;
            margin-bottom: 1.4rem;
        }

        .insight-card {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 10px;
            padding: 0.9rem;
            margin-bottom: 0.7rem;
        }

        .recommendation-card {
            border-left: 5px solid #6b7280;
            background: rgba(128, 128, 128, 0.08);
            border-radius: 5px;
            padding: 0.9rem;
            margin-bottom: 0.7rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# %%
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    """Load processed supply-chain data from MySQL."""

    dataframe = read_supply_chain_data()

    for column in [
        "order_date_dateorders",
        "shipping_date_dateorders",
    ]:
        if column in dataframe.columns:
            dataframe[column] = pd.to_datetime(
                dataframe[column],
                errors="coerce",
            )

    return dataframe


# %%
def sorted_values(
    dataframe: pd.DataFrame,
    column: str,
) -> list:
    """Return sorted unique string values."""

    if column not in dataframe.columns:
        return []

    return sorted(
        dataframe[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


# %%
def format_currency(value: float) -> str:
    """Format currency values for KPI cards."""

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:,.2f}K"

    return f"${value:,.2f}"


# %%
def display_kpis(
    dataframe: pd.DataFrame,
) -> None:
    """Render executive KPI cards."""

    kpis = calculate_kpis(dataframe)

    first_row = st.columns(5)

    first_row[0].metric(
        "Revenue",
        format_currency(
            kpis["total_revenue"]
        ),
    )

    first_row[1].metric(
        "Profit",
        format_currency(
            kpis["total_profit"]
        ),
    )

    first_row[2].metric(
        "Orders",
        f"{kpis['total_orders']:,}",
    )

    first_row[3].metric(
        "Customers",
        f"{kpis['total_customers']:,}",
    )

    first_row[4].metric(
        "Average Order Value",
        format_currency(
            kpis["average_order_value"]
        ),
    )

    second_row = st.columns(5)

    second_row[0].metric(
        "Profit Margin",
        f"{kpis['overall_profit_margin']:.2f}%",
    )

    second_row[1].metric(
        "Late Delivery Rate",
        f"{kpis['late_delivery_rate']:.2f}%",
    )

    second_row[2].metric(
        "Loss Order Rate",
        f"{kpis['loss_order_rate']:.2f}%",
    )

    second_row[3].metric(
        "Suspected Fraud Rate",
        f"{kpis['fraud_rate']:.2f}%",
    )

    second_row[4].metric(
        "Average Shipping Days",
        f"{kpis['average_shipping_days']:.2f}",
    )


# %%
try:
    source_dataframe = load_data()

except Exception as error:
    st.error(
        "The dashboard could not load data from MySQL."
    )
    st.code(
        "python setup_project.py\n"
        "streamlit run app.py"
    )
    st.exception(error)
    st.stop()


# %%
st.markdown(
    """
    <div class="dashboard-title">
        AI Supply Chain Risk Intelligence Platform
    </div>
    <div class="dashboard-subtitle">
        MySQL-backed analytics for revenue, profitability,
        customer behavior, and delivery risk.
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Navigation")

selected_page = st.sidebar.radio(
    "Select page",
    [
        "Executive Overview",
        "Sales & Profitability",
        "Products & Categories",
        "Customer Analytics",
        "Shipping & Delivery Risk",
        "Geographic Analysis",
        "Business Insights",
        "Data Explorer",
    ],
)


# %%
st.sidebar.divider()
st.sidebar.subheader("Filters")

years = sorted(
    source_dataframe["order_year"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

selected_years = st.sidebar.multiselect(
    "Order year",
    years,
    default=years,
)

markets = sorted_values(
    source_dataframe,
    "market",
)

selected_markets = st.sidebar.multiselect(
    "Market",
    markets,
    default=markets,
)

segments = sorted_values(
    source_dataframe,
    "customer_segment",
)

selected_segments = st.sidebar.multiselect(
    "Customer segment",
    segments,
    default=segments,
)

shipping_modes = sorted_values(
    source_dataframe,
    "shipping_mode",
)

selected_shipping_modes = st.sidebar.multiselect(
    "Shipping mode",
    shipping_modes,
    default=shipping_modes,
)

delivery_statuses = sorted_values(
    source_dataframe,
    "delivery_status",
)

selected_delivery_statuses = st.sidebar.multiselect(
    "Delivery status",
    delivery_statuses,
    default=delivery_statuses,
)


# %%
filtered_dataframe = source_dataframe.copy()

if selected_years:
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["order_year"].isin(
            selected_years
        )
    ]

if selected_markets:
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["market"]
        .astype(str)
        .isin(selected_markets)
    ]

if selected_segments:
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["customer_segment"]
        .astype(str)
        .isin(selected_segments)
    ]

if selected_shipping_modes:
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["shipping_mode"]
        .astype(str)
        .isin(selected_shipping_modes)
    ]

if selected_delivery_statuses:
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["delivery_status"]
        .astype(str)
        .isin(selected_delivery_statuses)
    ]

if filtered_dataframe.empty:
    st.warning(
        "No records match the selected filters."
    )
    st.stop()

st.sidebar.divider()
st.sidebar.metric(
    "Filtered rows",
    f"{len(filtered_dataframe):,}",
)
st.sidebar.metric(
    "Unique orders",
    f"{filtered_dataframe['order_id'].nunique():,}",
)


# %%
if selected_page == "Executive Overview":
    st.header("Executive Overview")
    display_kpis(filtered_dataframe)

    monthly = get_monthly_performance(
        filtered_dataframe
    )
    markets_data = get_market_performance(
        filtered_dataframe
    )
    shipping = get_shipping_performance(
        filtered_dataframe
    )

    left, right = st.columns(2)

    with left:
        figure = px.line(
            monthly,
            x="period",
            y="revenue",
            markers=True,
            title="Monthly Revenue",
            labels={
                "period": "Month",
                "revenue": "Revenue",
            },
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    with right:
        figure = px.bar(
            markets_data.sort_values(
                "revenue",
                ascending=True,
            ),
            x="revenue",
            y="market",
            orientation="h",
            title="Revenue by Market",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    left, right = st.columns(2)

    with left:
        delivery_counts = (
            filtered_dataframe["delivery_status"]
            .value_counts()
            .rename_axis("delivery_status")
            .reset_index(name="records")
        )

        figure = px.pie(
            delivery_counts,
            names="delivery_status",
            values="records",
            hole=0.45,
            title="Delivery Status Distribution",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    with right:
        figure = px.bar(
            shipping.sort_values(
                "late_delivery_rate",
                ascending=True,
            ),
            x="late_delivery_rate",
            y="shipping_mode",
            orientation="h",
            title="Late Delivery Rate by Shipping Mode",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    st.subheader("Executive Highlights")

    for insight in generate_business_insights(
        filtered_dataframe
    )[:6]:
        st.markdown(
            f'<div class="insight-card">{insight}</div>',
            unsafe_allow_html=True,
        )


# %%
elif selected_page == "Sales & Profitability":
    st.header("Sales & Profitability")
    display_kpis(filtered_dataframe)

    monthly = get_monthly_performance(
        filtered_dataframe
    )
    discount_data = get_discount_analysis(
        filtered_dataframe
    )

    figure = px.line(
        monthly,
        x="period",
        y=[
            "revenue",
            "profit",
        ],
        markers=True,
        title="Monthly Revenue and Profit",
    )
    st.plotly_chart(
        figure,
        use_container_width=True,
    )

    left, right = st.columns(2)

    with left:
        profit_counts = (
            filtered_dataframe["profit_category"]
            .value_counts()
            .rename_axis("profit_category")
            .reset_index(name="records")
        )

        figure = px.pie(
            profit_counts,
            names="profit_category",
            values="records",
            hole=0.45,
            title="Profit vs Loss Transactions",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    with right:
        figure = px.bar(
            discount_data,
            x="discount_band",
            y="loss_order_rate",
            title="Loss Rate by Discount Band",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    loss_products = get_loss_making_products(
        filtered_dataframe
    )

    if not loss_products.empty:
        figure = px.bar(
            loss_products.sort_values(
                "profit",
                ascending=False,
            ),
            x="profit",
            y="product_name",
            orientation="h",
            title="Largest Product Losses",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )


# %%
elif selected_page == "Products & Categories":
    st.header("Products & Categories")

    categories = get_category_performance(
        filtered_dataframe
    )
    products = get_product_performance(
        filtered_dataframe
    )

    left, right = st.columns(2)

    with left:
        figure = px.bar(
            categories.head(10).sort_values(
                "revenue",
                ascending=True,
            ),
            x="revenue",
            y="category_name",
            orientation="h",
            title="Top Categories by Revenue",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    with right:
        figure = px.bar(
            products.head(10).sort_values(
                "revenue",
                ascending=True,
            ),
            x="revenue",
            y="product_name",
            orientation="h",
            title="Top Products by Revenue",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    figure = px.scatter(
        categories,
        x="revenue",
        y="late_delivery_rate",
        size="orders",
        hover_name="category_name",
        title="Category Revenue vs Delivery Risk",
    )
    st.plotly_chart(
        figure,
        use_container_width=True,
    )

    st.dataframe(
        categories,
        use_container_width=True,
        hide_index=True,
    )


# %%
elif selected_page == "Customer Analytics":
    st.header("Customer Analytics")

    segments_data = (
        get_customer_segment_performance(
            filtered_dataframe
        )
    )
    customers = get_top_customers(
        filtered_dataframe
    )

    left, right = st.columns(2)

    with left:
        figure = px.bar(
            segments_data,
            x="customer_segment",
            y="revenue",
            title="Revenue by Customer Segment",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    with right:
        figure = px.bar(
            segments_data,
            x="customer_segment",
            y="late_delivery_rate",
            title="Delivery Risk by Customer Segment",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    figure = px.bar(
        customers.sort_values(
            "revenue",
            ascending=True,
        ),
        x="revenue",
        y=customers["customer_id"].astype(str),
        orientation="h",
        title="Top Customers by Revenue",
        labels={"y": "Customer ID"},
    )
    st.plotly_chart(
        figure,
        use_container_width=True,
    )

    st.dataframe(
        customers,
        use_container_width=True,
        hide_index=True,
    )


# %%
elif selected_page == "Shipping & Delivery Risk":
    st.header("Shipping & Delivery Risk")

    shipping = get_shipping_performance(
        filtered_dataframe
    )
    regions = get_high_risk_regions(
        filtered_dataframe
    )

    left, right = st.columns(2)

    with left:
        figure = px.bar(
            shipping.sort_values(
                "orders",
                ascending=True,
            ),
            x="orders",
            y="shipping_mode",
            orientation="h",
            title="Orders by Shipping Mode",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    with right:
        figure = px.bar(
            shipping.sort_values(
                "late_delivery_rate",
                ascending=True,
            ),
            x="late_delivery_rate",
            y="shipping_mode",
            orientation="h",
            title="Late Delivery Rate by Shipping Mode",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    figure = px.bar(
        regions.head(15).sort_values(
            "late_delivery_rate",
            ascending=True,
        ),
        x="late_delivery_rate",
        y="order_region",
        orientation="h",
        title="Highest-Risk Regions",
        hover_data=[
            "orders",
            "average_delay_days",
            "revenue",
        ],
    )
    st.plotly_chart(
        figure,
        use_container_width=True,
    )

    st.dataframe(
        regions.head(20),
        use_container_width=True,
        hide_index=True,
    )


# %%
elif selected_page == "Geographic Analysis":
    st.header("Geographic Analysis")

    markets_data = get_market_performance(
        filtered_dataframe
    )
    countries = get_country_performance(
        filtered_dataframe
    )

    left, right = st.columns(2)

    with left:
        figure = px.bar(
            markets_data.sort_values(
                "revenue",
                ascending=True,
            ),
            x="revenue",
            y="market",
            orientation="h",
            title="Revenue by Market",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    with right:
        figure = px.scatter(
            markets_data,
            x="revenue",
            y="late_delivery_rate",
            size="orders",
            hover_name="market",
            title="Market Revenue vs Delivery Risk",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    figure = px.bar(
        countries.head(20).sort_values(
            "revenue",
            ascending=True,
        ),
        x="revenue",
        y="order_country",
        orientation="h",
        title="Top Countries by Revenue",
    )
    st.plotly_chart(
        figure,
        use_container_width=True,
    )

    map_data = filtered_dataframe.dropna(
        subset=[
            "latitude",
            "longitude",
        ]
    )

    if not map_data.empty:
        map_sample = map_data.sample(
            min(
                10000,
                len(map_data),
            ),
            random_state=42,
        )

        figure = px.scatter_map(
            map_sample,
            lat="latitude",
            lon="longitude",
            color="late_delivery_risk",
            size="sales",
            hover_name="customer_city",
            hover_data=[
                "order_country",
                "market",
                "shipping_mode",
                "delivery_status",
            ],
            zoom=1,
            height=600,
            title="Customer Locations and Delivery Risk",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )


# %%
elif selected_page == "Business Insights":
    st.header("Automated Business Insights")

    for number, insight in enumerate(
        generate_business_insights(
            filtered_dataframe
        ),
        start=1,
    ):
        st.markdown(
            (
                '<div class="insight-card">'
                f"<strong>Insight {number}:</strong> "
                f"{insight}</div>"
            ),
            unsafe_allow_html=True,
        )

    st.subheader("Recommendations")

    for number, recommendation in enumerate(
        generate_business_recommendations(
            filtered_dataframe
        ),
        start=1,
    ):
        st.markdown(
            (
                '<div class="recommendation-card">'
                f"<strong>Recommendation {number}:</strong> "
                f"{recommendation}</div>"
            ),
            unsafe_allow_html=True,
        )

    if "suspected_fraud" in filtered_dataframe.columns:
        fraud = get_fraud_analysis(
            filtered_dataframe
        )

        figure = px.bar(
            fraud,
            x="market",
            y="fraud_rate",
            title="Suspected Fraud Rate by Market",
        )
        st.plotly_chart(
            figure,
            use_container_width=True,
        )


# %%
elif selected_page == "Data Explorer":
    st.header("Data Explorer")

    search_column = st.selectbox(
        "Search column",
        filtered_dataframe.columns.tolist(),
    )

    search_value = st.text_input(
        "Search value"
    )

    explorer = filtered_dataframe.copy()

    if search_value:
        explorer = explorer[
            explorer[search_column]
            .astype(str)
            .str.contains(
                search_value,
                case=False,
                na=False,
            )
        ]

    default_columns = [
        column
        for column in [
            "order_id",
            "order_date_dateorders",
            "customer_id",
            "category_name",
            "product_name",
            "market",
            "order_country",
            "sales",
            "order_profit_per_order",
            "shipping_mode",
            "delivery_status",
            "late_delivery_risk",
        ]
        if column in explorer.columns
    ]

    selected_columns = st.multiselect(
        "Display columns",
        explorer.columns.tolist(),
        default=default_columns,
    )

    displayed = (
        explorer[selected_columns]
        if selected_columns
        else explorer
    )

    st.dataframe(
        displayed,
        use_container_width=True,
        hide_index=True,
        height=600,
    )

    st.download_button(
        "Download filtered CSV",
        data=displayed.to_csv(
            index=False
        ).encode("utf-8"),
        file_name=(
            "filtered_supply_chain_data.csv"
        ),
        mime="text/csv",
    )
