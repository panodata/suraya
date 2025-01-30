# Source:
# https://docs.marimo.io/guides/working_with_data/dataframes.html
# https://github.com/marimo-team/marimo/blob/main/examples/sql/querying_dataframes.py
# https://github.com/crate/cratedb-toolkit/blob/3abe9830528fd708ef39394e578fe35918e4d651/cratedb_toolkit/cfr/marimo.py

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "duckdb",
#     "marimo",
#     "pandas==2.2.3",
#     "sqlalchemy-cratedb",
#     "sqlalchemy==2.0.36",
#     "python-dotenv==1.0.1",
# ]
# ///

import marimo

__generated_with = "0.10.13"
app = marimo.App(width="full", app_title="CrateDB Jobs Analysis")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _():
    import sqlalchemy as sa

    engine = sa.create_engine("crate://crate@localhost:4200/")
    return engine


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# sys.jobs_log""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Explore""")
    return


@app.cell
def _(mo):
    limitjl=mo.ui.slider(1,30000, step=20, value=100)
    limitjl
    return (limitjl,)


@app.cell(hide_code=True)
def _(engine, limitjl, pd):
    import ast  # Safely parse string representations of dictionaries
    import pandas as pd

    #df2 = pd.read_sql(sql="SELECT stmt, started, ended, username FROM sys.jobs_log limit 10", con=engine)
    #df2 = pd.read_sql(sql="SELECT * FROM sys.jobs_log limit {$limit.value} order by ended", con=engine)
    df2 = pd.read_sql(f"SELECT * FROM sys.jobs_log ORDER BY ended LIMIT {limitjl.value}", con=engine)

    # Convert epoch milliseconds to datetime
    df2['started'] = pd.to_datetime(df2['started'], unit='ms')
    df2['ended'] = pd.to_datetime(df2['ended'], unit='ms')
    df2['duration'] = (df2['ended'] - df2['started']).dt.total_seconds() * 1000


    # Example: Assuming the column is named 'metadata'
    df2['node'] = df2['node'].apply(lambda x: ast.literal_eval(x)['name'] if isinstance(x, str) else x['name'])

    #mo.ui.dataframe(df2)
    # Aggregating the 'duration' column
    #aggregated = df2['duration'].agg(['min', 'max', 'mean']).reset_index()

    # Rename the columns for clarity
    #aggregated.columns = ['aggregation', 'duration_min', 'duration_max', 'duration_mean']

    # Add aggregated values as new columns to df2
    #df2 = df2.join(aggregated[['duration_min', 'duration_max', 'duration_mean']].iloc[0], rsuffix='_agg')

    df2_next = df2
    df2_next = df2_next[["stmt", "started", "ended", "duration", "username", "node"]]
    df2_next
    return ast, df2, df2_next


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Slow Query Log""")
    return


@app.cell
def _(df2_next, mo):
    max_value = len(df2_next)
    slowq=mo.ui.slider(1,max_value, step=20, value=10)
    slowq
    return max_value, slowq


@app.cell
def _(df2_next, slowq):
    # Sort by 'duration' in descending order and get the top 10 slowest queries
    #slowest_queries = df2_next.sort_values(by='duration', ascending=False).head(10)
    # Sort by 'duration' in descending order and get the top 10 slowest queries
    slowq_value = int(slowq.value)  # Convert the slider value to an integer

    # Sort the DataFrame by 'duration' and get the top slowq_value rows
    slowest_queries = df2_next.sort_values(by='duration', ascending=False).head(slowq_value)
    #slowest_queries = df2_next.sort_values(by='duration', ascending=False).head(slowq.value)


    # Display the result
    print(slowest_queries[['stmt', 'duration']])

    # Display the result
    slowest_queries
    return slowest_queries, slowq_value


if __name__ == "__main__":
    app.run()
