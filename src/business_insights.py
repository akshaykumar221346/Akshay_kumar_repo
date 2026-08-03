# %% [markdown]
# # Business Analysis and Automated Insights
# Reusable calculations for the Streamlit dashboard.

# %%
from __future__ import annotations

import numpy as np
import pandas as pd


# %%
def require_columns(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> None:
    """Raise a clear error when required columns are missing."""

    missing_columns = [
        column
        for column in columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required columns are missing: "
            f"{missing_columns}"
        )


# %%
def calculate_kpis(
    dataframe: pd.DataFrame,
) -> dict[str, float | int]:
    """Calculate executive supply-chain KPIs."""

    require_columns(
        dataframe,
        [
            "sales",
            "order_profit_per_order",
            "order_id",
            "customer_id",
            "late_delivery_risk",
            "days_for_shipping_real",
        ],
    )

    total_revenue = float(
        dataframe["sales"].sum()
    )

    total_profit = float(
        dataframe["order_profit_per_order"].sum()
    )

    total_orders = int(
        dataframe["order_id"].nunique()
    )

    total_customers = int(
        dataframe["customer_id"].nunique()
    )

    average_order_value = (
        total_revenue / total_orders
        if total_orders
        else 0.0
    )

    overall_profit_margin = (
        total_profit / total_revenue * 100
        if total_revenue
        else 0.0
    )

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "average_order_value": average_order_value,
        "overall_profit_margin": overall_profit_margin,
        "late_delivery_rate": float(
            dataframe["late_delivery_risk"].mean()
            * 100
        ),
        "loss_order_rate": float(
            dataframe["is_loss_order"].mean()
            * 100
        )
        if "is_loss_order" in dataframe.columns
        else 0.0,
        "fraud_rate": float(
            dataframe["suspected_fraud"].mean()
            * 100
        )
        if "suspected_fraud" in dataframe.columns
        else 0.0,
        "average_shipping_days": float(
            dataframe["days_for_shipping_real"].mean()
        ),
    }


# %%
def get_monthly_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Return monthly revenue, profit, order, customer, and risk metrics."""

    require_columns(
        dataframe,
        [
            "order_year",
            "order_month",
            "order_month_name",
            "sales",
            "order_profit_per_order",
            "order_id",
            "customer_id",
            "late_delivery_risk",
        ],
    )

    monthly = (
        dataframe.groupby(
            [
                "order_year",
                "order_month",
                "order_month_name",
            ],
            as_index=False,
        )
        .agg(
            revenue=("sales", "sum"),
            profit=(
                "order_profit_per_order",
                "sum",
            ),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
            late_delivery_rate=(
                "late_delivery_risk",
                "mean",
            ),
        )
    )

    monthly["late_delivery_rate"] *= 100

    monthly["period"] = (
        monthly["order_year"]
        .astype("Int64")
        .astype(str)
        + "-"
        + monthly["order_month"]
        .astype("Int64")
        .astype(str)
        .str.zfill(2)
    )

    return monthly.sort_values(
        [
            "order_year",
            "order_month",
        ]
    ).reset_index(drop=True)


# %%
def get_category_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Return revenue, profit, quantity, and risk by category."""

    require_columns(
        dataframe,
        [
            "category_name",
            "sales",
            "order_profit_per_order",
            "order_id",
            "order_item_quantity",
            "late_delivery_risk",
        ],
    )

    aggregations = {
        "revenue": ("sales", "sum"),
        "profit": (
            "order_profit_per_order",
            "sum",
        ),
        "orders": ("order_id", "nunique"),
        "quantity": (
            "order_item_quantity",
            "sum",
        ),
        "late_delivery_rate": (
            "late_delivery_risk",
            "mean",
        ),
    }

    if "is_loss_order" in dataframe.columns:
        aggregations["loss_order_rate"] = (
            "is_loss_order",
            "mean",
        )

    category = (
        dataframe.groupby(
            "category_name",
            as_index=False,
        )
        .agg(**aggregations)
    )

    category["late_delivery_rate"] *= 100

    if "loss_order_rate" in category.columns:
        category["loss_order_rate"] *= 100
    else:
        category["loss_order_rate"] = 0.0

    category["profit_margin"] = np.where(
        category["revenue"] != 0,
        category["profit"]
        / category["revenue"]
        * 100,
        0,
    )

    return category.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)


