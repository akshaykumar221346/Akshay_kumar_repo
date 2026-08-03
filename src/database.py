# %% [markdown]
# # MySQL Database Module
# Handles connection, schema creation, data loading, indexing, and reading.

# %%
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


# %%
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)

DEFAULT_TABLE_NAME = "supply_chain_orders"


# %%
def get_database_config() -> dict[str, str]:
    """Read MySQL configuration from environment variables."""

    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": os.getenv("MYSQL_PORT", "3306"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv(
            "MYSQL_DATABASE",
            "supply_chain_db",
        ),
    }

    if not config["password"]:
        raise ValueError(
            "MYSQL_PASSWORD is missing. Copy .env.example to .env "
            "and add your MySQL password."
        )

    return config


# %%
def get_server_engine() -> Engine:
    """Create an engine connected to the MySQL server."""

    config = get_database_config()
    encoded_password = quote_plus(config["password"])

    connection_string = (
        f"mysql+pymysql://{config['user']}:{encoded_password}"
        f"@{config['host']}:{config['port']}/"
        "?charset=utf8mb4"
    )

    return create_engine(
        connection_string,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


# %%
def create_database_if_not_exists() -> None:
    """Create the configured MySQL database when it does not exist."""

    config = get_database_config()
    database_name = config["database"]
    server_engine = get_server_engine()

    try:
        with server_engine.begin() as connection:
            connection.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS "
                    f"`{database_name}` "
                    "CHARACTER SET utf8mb4 "
                    "COLLATE utf8mb4_unicode_ci"
                )
            )

        print(
            f"MySQL database '{database_name}' is ready."
        )

    except SQLAlchemyError as error:
        raise ConnectionError(
            f"Unable to create MySQL database: {error}"
        ) from error

    finally:
        server_engine.dispose()


