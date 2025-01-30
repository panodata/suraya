# Source:
# https://docs.marimo.io/guides/working_with_data/dataframes.html
# https://github.com/marimo-team/marimo/blob/main/examples/sql/querying_dataframes.py
# https://github.com/crate/cratedb-examples/blob/main/notebook/marimo/basic.py

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "duckdb",
#     "marimo",
#     "pandas==2.2.3",
#     "sqlalchemy-cratedb",
#     "sqlalchemy==2.0.36",
# ]
# ///

import marimo

__generated_with = "0.10.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    cratedb_sqlalchemy_url = "crate://cratedb:4200"
    return (cratedb_sqlalchemy_url,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Querying CrateDB

        This notebook shows how to use Marimo and CrateDB, with Python dataframes and SQL.
        First, let's create a dataframe called `df`, populated with content from CrateDB's
        built-in `sys.summits` table.
        """
    )

@app.cell(hide_code=True)
def _(mo, cratedb_sqlalchemy_url):
    mo.md(
        f"""
        Connecting to CrateDB at **`{cratedb_sqlalchemy_url}`**.
        """
    )


@app.cell
def _(mo, cratedb_sqlalchemy_url):
    import pandas as pd
    import sqlalchemy as sa

    engine = sa.create_engine(cratedb_sqlalchemy_url)
    df = pd.read_sql(sql="SELECT * FROM sys.summits ORDER BY height DESC", con=engine)

    print(df)
    df
    return df, engine, pd, sa


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        f"""
        Next, we **create a SQL cell**.
        In the SQL cell, you can query dataframes in your notebook as if they were tables — just reference them by name.
        For querying a data frame using SQL, Marimo uses DuckDB.
        """
    )
    return


@app.cell(hide_code=False)
def _(mo):
    result = mo.sql(
        f"""
        SELECT * FROM df WHERE region LIKE 'Bernina%' ORDER BY height DESC
        """,
        output=False,
    )
    return (result,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        The query output is returned to Python as a dataframe (Polars if you have it installed, Pandas otherwise).
        """
    )
    return


@app.cell
def _(result):
    print(result)
    result
    return


if __name__ == "__main__":
    app.run()