# %%
def get_product_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Return product-level business performance."""

    require_columns(
        dataframe,
        [
            "product_name",
            "sales",
            "order_profit_per_order",
            "order_item_quantity",
            "order_id",
            "late_delivery_risk",
        ],
    )

    products = (
        dataframe.groupby(
            "product_name",
            as_index=False,
        )
        .agg(
            revenue=("sales", "sum"),
            profit=(
                "order_profit_per_order",
                "sum",
            ),
            quantity=(
                "order_item_quantity",
                "sum",
            ),
            orders=("order_id", "nunique"),
            late_delivery_rate=(
                "late_delivery_risk",
                "mean",
            ),
        )
    )

    products["late_delivery_rate"] *= 100

    products["profit_margin"] = np.where(
        products["revenue"] != 0,
        products["profit"]
        / products["revenue"]
        * 100,
        0,
    )

    return products.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)


# %%
def get_market_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Return market-level sales and delivery metrics."""

    require_columns(
        dataframe,
        [
            "market",
            "sales",
            "order_profit_per_order",
            "order_id",
            "customer_id",
            "late_delivery_risk",
            "days_for_shipping_real",
        ],
    )

    market = (
        dataframe.groupby(
            "market",
            as_index=False,
        )
        .agg(
            revenue=("sales", "sum"),
            profit=(
                "order_profit_per_order",
                "sum",
            ),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
            late_delivery_rate=(
                "late_delivery_risk",
                "mean",
            ),
            average_shipping_days=(
                "days_for_shipping_real",
                "mean",
            ),
        )
    )

    market["late_delivery_rate"] *= 100

    market["profit_margin"] = np.where(
        market["revenue"] != 0,
        market["profit"]
        / market["revenue"]
        * 100,
        0,
    )

    return market.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)


# %%
def get_country_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Return destination-country performance."""

    require_columns(
        dataframe,
        [
            "order_country",
            "sales",
            "order_profit_per_order",
            "order_id",
            "late_delivery_risk",
            "days_for_shipping_real",
        ],
    )

    country = (
        dataframe.groupby(
            "order_country",
            as_index=False,
        )
        .agg(
            revenue=("sales", "sum"),
            profit=(
                "order_profit_per_order",
                "sum",
            ),
            orders=("order_id", "nunique"),
            late_delivery_rate=(
                "late_delivery_risk",
                "mean",
            ),
            average_shipping_days=(
                "days_for_shipping_real",
                "mean",
            ),
        )
    )

    country["late_delivery_rate"] *= 100

    return country.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)


# %%
def get_shipping_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Return shipping mode performance and delivery risk."""

    require_columns(
        dataframe,
        [
            "shipping_mode",
            "order_id",
            "sales",
            "order_profit_per_order",
            "days_for_shipping_real",
            "days_for_shipment_scheduled",
            "late_delivery_risk",
        ],
    )

    shipping = (
        dataframe.groupby(
            "shipping_mode",
            as_index=False,
        )
        .agg(
            orders=("order_id", "nunique"),
            revenue=("sales", "sum"),
            profit=(
                "order_profit_per_order",
                "sum",
            ),
            average_actual_days=(
                "days_for_shipping_real",
                "mean",
            ),
            average_scheduled_days=(
                "days_for_shipment_scheduled",
                "mean",
            ),
            late_delivery_rate=(
                "late_delivery_risk",
                "mean",
            ),
        )
    )

    shipping["late_delivery_rate"] *= 100

    shipping["average_delay_days"] = (
        shipping["average_actual_days"]
        - shipping["average_scheduled_days"]
    )

    return shipping.sort_values(
        "orders",
        ascending=False,
    ).reset_index(drop=True)


