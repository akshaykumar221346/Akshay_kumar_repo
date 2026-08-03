# %% [markdown]
# # AI Supply Chain Risk Intelligence Platform
# ## Data Cleaning and Feature Engineering Pipeline
#
# This file performs:
# 1. Dataset discovery or Kaggle download
# 2. Raw data loading
# 3. Column-name standardization
# 4. Data-quality reporting
# 5. Data cleaning
# 6. Business-rule validation
# 7. Business-oriented feature selection
# 8. Outlier detection using the IQR method
# 9. Feature engineering
# 10. Outlier flags and capped analytical variables
# 11. Feature-selection diagnostics
# 12. Final validation and CSV export
#
# The file uses `# %%` markers so that VS Code and compatible editors
# display the code as separate logical cells.


# %%
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import kagglehub
except ImportError:
    kagglehub = None


# %% [markdown]
# ## Project Paths and Configuration


# %%
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIRECTORY = PROJECT_ROOT / "data" / "processed"

RAW_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

PROCESSED_FILE_PATH = (
    PROCESSED_DATA_DIRECTORY / "dataco_cleaned_supply_chain.csv"
)

KAGGLE_DATASET_SLUG = (
    "shashwatwork/dataco-smart-supply-chain-for-big-data-analysis"
)

EXPECTED_DATASET_NAMES = [
    "DataCoSupplyChainDataset.csv",
    "dataco_supply_chain.csv",
    "DataCo_Supply_Chain.csv",
]


# %% [markdown]
# ## Analytics Feature Configuration
#
# These are the fields needed for EDA, business analysis, MySQL storage,
# and the Streamlit dashboard.


# %%
ANALYTICS_REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_customer_id",
    "order_item_id",
    "order_date_dateorders",
    "shipping_date_dateorders",
    "market",
    "order_region",
    "order_country",
    "customer_city",
    "customer_state",
    "customer_country",
    "customer_segment",
    "department_name",
    "category_name",
    "product_name",
    "shipping_mode",
    "delivery_status",
    "order_status",
    "sales",
    "sales_per_customer",
    "order_item_quantity",
    "order_item_discount",
    "order_item_discount_rate",
    "order_item_product_price",
    "order_item_total",
    "order_item_profit_ratio",
    "order_profit_per_order",
    "benefit_per_order",
    "product_price",
    "days_for_shipping_real",
    "days_for_shipment_scheduled",
    "late_delivery_risk",
    "latitude",
    "longitude",
]

OUTLIER_COLUMNS = [
    "sales",
    "sales_per_customer",
    "order_item_quantity",
    "order_item_discount",
    "order_item_product_price",
    "order_item_total",
    "order_profit_per_order",
    "benefit_per_order",
    "product_price",
    "days_for_shipping_real",
    "days_for_shipment_scheduled",
]

IDENTIFIER_COLUMNS = {
    "order_id",
    "customer_id",
    "order_customer_id",
    "order_item_id",
    "product_card_id",
    "category_id",
    "department_id",
    "order_item_cardprod_id",
    "product_category_id",
}

SENSITIVE_OR_UNUSED_COLUMNS = [
    "customer_email",
    "customer_password",
    "customer_street",
    "customer_fname",
    "customer_lname",
    "product_description",
    "product_status",
    "order_zipcode",
    "customer_zipcode",
]

DATE_COLUMNS = [
    "order_date_dateorders",
    "shipping_date_dateorders",
]

NUMERIC_COLUMNS = [
    "days_for_shipping_real",
    "days_for_shipment_scheduled",
    "benefit_per_order",
    "sales_per_customer",
    "late_delivery_risk",
    "category_id",
    "customer_id",
    "customer_zipcode",
    "department_id",
    "latitude",
    "longitude",
    "order_customer_id",
    "order_id",
    "order_item_cardprod_id",
    "order_item_discount",
    "order_item_discount_rate",
    "order_item_id",
    "order_item_product_price",
    "order_item_profit_ratio",
    "order_item_quantity",
    "sales",
    "order_item_total",
    "order_profit_per_order",
    "product_card_id",
    "product_category_id",
    "product_price",
]


# %% [markdown]
# ## Dataset Discovery and Kaggle Download


# %%
def find_local_dataset() -> Path | None:
    """
    Search the project's data/raw directory for the DataCo dataset.

    Returns:
        Path to a matching CSV file, or None when no file is found.
    """

    for file_name in EXPECTED_DATASET_NAMES:
        file_path = RAW_DATA_DIRECTORY / file_name

        if file_path.exists():
            return file_path

    for file_path in RAW_DATA_DIRECTORY.glob("*.csv"):
        normalized_name = file_path.name.lower()

        if "dataco" in normalized_name and "description" not in normalized_name:
            return file_path

    return None


