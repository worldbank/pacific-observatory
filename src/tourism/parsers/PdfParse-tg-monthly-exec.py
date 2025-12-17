from scripts.PdfParse import *
from datetime import datetime

tonga_lsts = os.listdir("data/tourism/tonga")
filepaths = list()
for path in tonga_lsts:
    folder_path = os.getcwd() + "/data/tourism/tonga/"
    if "Dec" in path:
        filepaths.append(folder_path + path)
    elif "2021" and "Bulletin" in path:
        filepaths.append(folder_path + path)
    else:
        pass

filepaths

months = pd.DataFrame()

for file in filepaths[:-1]:
    print(file)

    df = load_pdf(file, "Monthly Arrival and Departure", table_page=-5)
    latest_year, year_idx, month_idx = split_time(df, "Period")
    month = df.iloc[month_idx, 0:4]
    start_year = detect_year(df.iloc[month_idx].iloc[0])

    month = (month.dropna(how="all").reset_index()
             .drop("index", axis=1))

    print(f"The file starts from {start_year}.")

    month = separate_data(month, "Air Ship", " ").drop("Air Ship", axis=1)
    month = remove_separator(month)
    month = month.replace(r'^\s*$', 0, regex=True)

    if check_quality(month, ["Period", "Year"], "Total") == False:
        name = file.split("/")[-1].split(".")[0]
        print("  ", name, "could go wrong!")

    generate_time(month, start_year)
    months = pd.concat([months, month], axis=0)

months = (months[["Year", "Period", "Air", "Ship", "Yacht", "Total"]]
          .drop_duplicates()
          .sort_values(by="Year")
          .reset_index()
          .drop("index", axis=1))

# Clean the datetime format
time = list()
for idx in months.index:
    month, year = months["Period"][idx], str(months["Year"][idx])
    if type(month) == str:
        try:
            YM = year + month
            time.append(datetime.strptime(YM, "%Y%B"))
        except:
            time.append(datetime.strptime(YM, "%Y%b"))
    else:
        time.append(month)

months["time"] = time
months = months.sort_values(by="time")

months

# Check for duplicates (e.g. Dec vs December in different years)
colnames = months.columns[~months.columns.isin(["Period"])]
indexes = months[colnames].drop_duplicates().index
months = months.iloc[indexes].reset_index().drop("index", axis=1)

# Save the file
months.to_csv("data/tourism/tonga/tonga_monthly_visitor.csv",
              encoding="utf-8")
