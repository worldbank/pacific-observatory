import os
import re
import pandas as pd
import tabula
import PyPDF2


def locate_table(
        filepath: str,
        search_string: str,
        ignore_case: bool = False
):
    search_lst = []
    reader = PyPDF2.PdfReader(filepath)

    for page_num, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text()
            hits = None
            if ignore_case == False:
                hits = re.search(search_string, page_text.lower())
            else:
                hits = re.search(
                    search_string, page_text.lower(), re.IGNORECASE)

            if hits:
                search_lst.append(page_num+1)
        except:
            pass

    return {"table_loc": search_lst}


def load_pdf(filepath: str,
             search_string: str,
             table_page: int,
             table_seq=0):

    table_loc = locate_table(filepath, search_string,
                             ignore_case=True)["table_loc"]
    if len(table_loc) != 0:
        table_page = table_loc[-1]
        dfs = tabula.read_pdf(filepath, pages=table_page, stream=True)
        if len(dfs) > 1:
            print(f"The page has {len(dfs)} tables.")
            df = dfs[table_seq]

        else:
            df = dfs[0]
            df.columns = df.iloc[0, :].to_list()
    else:
        dfs = tabula.read_pdf(filepath, pages="all", stream=True)
        df = dfs[table_page]
        df.columns = df.iloc[0, :].to_list()

    df = df.iloc[1:].reset_index().drop("index", axis=1)

    return df