# %%
def download_dataset_from_kaggle() -> Path:
    """
    Download the DataCo dataset using kagglehub and copy the main CSV
    into the project's data/raw folder.

    Raises:
        ImportError: When kagglehub is not installed.
        FileNotFoundError: When the downloaded folder does not contain
            the expected transaction CSV.
    """

    if kagglehub is None:
        raise ImportError(
            "kagglehub is not installed. Run: pip install kagglehub"
        )

    print("Downloading the DataCo dataset from Kaggle...")

    downloaded_directory = Path(
        kagglehub.dataset_download(KAGGLE_DATASET_SLUG)
    )

    candidate_files = [
        file_path
        for file_path in downloaded_directory.rglob("*.csv")
        if "datacosupplychaindataset" in file_path.name.lower()
        and "description" not in file_path.name.lower()
    ]

    if not candidate_files:
        candidate_files = [
            file_path
            for file_path in downloaded_directory.rglob("*.csv")
            if "description" not in file_path.name.lower()
            and "tokenized" not in file_path.name.lower()
        ]

    if not candidate_files:
        raise FileNotFoundError(
            "The main DataCo transaction CSV was not found in the "
            "downloaded Kaggle dataset."
        )

    source_file = candidate_files[0]
    destination_file = (
        RAW_DATA_DIRECTORY / "DataCoSupplyChainDataset.csv"
    )

    shutil.copy2(source_file, destination_file)

    print(f"Dataset copied to: {destination_file}")

    return destination_file


# %%
def resolve_dataset_path() -> Path:
    """
    Return a local DataCo dataset path. Download from Kaggle only when
    the file is not already available in data/raw.
    """

    local_dataset = find_local_dataset()

    if local_dataset is not None:
        print(f"Using local dataset: {local_dataset}")
        return local_dataset

    return download_dataset_from_kaggle()


# %% [markdown]
# ## Raw Data Loading


# %%
def load_raw_data(
    file_path: Path | str | None = None,
) -> pd.DataFrame:
    """
    Load the DataCo supply-chain CSV.

    Args:
        file_path: Optional explicit path to the main DataCo CSV.

    Returns:
        Raw pandas DataFrame.
    """

    resolved_path = (
        Path(file_path)
        if file_path is not None
        else resolve_dataset_path()
    )

    if not resolved_path.exists():
        raise FileNotFoundError(
            f"Dataset was not found at: {resolved_path}"
        )

    try:
        dataframe = pd.read_csv(
            resolved_path,
            encoding="latin1",
            low_memory=False,
        )
    except UnicodeDecodeError:
        dataframe = pd.read_csv(
            resolved_path,
            encoding="utf-8",
            low_memory=False,
        )
    except Exception as error:
        raise RuntimeError(
            f"Unable to load the DataCo dataset: {error}"
        ) from error

    print(f"Raw dataset shape: {dataframe.shape}")

    return dataframe


# %% [markdown]
# ## Column Standardization