# %%
def get_customer_segment_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Return performance by customer segment."""

    require_columns(
        dataframe,
        [
            "customer_segment",
            "sales",
            "order_profit_per_order",
            "order_id",
            "customer_id",
            "late_delivery_risk",
        ],
    )

    segment = (
        dataframe.groupby(
            "customer_segment",
            as_index=False,
        )
        .agg(
            revenue=("sales", "sum"),
            profit=(
                "order_profit_per_order",
                "sum",
            ),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
            late_delivery_rate=(
                "late_delivery_risk",
                "mean",
            ),
        )
    )

    segment["late_delivery_rate"] *= 100

    segment[
        "average_revenue_per_customer"
    ] = np.where(
        segment["customers"] != 0,
        segment["revenue"]
        / segment["customers"],
        0,
    )

    return segment.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)


# %%
def get_top_customers(
    dataframe: pd.DataFrame,
    top_n: int = 15,
) -> pd.DataFrame:
    """Return the highest-value customers."""

    require_columns(
        dataframe,
        [
            "customer_id",
            "sales",
            "order_profit_per_order",
            "order_id",
            "late_delivery_risk",
        ],
    )

    customers = (
        dataframe.groupby(
            "customer_id",
            as_index=False,
        )
        .agg(
            revenue=("sales", "sum"),
            profit=(
                "order_profit_per_order",
                "sum",
            ),
            orders=("order_id", "nunique"),
            late_delivery_rate=(
                "late_delivery_risk",
                "mean",
            ),
        )
    )

    customers["late_delivery_rate"] *= 100

    customers["average_order_value"] = np.where(
        customers["orders"] != 0,
        customers["revenue"]
        / customers["orders"],
        0,
    )

    return customers.nlargest(
        top_n,
        "revenue",
    ).reset_index(drop=True)


# %%
def get_high_risk_regions(
    dataframe: pd.DataFrame,
    minimum_orders: int | None = None,
) -> pd.DataFrame:
    """Identify regions with meaningful volume and high delay risk."""

    require_columns(
        dataframe,
        [
            "order_region",
            "order_id",
            "sales",
            "order_profit_per_order",
            "late_delivery_risk",
            "delay_days",
        ],
    )

    regions = (
        dataframe.groupby(
            "order_region",
            as_index=False,
        )
        .agg(
            orders=("order_id", "nunique"),
            revenue=("sales", "sum"),
            profit=(
                "order_profit_per_order",
                "sum",
            ),
            late_delivery_rate=(
                "late_delivery_risk",
                "mean",
            ),
            average_delay_days=(
                "delay_days",
                "mean",
            ),
        )
    )

    regions["late_delivery_rate"] *= 100

    if minimum_orders is None:
        minimum_orders = max(
            20,
            int(regions["orders"].median()),
        )

    regions = regions[
        regions["orders"] >= minimum_orders
    ]

    return regions.sort_values(
        [
            "late_delivery_rate",
            "orders",
        ],
        ascending=[
            False,
            False,
        ],
    ).reset_index(drop=True)


# %%
def get_loss_making_products(
    dataframe: pd.DataFrame,
    top_n: int = 10,
) -> pd.DataFrame:
    """Return products with the most negative total profit."""

    require_columns(
        dataframe,
        [
            "product_name",
            "sales",
            "order_profit_per_order",
            "order_id",
        ],
    )

    aggregations = {
        "revenue": ("sales", "sum"),
        "profit": (
            "order_profit_per_order",
            "sum",
        ),
        "orders": ("order_id", "nunique"),
    }

    if "is_loss_order" in dataframe.columns:
        aggregations["loss_transactions"] = (
            "is_loss_order",
            "sum",
        )

    products = (
        dataframe.groupby(
            "product_name",
            as_index=False,
        )
        .agg(**aggregations)
    )

    if "loss_transactions" not in products.columns:
        products["loss_transactions"] = 0

    products["loss_transaction_rate"] = np.where(
        products["orders"] != 0,
        products["loss_transactions"]
        / products["orders"]
        * 100,
        0,
    )

    return (
        products[
            products["profit"] < 0
        ]
        .sort_values(
            "profit",
            ascending=True,
        )
        .head(top_n)
        .reset_index(drop=True)
    )


# %%
def get_discount_analysis(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Analyze profitability by discount band."""

    require_columns(
        dataframe,
        [
            "order_item_discount_rate",
            "sales",
            "order_profit_per_order",
            "order_id",
        ],
    )

    discount_data = dataframe.copy()

    if "discount_band" not in discount_data.columns:
        discount_data["discount_band"] = pd.cut(
            discount_data[
                "order_item_discount_rate"
            ],
            bins=[
                -0.001,
                0,
                0.05,
                0.10,
                0.20,
                1,
            ],
            labels=[
                "No Discount",
                "1-5%",
                "6-10%",
                "11-20%",
                "Above 20%",
            ],
            include_lowest=True,
        )

    aggregations = {
        "revenue": ("sales", "sum"),
        "profit": (
            "order_profit_per_order",
            "sum",
        ),
        "orders": ("order_id", "nunique"),
        "average_profit": (
            "order_profit_per_order",
            "mean",
        ),
    }

    if "is_loss_order" in discount_data.columns:
        aggregations["loss_order_rate"] = (
            "is_loss_order",
            "mean",
        )

    result = (
        discount_data.groupby(
            "discount_band",
            observed=False,
            as_index=False,
        )
        .agg(**aggregations)
    )

    if "loss_order_rate" in result.columns:
        result["loss_order_rate"] *= 100
    else:
        result["loss_order_rate"] = 0.0

    return result


