# %% [markdown]
# # Project Setup Runner
# Runs preprocessing and loads the final data into MySQL.

# %%
from __future__ import annotations

from src.data_pipeline import run_data_pipeline
from src.database import (
    get_table_summary,
    load_dataframe_to_mysql,
)


# %%
def main() -> None:
    """Run the data pipeline and load the result into MySQL."""

    processed_dataframe = run_data_pipeline()

    load_dataframe_to_mysql(
        dataframe=processed_dataframe,
        table_name="supply_chain_orders",
        if_exists="replace",
        chunk_size=2000,
    )

    summary = get_table_summary(
        table_name="supply_chain_orders"
    )

    print("\nProject setup completed.")
    print(
        f"MySQL table contains {summary['rows']:,} rows "
        f"and {summary['columns']:,} columns."
    )
    print("\nRun the dashboard with:")
    print("streamlit run app.py")


# %%
if __name__ == "__main__":
    main()
