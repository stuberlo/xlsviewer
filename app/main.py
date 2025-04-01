from typing import Annotated
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os
import functools
import pandas as pd
import numpy as np

app = FastAPI()

# The file to load set from environment
filename = os.environ["FILENAME"]

# load file into pandas dataframe
# - nan replace for json compatability
# - set all to string for string search in all columns
df = pd.read_excel(f"app/data/{filename}").replace(np.nan, None).astype(str)


# main page at root endpoint
@app.get("/")
def root():
    return FileResponse("app/index.html")


# main search function endpoint
# input:
#   - list of columns with search string (column,search_string)
#   - current page for pagination
@app.get("/search/")
def search_rows(q: Annotated[list[str] | None, Query()] = [], page: int = 1):

    # extract columns and search strings from query
    column_search = {
        query.split(",")[0]: ",".join(query.split(",")[1:]).strip() for query in q
    }

    # columns with non empty filters
    filter_search = [(col, val) for col, val in column_search.items() if val]

    # if filters are set, use pandas to filter out a new dataframe
    # otherwise just use the whole dataframe
    if filter_search:
        filtered_df = df.loc[
            functools.reduce(
                np.logical_and,
                (df[col].str.contains(val) for col, val in filter_search),
            ),
            list(column_search),  # keep data from all columns, also non filtered ones
        ]
    else:
        filtered_df = df

    # linear search in filtered dataframe with pagination
    rows_per_page = 15
    total_count = filtered_df.shape[0]
    page_count = np.ceil(total_count / rows_per_page)
    from_row, to_row = (page - 1) * rows_per_page + 1, min(
        page * rows_per_page, total_count
    )
    count = 1
    search_result = []
    for i, row in filtered_df.iterrows():
        if from_row <= count <= to_row:
            search_result.append(row.to_dict())
        elif count > to_row:
            break
        count += 1
    return {
        "columns": list(column_search),
        "rows": search_result,
        "count": total_count,
        "page": page,
        "page_count": page_count,
        "showing_range": "%d-%d" % (from_row, to_row),
    }


# get meta information about file
@app.get("/getcolumns")
def get_columns():
    return {"columns": list(df.columns), "filename": filename}