# %%
def get_fraud_analysis(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate suspected fraud counts and rates by market."""

    require_columns(
        dataframe,
        [
            "market",
            "order_id",
        ],
    )

    if "suspected_fraud" not in dataframe.columns:
        raise ValueError(
            "suspected_fraud feature is unavailable."
        )

    fraud = (
        dataframe.groupby(
            "market",
            as_index=False,
        )
        .agg(
            total_orders=("order_id", "nunique"),
            suspected_fraud_records=(
                "suspected_fraud",
                "sum",
            ),
        )
    )

    fraud["fraud_rate"] = np.where(
        fraud["total_orders"] != 0,
        fraud["suspected_fraud_records"]
        / fraud["total_orders"]
        * 100,
        0,
    )

    return fraud.sort_values(
        "fraud_rate",
        ascending=False,
    ).reset_index(drop=True)


# %%
def generate_business_insights(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Generate data-grounded narrative business insights."""

    kpis = calculate_kpis(dataframe)
    category = get_category_performance(dataframe)
    products = get_product_performance(dataframe)
    markets = get_market_performance(dataframe)
    shipping = get_shipping_performance(dataframe)
    segments = get_customer_segment_performance(
        dataframe
    )
    risky_regions = get_high_risk_regions(
        dataframe
    )
    discounts = get_discount_analysis(
        dataframe
    )

    insights = [
        (
            f"The selected data generated "
            f"${kpis['total_revenue']:,.2f} in revenue and "
            f"${kpis['total_profit']:,.2f} in profit."
        ),
        (
            f"The overall profit margin was "
            f"{kpis['overall_profit_margin']:.2f}%."
        ),
        (
            f"The data contains {kpis['total_orders']:,} unique "
            f"orders from {kpis['total_customers']:,} customers."
        ),
        (
            f"The average order value was "
            f"${kpis['average_order_value']:,.2f}."
        ),
        (
            f"The late-delivery rate was "
            f"{kpis['late_delivery_rate']:.2f}%."
        ),
        (
            f"The average actual shipping duration was "
            f"{kpis['average_shipping_days']:.2f} days."
        ),
    ]

    if not category.empty:
        top_category = category.iloc[0]

        insights.append(
            f"{top_category['category_name']} generated the "
            f"highest category revenue at "
            f"${top_category['revenue']:,.2f}."
        )

    if not products.empty:
        top_product = products.iloc[0]

        insights.append(
            f"{top_product['product_name']} was the "
            f"highest-revenue product at "
            f"${top_product['revenue']:,.2f}."
        )

    if not markets.empty:
        top_market = markets.iloc[0]

        insights.append(
            f"{top_market['market']} was the strongest market "
            f"by revenue, generating "
            f"${top_market['revenue']:,.2f}."
        )

    if not shipping.empty:
        best_shipping = shipping.nsmallest(
            1,
            "late_delivery_rate",
        ).iloc[0]

        worst_shipping = shipping.nlargest(
            1,
            "late_delivery_rate",
        ).iloc[0]

        insights.append(
            f"{best_shipping['shipping_mode']} had the lowest "
            f"late-delivery rate at "
            f"{best_shipping['late_delivery_rate']:.2f}%."
        )

        insights.append(
            f"{worst_shipping['shipping_mode']} had the highest "
            f"late-delivery rate at "
            f"{worst_shipping['late_delivery_rate']:.2f}%."
        )

    if not segments.empty:
        top_segment = segments.iloc[0]

        insights.append(
            f"The {top_segment['customer_segment']} customer "
            f"segment generated the highest revenue at "
            f"${top_segment['revenue']:,.2f}."
        )

    if not risky_regions.empty:
        region = risky_regions.iloc[0]

        insights.append(
            f"{region['order_region']} had the highest "
            f"significant regional delay rate at "
            f"{region['late_delivery_rate']:.2f}% across "
            f"{int(region['orders']):,} orders."
        )

    if not discounts.empty:
        risky_discount = discounts.nlargest(
            1,
            "loss_order_rate",
        ).iloc[0]

        insights.append(
            f"The {risky_discount['discount_band']} band had "
            f"the highest loss-order rate at "
            f"{risky_discount['loss_order_rate']:.2f}%."
        )

    if "is_loss_order" in dataframe.columns:
        insights.append(
            f"{kpis['loss_order_rate']:.2f}% of transaction "
            "records generated a negative order profit."
        )

    if "suspected_fraud" in dataframe.columns:
        insights.append(
            f"Suspected fraud represented "
            f"{kpis['fraud_rate']:.2f}% of transaction records."
        )

    return insights


# %%
def generate_business_recommendations(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Generate practical recommendations from the calculated results."""

    shipping = get_shipping_performance(dataframe)
    categories = get_category_performance(dataframe)
    loss_products = get_loss_making_products(
        dataframe
    )
    risky_regions = get_high_risk_regions(
        dataframe
    )
    discounts = get_discount_analysis(
        dataframe
    )

    recommendations: list[str] = []

    if not shipping.empty:
        worst_shipping = shipping.nlargest(
            1,
            "late_delivery_rate",
        ).iloc[0]

        recommendations.append(
            f"Review carrier capacity and service expectations "
            f"for {worst_shipping['shipping_mode']}, which has "
            f"a {worst_shipping['late_delivery_rate']:.2f}% "
            "late-delivery rate."
        )

    if not categories.empty:
        top_category = categories.iloc[0]

        recommendations.append(
            f"Protect stock availability for "
            f"{top_category['category_name']}, the leading "
            "revenue category."
        )

    if not loss_products.empty:
        product = loss_products.iloc[0]

        recommendations.append(
            f"Review pricing, procurement cost, and discounting "
            f"for {product['product_name']}, which produced a "
            f"total loss of ${abs(product['profit']):,.2f}."
        )

    if not risky_regions.empty:
        region = risky_regions.iloc[0]

        recommendations.append(
            f"Prioritize route and carrier analysis in "
            f"{region['order_region']}, where the delay rate is "
            f"{region['late_delivery_rate']:.2f}%."
        )

    if not discounts.empty:
        risky_discount = discounts.nlargest(
            1,
            "loss_order_rate",
        ).iloc[0]

        recommendations.append(
            f"Reassess the {risky_discount['discount_band']} "
            f"discount policy because its loss-order rate is "
            f"{risky_discount['loss_order_rate']:.2f}%."
        )

    recommendations.extend(
        [
            (
                "Track high-value customers separately and "
                "monitor whether delivery problems affect them."
            ),
            (
                "Review the executive dashboard regularly for "
                "changes in revenue, profit, regional delays, "
                "discount risk, and loss-making products."
            ),
        ]
    )

    return recommendations


# %%
if __name__ == "__main__":
    print(
        "Import this module from app.py or a notebook "
        "to calculate business insights."
    )
