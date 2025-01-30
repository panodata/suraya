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
    cratedb_sqlalchemy_url = "crate://"
    return (cratedb_sqlalchemy_url,)


@app.cell(hide_code=True)
def _(mo, cratedb_sqlalchemy_url):
    mo.md(
        """
        # Connect to CrateDB or CrateDB Cloud

        This notebook shows how to use Marimo and CrateDB, with Python dataframes and SQL.
        First, let's create a dataframe called `df`, populated with content from CrateDB's
        built-in `sys.summits` table.
        """
    )


@app.cell
def _(mo):
    settings = mo.vstack(
        [
            mo.md("Edit User"),
            first := mo.ui.text(label="First Name"),
            last := mo.ui.text(label="Last Name"),
        ]
    )

    organization = mo.vstack(
        [
            mo.md("Edit Organization"),
            org := mo.ui.text(label="Organization Name", value="..."),
            employees := mo.ui.number(
                label="Number of Employees", start=0, stop=1000
            ),
        ]
    )

    mo.ui.tabs(
        {
            "🧙‍♀ User": settings,
            "🏢 Organization": organization,
        }
    )
    return employees, first, last, org, organization, settings


@app.cell
def _(employees, first, last, mo, org):
    mo.md(
        f"""
        Welcome **{first.value} {last.value}** to **{org.value}**! You are 
        employee no. **{employees.value + 1}**.

        #{"🎉" * (min(employees.value + 1, 1000))} 
        """
    ) if all([first.value, last.value, org.value]) else mo.md(
        "Type a first and last name!"
    )
    return


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
    df = pd.read_sql(sql="SELECT * FROM sys.summits ORDER BY height DESC LIMIT 5", con=engine)

    print(df)
    df
    return df, engine, pd, sa


if __name__ == "__main__":
    app.run()
