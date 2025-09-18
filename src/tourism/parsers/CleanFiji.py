import os
import random
import numpy as np
import pandas as pd
import datetime

from scripts.python.PdfParse import *
from scripts.python.utils import *

scraping_folder = os.getcwd() + "/data/tourism/fiji/scraping/"
scraping_files = os.listdir(scraping_folder)
files_2019 = [scraping_folder +
              file for file in scraping_files if "2019" in file and "SA" not in file]

# A previous version for parsing tables from monthly news updates
total_2019 = pd.DataFrame()
for file in files_2019:
    month = (file.split("/")[-1]
             .replace("VA", "")
             .replace("2019", "")
             .replace(".pdf", "")
             .replace("_", "")
             .lower())

    df = tabula.read_pdf(file)[0].iloc[:, :2]

    df = (df.dropna()
          .reset_index()
          .drop("index", axis=1))

    if "Unnamed: 1" not in df.columns:
        df.iloc[:, -1] = df.iloc[:, -1].str.split(expand=True)[0]
        df.columns = ["country", str(month)]

    else:

        df = df.rename(
            {"Unnamed: 0": "country", "Unnamed: 1": str(month)}, axis=1)

    df = remove_separator(df)
    total_2019 = pd.concat([total_2019, df], axis=1)


total_2019 = total_2019.iloc[:, ~total_2019.columns.duplicated()]
colnames = (total_2019["country"].str.lower()
                                 .str.replace("cont.", "continental")
                                 .to_list())
total_2019 = total_2019.T
total_2019.columns = colnames
total_2019 = (total_2019.drop(index="country")
                        .reset_index()
                        .rename({"index": "month",
                                 "totalvisitors": "total"}, axis=1))

total_2019["year"] = 2019
cols = total_2019.columns.to_list()
cols = cols[-1:] + cols[:-1]
total_2019 = total_2019[cols]
total_2019.to_csv(
    os.getcwd() + "/data/tourism/fiji/intermediate/visitors_by_month_2019.csv",
    encoding="utf-8")


# A Speicific file from 2019 December
dec19 = scraping_folder + "VA_SA_Dec_2019.pdf"
dec19_df = load_pdf(dec19, "Table 1", table_page=1)[:26]
dec19_df = (dec19_df.drop(index=0)
            .reset_index()
            .drop(["index"], axis=1)
            .dropna(how="all", axis=1))

# Adjust the white space for expansion
splited_cols = dec19_df["KINGDOM EUROPE"].str.replace(
    r'\s+[,]', ',').str.split(expand=True, n=2)
splited_cols.columns = "KINGDOM EUROPE".split(" ")

# Drop the original column for spliting
dec19_df = (pd.concat([dec19_df, splited_cols], axis=1)
            .drop("KINGDOM EUROPE", axis=1))
dec19_df.columns = [col.lower() for col in dec19_df.columns]

# Remove all unnecessary separators
dec19_df = remove_separator(dec19_df)

# Fill the NA years
dec19_df["year"] = [2018 + (idx - 1) // 12 for idx in dec19_df.index]
dec19_df["month"] = [datetime.datetime.strptime(
    month, '%B').month for month in dec19_df.month]
dec19_df["dates"] = [str(year) + "-" + str(month) + "-01" for year,
                     month in zip(dec19_df.year, dec19_df.month)]
dec19_df["dates"] = pd.to_datetime(dec19_df["dates"])

# Create a mapping for existing column names
rename_dict = {"zealand": "newzealand",
               "korea": "southkorea",
               "islands": "pacificislands",
               "kingdom": "unitedkingdom",
               "asia": "restofasia",
               "europe": "continentaleurope"}
dec19_df = (dec19_df.rename(rename_dict, axis=1)
            .drop("month", axis=1))

dec19_cols = dec19_df.columns.to_list()
dec19_cols = dec19_cols[-1:] + dec19_cols[:-1]
dec19_df = dec19_df[dec19_cols]
dec19_df.to_csv(
    os.getcwd() + "/data/tourism/fiji/intermediate/visitors_by_origin_month_17_19.csv",
    encoding="utf-8")
