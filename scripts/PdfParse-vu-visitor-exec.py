from scripts.PdfParse import *

vu_lsts = os.listdir("data/tourism/vanuatu")
dec_lst = [file for file in vu_lsts if "Dec" in file]

error_dict = {
    "file": [],
    "reason": []
}

# Total Visitor
for file in dec_lst:
    if ".pdf" in file:

        print(f"{file} has started")
        filepath = os.getcwd() + "/data/tourism/vanuatu/" + file

        df = load_pdf(filepath, "Visitor Arrivals by Purpose of Visit", 6)
        df.columns = df.iloc[0]

        df = df.dropna(thresh=4, axis=1).replace("-", 0)
        df = df.iloc[3:].reset_index().drop("index", axis=1)

        try:
            col_lst = df.columns.to_list()
            stored_splited = ["Business, Stop",
                              "Cruiseship Other", "Conferences Stop Over"]

            for idx, val in enumerate(col_lst):
                if type(val) == str and val in stored_splited:
                    if val == "Business, Stop":
                        separate_data(df, "Business, Stop", ",")

                    elif val == "Conferences Stop Over":
                        splited = df[val].str.split(" ", n=2, expand=True)

                        if len(splited.columns) == 2:
                            splited.columns = [val.split(" ")[0], val.split(" ")[-1]]
                            df = pd.concat([df, splited], axis=1)

                        else:
                            print(f"{file} has incompatible column.")
                            error_dict["file"].append(file)
                            error_dict["reason"].append("Incompatible Column")

                    else:
                        splited = df[val].str.split(" ", n=2, expand=True)

                        if len(splited.columns) == 2:
                            splited.columns = val.split(" ")
                            df = pd.concat([df, splited], axis=1)
                        else:
                            print("Incompatible Column")
                            error_dict["file"].append(file)
                            error_dict["reason"].append("Incompatible Column")

            df = remove_separator(df)

            try:
                if "Holidays" in df.columns:
                    df["Holidays"] = df["Holidays"].str.replace(" ", "")
                    saved_path = os.getcwd() + "/data/tourism/vanuatu/temp/" + \
                        file.split(".")[0] + ".csv"
                    df.to_csv(saved_path, encoding="utf-8")

                else:
                    print("Holidays column not found.")
                    error_dict["file"].append(file)
                    error_dict["reason"].append("Holidays column not found.")

            except:
                print(f"{file} has an error.")
                error_dict["file"].append(file)
                error_dict["reason"].append("Année or Mois column not found.")

        except:
            error_dict["file"].append(file)
            error_dict["reason"].append("Column Error")


error_dict

# By Country
bycountry_err_lst = list()
for file in dec_lst:
    if ".pdf" in file:

        print(f"{file} has started")
        filepath = os.getcwd() + "/data/tourism/vanuatu/" + file


        try:
            df = load_pdf(filepath, "Visitor Arrivals by Usual Country of Residence", 7)
            df = df.iloc[:, :-2]

            headers, row1 = df.columns.to_list(), df.iloc[0].to_list()
            newheader = list()
            for header, row in zip(headers, row1):
                if type(header) != str:
                    newheader.append(str(row))
                else:
                    newheader.append(str(header))

            newheader[-1], newheader[5] = "Total", "Europe"

            df.columns = newheader
            df = df.iloc[2:].reset_index().drop("index", axis=1)
            df = remove_separator(df)

            if check_quality(df, ["Month", "Year"], "Total"):
                print(f"{file} pass the quality check.")
                saved_path = os.getcwd() + "/data/tourism/vanuatu/byorigin/" + \
                    file.split(".")[0] + ".csv"
                df.to_csv(saved_path, encoding="utf-8")
            else:
                print(f"{file} could have column errors")
                saved_path = os.getcwd() + "/data/tourism/vanuatu/byorigin/" + \
                    file.split(".")[0] + ".csv"
                df.to_csv(saved_path, encoding="utf-8")
                bycountry_err_lst.append(file)

        except:
            print(f"{file} could have errors in finding the table.")
            bycountry_err_lst.append(file)