# %%
def get_mysql_engine() -> Engine:
    """Create and validate an engine for the project database."""

    create_database_if_not_exists()

    config = get_database_config()
    encoded_password = quote_plus(config["password"])

    connection_string = (
        f"mysql+pymysql://{config['user']}:{encoded_password}"
        f"@{config['host']}:{config['port']}/"
        f"{config['database']}?charset=utf8mb4"
    )

    engine = create_engine(
        connection_string,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except SQLAlchemyError as error:
        engine.dispose()

        raise ConnectionError(
            f"Unable to connect to MySQL: {error}"
        ) from error

    return engine


# %%
def prepare_dataframe_for_mysql(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Convert pandas-only types into MySQL-compatible values."""

    prepared = dataframe.copy()

    category_columns = prepared.select_dtypes(
        include=["category"]
    ).columns

    for column in category_columns:
        prepared[column] = (
            prepared[column].astype("string")
        )

    boolean_columns = prepared.select_dtypes(
        include=["bool"]
    ).columns

    for column in boolean_columns:
        prepared[column] = (
            prepared[column].astype(int)
        )

    object_columns = prepared.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in object_columns:
        prepared[column] = prepared[column].where(
            prepared[column].notna(),
            None,
        )

    prepared = prepared.replace(
        {
            pd.NA: None,
            float("inf"): None,
            float("-inf"): None,
        }
    )

    return prepared


# %%
def table_exists(
    table_name: str = DEFAULT_TABLE_NAME,
) -> bool:
    """Return True when the table exists."""

    engine = get_mysql_engine()

    try:
        return inspect(engine).has_table(table_name)

    finally:
        engine.dispose()


# %%
def create_indexes(
    engine: Engine,
    table_name: str = DEFAULT_TABLE_NAME,
) -> None:
    """
    Create indexes used by dashboard filters and analysis.

    Text columns use prefix indexes because Pandas may create
    them as MySQL TEXT columns.
    """

    index_definitions = {
        "idx_order_id": "`order_id`",
        "idx_customer_id": "`customer_id`",
        "idx_order_date": "`order_date_dateorders`",
        "idx_market": "`market`(50)",
        "idx_order_region": "`order_region`(100)",
        "idx_order_country": "`order_country`(100)",
        "idx_shipping_mode": "`shipping_mode`(50)",
        "idx_delivery_status": "`delivery_status`(50)",
        "idx_late_delivery": "`late_delivery_risk`",
        "idx_category_name": "`category_name`(100)",
    }

    inspector = inspect(engine)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(table_name)
    }

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(table_name)
    }

    required_column_names = {
        "idx_order_id": "order_id",
        "idx_customer_id": "customer_id",
        "idx_order_date": "order_date_dateorders",
        "idx_market": "market",
        "idx_order_region": "order_region",
        "idx_order_country": "order_country",
        "idx_shipping_mode": "shipping_mode",
        "idx_delivery_status": "delivery_status",
        "idx_late_delivery": "late_delivery_risk",
        "idx_category_name": "category_name",
    }

    with engine.begin() as connection:

        for index_name, index_expression in (
            index_definitions.items()
        ):

            required_column = (
                required_column_names[index_name]
            )

            if required_column not in existing_columns:
                continue

            if index_name in existing_indexes:
                continue

            try:
                connection.execute(
                    text(
                        f"CREATE INDEX `{index_name}` "
                        f"ON `{table_name}` "
                        f"({index_expression})"
                    )
                )

                print(
                    f"Created index: {index_name}"
                )

            except SQLAlchemyError as error:
                print(
                    f"Index {index_name} was skipped: "
                    f"{error}"
                )

    print("MySQL index creation completed.")


# %%
def load_dataframe_to_mysql(
    dataframe: pd.DataFrame,
    table_name: str = DEFAULT_TABLE_NAME,
    if_exists: str = "replace",
    chunk_size: int = 2000,
) -> None:
    """Load the processed DataFrame into MySQL."""

    if dataframe.empty:
        raise ValueError(
            "Cannot load an empty DataFrame into MySQL."
        )

    if if_exists not in {
        "fail",
        "replace",
        "append",
    }:
        raise ValueError(
            "if_exists must be 'fail', 'replace', or 'append'."
        )

    engine = get_mysql_engine()
    prepared = prepare_dataframe_for_mysql(dataframe)

    try:
        prepared.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=chunk_size,
            method="multi",
        )

        create_indexes(
            engine=engine,
            table_name=table_name,
        )

        print(
            f"{len(prepared):,} records loaded into "
            f"MySQL table '{table_name}'."
        )

    except SQLAlchemyError as error:
        raise RuntimeError(
            f"Unable to load data into MySQL: {error}"
        ) from error

    finally:
        engine.dispose()


# %%
def read_supply_chain_data(
    table_name: str = DEFAULT_TABLE_NAME,
    limit: int | None = None,
) -> pd.DataFrame:
    """Read supply-chain data from MySQL."""

    engine = get_mysql_engine()

    query = f"SELECT * FROM `{table_name}`"

    if limit is not None:
        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        query += f" LIMIT {int(limit)}"

    try:
        dataframe = pd.read_sql(
            text(query),
            con=engine,
        )

    except SQLAlchemyError as error:
        raise RuntimeError(
            f"Unable to read data from MySQL: {error}"
        ) from error

    finally:
        engine.dispose()

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
def execute_query(
    query: str,
    parameters: dict | None = None,
) -> pd.DataFrame:
    """Execute a read-only SQL query and return a DataFrame."""

    if not query.strip().lower().startswith(
        ("select", "with", "show", "describe")
    ):
        raise ValueError(
            "Only read-only SQL queries are allowed."
        )

    engine = get_mysql_engine()

    try:
        return pd.read_sql(
            text(query),
            con=engine,
            params=parameters,
        )

    finally:
        engine.dispose()


# %%
def get_table_summary(
    table_name: str = DEFAULT_TABLE_NAME,
) -> dict[str, int]:
    """Return row and column counts for the MySQL table."""

    engine = get_mysql_engine()

    try:
        inspector = inspect(engine)

        if not inspector.has_table(table_name):
            raise RuntimeError(
                f"MySQL table '{table_name}' does not exist."
            )

        columns = inspector.get_columns(table_name)

        with engine.connect() as connection:
            row_count = connection.execute(
                text(
                    f"SELECT COUNT(*) "
                    f"FROM `{table_name}`"
                )
            ).scalar_one()

        return {
            "rows": int(row_count),
            "columns": len(columns),
        }

    finally:
        engine.dispose()


# %%
if __name__ == "__main__":
    summary = get_table_summary()

    print(
        f"MySQL table contains {summary['rows']:,} rows "
        f"and {summary['columns']:,} columns."
    )
