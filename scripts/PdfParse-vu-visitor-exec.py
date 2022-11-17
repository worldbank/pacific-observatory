from scripts.PdfParse import *

vu_lsts = os.listdir("data/tourism/vanuatu")


error_dict = {
    "file": [],
    "reason": []
}

error_dict

for file in vu_lsts:
    if ".pdf" in file:
        print(f"{file} has started")

        filepath = os.getcwd() + "/data/tourism/vanuatu/" + file

        df = load_pdf(filepath, "Visitor Arrivals by Purpose of Visit", 6)
        df.columns = df.iloc[0]

        df = df.dropna(thresh=4, axis=1).replace("-", 0)
        df = df.iloc[3:].reset_index().drop("index", axis=1)

        splited = df["Conferences Stop Over"].str.split(" ", n=2, expand=True)
        if len(splited.columns) == 2:
            splited.columns = ["Conference", "Stopover"]
        else:

        df = pd.concat([df, splited], axis=1)
        df = remove_separator(df)

        try:
            df = df.drop(["Conferences Stop Over", "Année", "Mois"], axis=1)

            if "Holidays" in df.columns:
                df["Holidays"] = df["Holidays"].str.replace(" ", "")
                if check_quality(df, ["Year", "Month"], "Visitors"):
                    saved_path = os.getcwd() + "/data/tourism/vanuatu/temp/" + file.split(".")[0] + ".csv"
                    df.to_csv(saved_path, encoding="utf-8")

            else:
                error_dict["file"].append(file)
                error_dict["reason"].append("Holidays column not found.")

        except:
            print(f"{file} has an error.")
            error_dict["file"].append(file)
            error_dict["reason"].append("Année or Mois column not found.")


len(splited.columns)
