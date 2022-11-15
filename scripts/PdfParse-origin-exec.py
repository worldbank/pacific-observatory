from scripts.PdfParse import *
import re

tonga_lsts = os.listdir("data/tourism/tonga")

error_lsts = list()
for file in tonga_lsts:
    if ".pdf" in file:
        print(f"{file} has started")

        try:
            filepath = os.getcwd() + "/data/tourism/tonga/" + file

            df = load_pdf(filepath, "Total Visitors by Usual Residence and Purpose of Visit",
                          table_page=5, table_seq=-1)

            df = df.dropna(how="all", axis=1)

            colname_lst = df.iloc[0].to_list()
            colname_lst[0:2] = ["Country", "Total"]
            df.columns = colname_lst

            df = separate_data(df, "Conference Friends").drop("Conference Friends", axis=1)
            df = (df.iloc[1:-2, :]
                    .dropna(how="all", axis=1)
                    .reset_index().
                    drop("index", axis=1))

            saved_path = os.getcwd() + "/data/tourism/tonga/temp/" + file.split(".")[0] + ".csv"

            df.to_csv(saved_path, encoding="utf-8")

        except:
            print(f"{file} has an error.")
            error_lsts.append(file)

with open(os.getcwd() + "/data/tourism/tonga/temp/error.txt", "w") as file:
    file.write("\n".join(error_lsts))