# %%
def standardize_column_names(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert raw column names to lowercase snake_case names that are
    compatible with Python and MySQL.
    """

    standardized = dataframe.copy()

    standardized.columns = (
        standardized.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    duplicate_column_names = (
        standardized.columns[
            standardized.columns.duplicated()
        ]
        .unique()
        .tolist()
    )

    if duplicate_column_names:
        raise ValueError(
            "Duplicate column names were created after standardization: "
            f"{duplicate_column_names}"
        )

    return standardized


# %% [markdown]
# ## Data Quality Report


# %%
def create_data_quality_report(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Produce a column-level data-quality report.
    """

    report = pd.DataFrame(
        {
            "column_name": dataframe.columns,
            "data_type": dataframe.dtypes.astype(str).values,
            "row_count": len(dataframe),
            "missing_values": dataframe.isna().sum().values,
            "missing_percentage": (
                dataframe.isna().mean().values * 100
            ).round(2),
            "unique_values": dataframe.nunique(
                dropna=False
            ).values,
        }
    )

    return report.sort_values(
        by=[
            "missing_percentage",
            "unique_values",
        ],
        ascending=[
            False,
            False,
        ],
    ).reset_index(drop=True)


# %%
def save_report(
    dataframe: pd.DataFrame,
    file_name: str,
) -> Path:
    """
    Save a report DataFrame to data/processed.
    """

    output_path = PROCESSED_DATA_DIRECTORY / file_name
    dataframe.to_csv(output_path, index=False)

    return output_path


# %% [markdown]
# ## Text, Date, and Numeric Conversion


# %%
def clean_text_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Strip whitespace and normalize missing values in text columns.
    """

    cleaned = dataframe.copy()

    text_columns = cleaned.select_dtypes(
        include=[
            "object",
            "string",
            "category",
        ]
    ).columns

    for column in text_columns:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
            .replace(
                {
                    "": pd.NA,
                    "nan": pd.NA,
                    "NaN": pd.NA,
                    "none": pd.NA,
                    "None": pd.NA,
                    "null": pd.NA,
                    "NULL": pd.NA,
                }
            )
        )

    return cleaned


# %%
def convert_date_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert expected date columns into pandas datetime values.
    """

    converted = dataframe.copy()

    for column in DATE_COLUMNS:
        if column in converted.columns:
            converted[column] = pd.to_datetime(
                converted[column],
                errors="coerce",
            )

    return converted


# %%
def convert_numeric_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert expected numerical fields into numeric values.
    """

    converted = dataframe.copy()

    for column in NUMERIC_COLUMNS:
        if column in converted.columns:
            converted[column] = pd.to_numeric(
                converted[column],
                errors="coerce",
            )

    return converted


# %% [markdown]
# ## Duplicate and Privacy-Related Column Handling


# %%
def remove_duplicate_rows(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove exact duplicate rows.
    """

    duplicate_count = int(
        dataframe.duplicated().sum()
    )

    print(f"Complete duplicate rows found: {duplicate_count:,}")

    return dataframe.drop_duplicates().copy()


# %%
def remove_sensitive_or_unused_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove personal, security-related, or unnecessary fields.
    """

    cleaned = dataframe.copy()

    existing_columns = [
        column
        for column in SENSITIVE_OR_UNUSED_COLUMNS
        if column in cleaned.columns
    ]

    if existing_columns:
        cleaned = cleaned.drop(
            columns=existing_columns,
            errors="ignore",
        )

        print("Removed sensitive or unused columns:")
        for column in existing_columns:
            print(f"- {column}")

    return cleaned


# %% [markdown]
# ## Missing-Value Treatment


# %%
def drop_rows_missing_critical_values(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove records that are missing fields required for order-level
    analysis.
    """

    cleaned = dataframe.copy()

    critical_columns = [
        column
        for column in [
            "order_id",
            "customer_id",
            "order_date_dateorders",
            "shipping_date_dateorders",
            "sales",
            "order_item_quantity",
        ]
        if column in cleaned.columns
    ]

    before_rows = len(cleaned)

    cleaned = cleaned.dropna(
        subset=critical_columns
    )

    removed_rows = before_rows - len(cleaned)

    print(
        "Rows removed because critical values were missing: "
        f"{removed_rows:,}"
    )

    return cleaned


# %%
def fill_noncritical_missing_values(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fill noncritical categorical values with 'Unknown' and noncritical
    numeric values with the median.

    Identifier columns are not median-imputed.
    """

    cleaned = dataframe.copy()

    categorical_columns = cleaned.select_dtypes(
        include=[
            "object",
            "string",
            "category",
        ]
    ).columns

    for column in categorical_columns:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .fillna("Unknown")
        )

    numeric_columns = cleaned.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:
        if column in IDENTIFIER_COLUMNS:
            continue

        if cleaned[column].isna().any():
            median_value = cleaned[column].median()

            if pd.notna(median_value):
                cleaned[column] = (
                    cleaned[column]
                    .fillna(median_value)
                )

    return cleaned


# %% [markdown]
# ## Business-Rule Validation
#
# These checks remove or correct logically invalid records. Statistical
# outliers are handled separately because extreme business observations
# may still be genuine.


# %%
def apply_business_rules(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply clear business-validity rules.

    Rules:
    - Sales cannot be negative.
    - Item quantity must be greater than zero.
    - Shipping-day values cannot be negative.
    - Discount amount cannot be negative.
    - Discount rate must be between 0 and 1.
    - Late-delivery risk must be binary.
    - Invalid latitude and longitude values become missing.
    """

    cleaned = dataframe.copy()
    initial_rows = len(cleaned)

    if "sales" in cleaned.columns:
        cleaned = cleaned[
            cleaned["sales"].notna()
            & (cleaned["sales"] >= 0)
        ]

    if "order_item_quantity" in cleaned.columns:
        cleaned = cleaned[
            cleaned["order_item_quantity"].notna()
            & (cleaned["order_item_quantity"] > 0)
        ]

    for column in [
        "days_for_shipping_real",
        "days_for_shipment_scheduled",
    ]:
        if column in cleaned.columns:
            cleaned = cleaned[
                cleaned[column].notna()
                & (cleaned[column] >= 0)
            ]

    if "order_item_discount" in cleaned.columns:
        cleaned = cleaned[
            cleaned["order_item_discount"].notna()
            & (cleaned["order_item_discount"] >= 0)
        ]

    if "order_item_discount_rate" in cleaned.columns:
        valid_discount_mask = (
            cleaned["order_item_discount_rate"]
            .between(0, 1)
        )

        invalid_discount_count = int(
            (~valid_discount_mask).sum()
        )

        if invalid_discount_count:
            print(
                "Invalid discount-rate rows removed: "
                f"{invalid_discount_count:,}"
            )

        cleaned = cleaned[
            valid_discount_mask
        ]

    if "late_delivery_risk" in cleaned.columns:
        cleaned = cleaned[
            cleaned["late_delivery_risk"].isin(
                [0, 1]
            )
        ]

    if "latitude" in cleaned.columns:
        invalid_latitude_mask = ~cleaned[
            "latitude"
        ].between(-90, 90)

        cleaned.loc[
            invalid_latitude_mask,
            "latitude",
        ] = np.nan

    if "longitude" in cleaned.columns:
        invalid_longitude_mask = ~cleaned[
            "longitude"
        ].between(-180, 180)

        cleaned.loc[
            invalid_longitude_mask,
            "longitude",
        ] = np.nan

    cleaned = cleaned.reset_index(drop=True)

    removed_rows = initial_rows - len(cleaned)

    print(
        "Rows removed by business rules: "
        f"{removed_rows:,}"
    )

    return cleaned


# %% [markdown]
# ## Main Data-Cleaning Function


# %%
def clean_data(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run the main data-cleaning sequence.
    """

    print("\nStarting data cleaning...")

    cleaned = remove_duplicate_rows(
        dataframe
    )

    cleaned = remove_sensitive_or_unused_columns(
        cleaned
    )

    cleaned = clean_text_columns(
        cleaned
    )

    cleaned = convert_date_columns(
        cleaned
    )

    cleaned = convert_numeric_columns(
        cleaned
    )

    cleaned = drop_rows_missing_critical_values(
        cleaned
    )

    cleaned = fill_noncritical_missing_values(
        cleaned
    )

    cleaned = apply_business_rules(
        cleaned
    )

    cleaned = cleaned.reset_index(drop=True)

    print(f"Cleaned dataset shape: {cleaned.shape}")

    return cleaned


# %% [markdown]
# ## Business-Oriented Feature Selection
#
# This selection is for EDA, MySQL, and Streamlit. It is not the final
# machine-learning feature-selection stage.


# %%
def select_analytics_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep only the fields needed for analysis, feature engineering,
    database storage, and dashboard development.
    """

    selected_columns = [
        column
        for column in ANALYTICS_REQUIRED_COLUMNS
        if column in dataframe.columns
    ]

    missing_columns = [
        column
        for column in ANALYTICS_REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if not selected_columns:
        raise ValueError(
            "None of the required analytics columns were found."
        )

    if missing_columns:
        print("\nExpected columns not present in the raw dataset:")
        for column in missing_columns:
            print(f"- {column}")

    selected = dataframe[
        selected_columns
    ].copy()

    print(
        "Dataset shape after business feature selection: "
        f"{selected.shape}"
    )

    return selected


# %% [markdown]
# ## IQR Outlier Detection


# %%
def detect_outliers_iqr(
    dataframe: pd.DataFrame,
    columns: list[str],
    iqr_multiplier: float = 1.5,
) -> pd.DataFrame:
    """
    Detect potential outliers using the interquartile-range method.

    This function reports outliers but does not alter the data.
    """

    reports: list[dict[str, Any]] = []

    for column in columns:
        if column not in dataframe.columns:
            continue

        series = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            continue

        q1 = float(series.quantile(0.25))
        median = float(series.median())
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1

        if iqr == 0:
            lower_bound = q1
            upper_bound = q3
            outlier_count = 0
        else:
            lower_bound = q1 - iqr_multiplier * iqr
            upper_bound = q3 + iqr_multiplier * iqr

            outlier_mask = (
                (series < lower_bound)
                | (series > upper_bound)
            )

            outlier_count = int(
                outlier_mask.sum()
            )

        outlier_percentage = (
            outlier_count / len(series) * 100
            if len(series)
            else 0
        )

        reports.append(
            {
                "column_name": column,
                "minimum_value": float(series.min()),
                "q1": q1,
                "median": median,
                "q3": q3,
                "maximum_value": float(series.max()),
                "iqr": float(iqr),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "outlier_count": outlier_count,
                "outlier_percentage": round(
                    outlier_percentage,
                    2,
                ),
            }
        )

    report = pd.DataFrame(reports)

    if not report.empty:
        report = report.sort_values(
            by=[
                "outlier_percentage",
                "outlier_count",
            ],
            ascending=[
                False,
                False,
            ],
        ).reset_index(drop=True)

    return report


# %% [markdown]
# ## Outlier Flags
#
# Flags help the dashboard identify unusual transactions without deleting
# valid high-value business records.


# %%
def create_outlier_flags(
    dataframe: pd.DataFrame,
    columns: list[str],
    iqr_multiplier: float = 1.5,
) -> pd.DataFrame:
    """
    Add one binary outlier flag per selected numerical feature.
    """

    flagged = dataframe.copy()
    flag_columns: list[str] = []

    for column in columns:
        if column not in flagged.columns:
            continue

        series = pd.to_numeric(
            flagged[column],
            errors="coerce",
        )

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        flag_column = f"{column}_outlier"

        if pd.isna(iqr) or iqr == 0:
            flagged[flag_column] = 0
        else:
            lower_bound = q1 - iqr_multiplier * iqr
            upper_bound = q3 + iqr_multiplier * iqr

            flagged[flag_column] = np.where(
                (series < lower_bound)
                | (series > upper_bound),
                1,
                0,
            )

        flag_columns.append(flag_column)

    if flag_columns:
        flagged["has_numeric_outlier"] = (
            flagged[flag_columns]
            .max(axis=1)
            .astype(int)
        )

        flagged["numeric_outlier_count"] = (
            flagged[flag_columns]
            .sum(axis=1)
            .astype(int)
        )

    return flagged


# %% [markdown]
# ## Outlier Capping
#
# Original financial and operational fields remain unchanged. Separate
# `_capped` columns are created for distribution analysis, correlations,
# and later ML preprocessing.


# %%
def cap_outliers_iqr(
    dataframe: pd.DataFrame,
    columns: list[str],
    iqr_multiplier: float = 1.5,
) -> pd.DataFrame:
    """
    Create winsorized `_capped` versions of selected numeric fields.
    """

    capped = dataframe.copy()

    for column in columns:
        if column not in capped.columns:
            continue

        series = pd.to_numeric(
            capped[column],
            errors="coerce",
        )

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if pd.isna(iqr) or iqr == 0:
            print(
                f"Outlier capping skipped for {column}: "
                "IQR is zero or unavailable."
            )
            continue

        lower_bound = q1 - iqr_multiplier * iqr
        upper_bound = q3 + iqr_multiplier * iqr

        outlier_count = int(
            (
                (series < lower_bound)
                | (series > upper_bound)
            ).sum()
        )

        capped_column = f"{column}_capped"

        capped[capped_column] = series.clip(
            lower=lower_bound,
            upper=upper_bound,
        )

        print(
            f"{column}: {outlier_count:,} values capped "
            f"in {capped_column}."
        )

    return capped


# %% [markdown]
# ## Date and Operational Feature Engineering


# %%
def create_date_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create calendar features from the order date.
    """

    featured = dataframe.copy()
    order_date = "order_date_dateorders"

    if order_date not in featured.columns:
        return featured

    featured["order_year"] = (
        featured[order_date].dt.year
    )

    featured["order_month"] = (
        featured[order_date].dt.month
    )

    featured["order_month_name"] = (
        featured[order_date].dt.month_name()
    )

    featured["order_quarter"] = (
        featured[order_date].dt.quarter
    )

    featured["order_day"] = (
        featured[order_date].dt.day
    )

    featured["order_day_name"] = (
        featured[order_date].dt.day_name()
    )

    featured["order_week"] = (
        featured[order_date]
        .dt.isocalendar()
        .week
        .astype("Int64")
    )

    featured["order_year_month"] = (
        featured[order_date]
        .dt.to_period("M")
        .astype(str)
    )

    featured["is_weekend_order"] = np.where(
        featured[order_date].dt.dayofweek >= 5,
        1,
        0,
    )

    return featured


# %%
def create_delivery_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create shipment-duration and delivery-performance features.
    """

    featured = dataframe.copy()

    order_date = "order_date_dateorders"
    shipping_date = "shipping_date_dateorders"

    if {
        order_date,
        shipping_date,
    }.issubset(featured.columns):
        featured["order_to_shipping_days"] = (
            (
                featured[shipping_date]
                - featured[order_date]
            )
            .dt.total_seconds()
            .div(86_400)
            .round(2)
        )

    if {
        "days_for_shipping_real",
        "days_for_shipment_scheduled",
    }.issubset(featured.columns):
        featured["delay_days"] = (
            featured["days_for_shipping_real"]
            - featured[
                "days_for_shipment_scheduled"
            ]
        )

        featured["delivery_performance"] = np.select(
            condlist=[
                featured["delay_days"] < 0,
                featured["delay_days"] == 0,
                featured["delay_days"] > 0,
            ],
            choicelist=[
                "Early",
                "On Time",
                "Late",
            ],
            default="Unknown",
        )

        featured["delivery_risk_level"] = pd.cut(
            featured["delay_days"],
            bins=[
                -np.inf,
                0,
                1,
                3,
                np.inf,
            ],
            labels=[
                "Low",
                "Moderate",
                "High",
                "Critical",
            ],
            include_lowest=True,
        )

    return featured


# %% [markdown]
# ## Profitability and Discount Feature Engineering


# %%
def create_profitability_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create profit-margin, profit/loss, and order-value features.
    """

    featured = dataframe.copy()

    if {
        "order_profit_per_order",
        "sales",
    }.issubset(featured.columns):
        featured["profit_margin_percentage"] = (
            np.where(
                featured["sales"] != 0,
                (
                    featured[
                        "order_profit_per_order"
                    ]
                    / featured["sales"]
                )
                * 100,
                0,
            )
        ).round(2)

        featured["is_loss_order"] = np.where(
            featured["order_profit_per_order"] < 0,
            1,
            0,
        )

        featured["profit_category"] = np.where(
            featured["order_profit_per_order"] < 0,
            "Loss",
            "Profit",
        )

    if "sales" in featured.columns:
        sales_q1 = featured["sales"].quantile(0.25)
        sales_q3 = featured["sales"].quantile(0.75)

        featured["order_value_segment"] = pd.cut(
            featured["sales"],
            bins=[
                -np.inf,
                sales_q1,
                sales_q3,
                np.inf,
            ],
            labels=[
                "Low Value",
                "Medium Value",
                "High Value",
            ],
            include_lowest=True,
        )

    return featured


# %%
def create_discount_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create calculated discount percentage and discount bands.
    """

    featured = dataframe.copy()

    if {
        "order_item_discount",
        "sales",
    }.issubset(featured.columns):
        featured[
            "calculated_discount_percentage"
        ] = (
            np.where(
                featured["sales"] > 0,
                (
                    featured[
                        "order_item_discount"
                    ]
                    / featured["sales"]
                )
                * 100,
                0,
            )
        ).round(2)

    if "order_item_discount_rate" in featured.columns:
        featured["discount_band"] = pd.cut(
            featured["order_item_discount_rate"],
            bins=[
                -0.001,
                0,
                0.05,
                0.10,
                0.20,
                1.00,
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

    return featured


# %% [markdown]
# ## Fraud, Cancellation, Route, and Risk Features


# %%
def create_status_and_risk_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create fraud, cancellation, route, and overall risk indicators.
    """

    featured = dataframe.copy()

    if "order_status" in featured.columns:
        normalized_status = (
            featured["order_status"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        featured["suspected_fraud"] = np.where(
            normalized_status.eq(
                "SUSPECTED_FRAUD"
            ),
            1,
            0,
        )

        featured["is_cancelled"] = np.where(
            normalized_status.str.contains(
                "CANCELED|CANCELLED",
                regex=True,
                na=False,
            ),
            1,
            0,
        )

    if {
        "order_region",
        "order_country",
    }.issubset(featured.columns):
        featured["shipment_route"] = (
            featured["order_region"]
            .astype(str)
            .str.strip()
            + " -> "
            + featured["order_country"]
            .astype(str)
            .str.strip()
        )

    risk_components: list[pd.Series] = []

    if "late_delivery_risk" in featured.columns:
        risk_components.append(
            featured["late_delivery_risk"]
            .fillna(0)
            .astype(int)
        )

    if "is_loss_order" in featured.columns:
        risk_components.append(
            featured["is_loss_order"]
            .fillna(0)
            .astype(int)
        )

    if "suspected_fraud" in featured.columns:
        risk_components.append(
            featured["suspected_fraud"]
            .fillna(0)
            .astype(int)
        )

    if risk_components:
        risk_matrix = pd.concat(
            risk_components,
            axis=1,
        )

        featured["operational_risk_count"] = (
            risk_matrix.sum(axis=1).astype(int)
        )

        featured["overall_operational_risk"] = pd.cut(
            featured["operational_risk_count"],
            bins=[
                -1,
                0,
                1,
                3,
            ],
            labels=[
                "Low",
                "Medium",
                "High",
            ],
        )

    return featured


# %% [markdown]
# ## Complete Feature Engineering


# %%
def create_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run all feature-engineering steps.
    """

    print("\nStarting feature engineering...")

    featured = create_date_features(
        dataframe
    )

    featured = create_delivery_features(
        featured
    )

    featured = create_profitability_features(
        featured
    )

    featured = create_discount_features(
        featured
    )

    featured = create_status_and_risk_features(
        featured
    )

    print(
        "Feature engineering completed. "
        f"Current shape: {featured.shape}"
    )

    return featured


# %% [markdown]
# ## Feature-Selection Diagnostics
#
# This report identifies constant, near-constant, duplicate, and highly
# correlated fields. It does not automatically delete all correlated
# variables because some remain useful for business reporting.


# %%
def create_feature_selection_report(
    dataframe: pd.DataFrame,
    correlation_threshold: float = 0.95,
) -> dict[str, Any]:
    """
    Create feature-selection diagnostics.
    """

    constant_columns = [
        column
        for column in dataframe.columns
        if dataframe[column].nunique(
            dropna=False
        )
        <= 1
    ]

    near_constant_columns: list[str] = []

    for column in dataframe.columns:
        normalized_counts = (
            dataframe[column]
            .value_counts(
                normalize=True,
                dropna=False,
            )
        )

        if (
            not normalized_counts.empty
            and normalized_counts.iloc[0] >= 0.99
            and dataframe[column].nunique(
                dropna=False
            )
            > 1
        ):
            near_constant_columns.append(column)

    duplicate_columns: list[dict[str, str]] = []
    column_names = dataframe.columns.tolist()

    for index, first_column in enumerate(column_names):
        for second_column in column_names[index + 1:]:
            if dataframe[first_column].equals(
                dataframe[second_column]
            ):
                duplicate_columns.append(
                    {
                        "first_column": first_column,
                        "duplicate_column": second_column,
                    }
                )

    numeric_dataframe = dataframe.select_dtypes(
        include="number"
    ).copy()

    id_like_columns = [
        column
        for column in numeric_dataframe.columns
        if column in IDENTIFIER_COLUMNS
        or column.endswith("_id")
    ]

    numeric_dataframe = numeric_dataframe.drop(
        columns=id_like_columns,
        errors="ignore",
    )

    highly_correlated_pairs: list[dict[str, Any]] = []

    if numeric_dataframe.shape[1] >= 2:
        correlation_matrix = (
            numeric_dataframe.corr().abs()
        )

        columns = correlation_matrix.columns

        for row_index in range(len(columns)):
            for column_index in range(
                row_index + 1,
                len(columns),
            ):
                correlation = correlation_matrix.iloc[
                    row_index,
                    column_index,
                ]

                if (
                    pd.notna(correlation)
                    and correlation
                    >= correlation_threshold
                ):
                    highly_correlated_pairs.append(
                        {
                            "feature_1": columns[row_index],
                            "feature_2": columns[column_index],
                            "absolute_correlation": round(
                                float(correlation),
                                4,
                            ),
                        }
                    )

    return {
        "constant_columns": constant_columns,
        "near_constant_columns": near_constant_columns,
        "duplicate_columns": duplicate_columns,
        "highly_correlated_pairs": highly_correlated_pairs,
    }


# %%
def save_feature_selection_reports(
    report: dict[str, Any],
) -> None:
    """
    Save each feature-selection report section as a CSV file.
    """

    pd.DataFrame(
        {
            "constant_column": report[
                "constant_columns"
            ]
        }
    ).to_csv(
        PROCESSED_DATA_DIRECTORY
        / "constant_columns_report.csv",
        index=False,
    )

    pd.DataFrame(
        {
            "near_constant_column": report[
                "near_constant_columns"
            ]
        }
    ).to_csv(
        PROCESSED_DATA_DIRECTORY
        / "near_constant_columns_report.csv",
        index=False,
    )

    pd.DataFrame(
        report["duplicate_columns"]
    ).to_csv(
        PROCESSED_DATA_DIRECTORY
        / "duplicate_columns_report.csv",
        index=False,
    )

    pd.DataFrame(
        report["highly_correlated_pairs"]
    ).to_csv(
        PROCESSED_DATA_DIRECTORY
        / "highly_correlated_features_report.csv",
        index=False,
    )

    json_path = (
        PROCESSED_DATA_DIRECTORY
        / "feature_selection_summary.json"
    )

    with json_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            default=str,
        )


# %%
def remove_safe_redundant_features(
    dataframe: pd.DataFrame,
    feature_report: dict[str, Any],
) -> pd.DataFrame:
    """
    Remove only constant columns.

    Near-constant, duplicate, and highly correlated features are reported
    but not removed automatically because they may be useful for analysis.
    """

    cleaned = dataframe.copy()

    constant_columns = feature_report.get(
        "constant_columns",
        [],
    )

    if constant_columns:
        cleaned = cleaned.drop(
            columns=constant_columns,
            errors="ignore",
        )

        print("\nConstant columns removed:")
        for column in constant_columns:
            print(f"- {column}")

    return cleaned


# %% [markdown]
# ## Final Validation


# %%
def validate_cleaned_data(
    dataframe: pd.DataFrame,
) -> None:
    """
    Validate the final processed dataset.
    """

    if dataframe.empty:
        raise ValueError(
            "The processed dataset contains no records."
        )

    required_columns = [
        "sales",
        "order_id",
        "customer_id",
        "order_status",
        "shipping_mode",
        "late_delivery_risk",
    ]

    missing_required_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_required_columns:
        raise ValueError(
            "Required columns are missing after preprocessing: "
            f"{missing_required_columns}"
        )

    if dataframe["order_id"].isna().all():
        raise ValueError(
            "All order_id values are missing."
        )

    if (
        "order_date_dateorders" in dataframe.columns
        and dataframe[
            "order_date_dateorders"
        ].isna().all()
    ):
        raise ValueError(
            "All order dates are missing after date conversion."
        )

    if (
        "late_delivery_risk" in dataframe.columns
        and not set(
            dataframe["late_delivery_risk"]
            .dropna()
            .unique()
            .tolist()
        ).issubset({0, 1})
    ):
        raise ValueError(
            "late_delivery_risk contains nonbinary values."
        )

    print("\nFinal validation completed successfully.")
    print(f"Final rows: {len(dataframe):,}")
    print(f"Final columns: {len(dataframe.columns):,}")


# %% [markdown]
# ## Save Processed Dataset


# %%
def prepare_for_csv_export(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert category columns to strings before CSV export.
    """

    export_dataframe = dataframe.copy()

    category_columns = export_dataframe.select_dtypes(
        include="category"
    ).columns

    for column in category_columns:
        export_dataframe[column] = (
            export_dataframe[column]
            .astype("string")
        )

    return export_dataframe


# %%
def save_processed_data(
    dataframe: pd.DataFrame,
) -> Path:
    """
    Save the final cleaned and feature-engineered dataset.
    """

    export_dataframe = prepare_for_csv_export(
        dataframe
    )

    export_dataframe.to_csv(
        PROCESSED_FILE_PATH,
        index=False,
    )

    print(
        "\nProcessed dataset saved to: "
        f"{PROCESSED_FILE_PATH}"
    )

    return PROCESSED_FILE_PATH


# %% [markdown]
# ## Complete Pipeline


# %%
def run_data_pipeline(
    file_path: Path | str | None = None,
) -> pd.DataFrame:
    """
    Execute the complete preprocessing pipeline.

    Args:
        file_path: Optional path to the DataCo transaction CSV.

    Returns:
        Final cleaned and feature-engineered DataFrame.
    """

    print("=" * 72)
    print("AI SUPPLY CHAIN DATA PIPELINE")
    print("=" * 72)

    raw_dataframe = load_raw_data(
        file_path=file_path
    )

    standardized_dataframe = standardize_column_names(
        raw_dataframe
    )

    quality_before = create_data_quality_report(
        standardized_dataframe
    )

    save_report(
        quality_before,
        "data_quality_report_before_cleaning.csv",
    )

    cleaned_dataframe = clean_data(
        standardized_dataframe
    )

    selected_dataframe = select_analytics_features(
        cleaned_dataframe
    )

    outlier_report_before = detect_outliers_iqr(
        dataframe=selected_dataframe,
        columns=OUTLIER_COLUMNS,
        iqr_multiplier=1.5,
    )

    save_report(
        outlier_report_before,
        "outlier_report_before_treatment.csv",
    )

    if not outlier_report_before.empty:
        print("\nOutlier summary before treatment:")
        print(
            outlier_report_before[
                [
                    "column_name",
                    "lower_bound",
                    "upper_bound",
                    "outlier_count",
                    "outlier_percentage",
                ]
            ].to_string(index=False)
        )

    featured_dataframe = create_features(
        selected_dataframe
    )

    flagged_dataframe = create_outlier_flags(
        dataframe=featured_dataframe,
        columns=OUTLIER_COLUMNS,
        iqr_multiplier=1.5,
    )

    capped_dataframe = cap_outliers_iqr(
        dataframe=flagged_dataframe,
        columns=OUTLIER_COLUMNS,
        iqr_multiplier=1.5,
    )

    feature_report = create_feature_selection_report(
        capped_dataframe,
        correlation_threshold=0.95,
    )

    save_feature_selection_reports(
        feature_report
    )

    final_dataframe = remove_safe_redundant_features(
        dataframe=capped_dataframe,
        feature_report=feature_report,
    )

    validate_cleaned_data(
        final_dataframe
    )

    quality_after = create_data_quality_report(
        final_dataframe
    )

    save_report(
        quality_after,
        "data_quality_report_after_cleaning.csv",
    )

    save_processed_data(
        final_dataframe
    )

    print("\nPipeline completed successfully.")

    return final_dataframe


# %% [markdown]
# ## Script Execution
#
# Run this file directly with:
#
# `python src/data_pipeline.py`


# %%
if __name__ == "__main__":
    final_df = run_data_pipeline()

    print("\nSample processed records:")
    print(final_df.head())

    print("\nFinal dataset shape:")
    print(final_df.shape)
