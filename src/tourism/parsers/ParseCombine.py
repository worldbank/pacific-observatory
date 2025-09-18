import os
import pandas as pd

file_lst = os.listdir("data/tourism/vanuatu/byorigin")
file_lst = [os.getcwd() + "/data/tourism/vanuatu/byorigin/" + file for file in file_lst]

combined = pd.DataFrame()
for file in file_lst:
    df = pd.read_csv(file)
    combined = pd.concat([df, combined], axis=0)

combined.drop_duplicates()
