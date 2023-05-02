import pandas as pd
import numpy as np
import statsmodels
import sklearn
import os
from scripts.python.tsa.utsmodel import SARIMAXData
from scripts.python.tsa.ts_eval import *


class MultiTSData(SARIMAXData):
    SELECT_COLS = ["seats_arrivals_total", "seats_arrivals_intl",
                   "number_of_flights_total", "number_of_flights_intl"]

    def __init__(self, country: str, data=None):
        super().__init__(country, data)
        self.aviation_path = os.getcwd() + "/data/tourism/aviation_seats_flights_pic.xlsx"

    def read_and_merge(self,
                       avi_type: str = "passenger",
                       select_cols: list = SELECT_COLS):
        
        # Inherit from the read_and_merge method from SARIMAXData
        super().read_and_merge()
        
        # Process the Aviation Data
        avi = pd.read_excel(self.aviation_path)
        avi.columns = [col.lower().replace(" ", "") for col in avi.columns]
        avi["date"] = pd.to_datetime(avi["date"])
        avi["country"] = avi["country"].str.lower()
        avi = (avi[(avi.country == str(self.country)) & (avi.aircraft_type == str(avi_type))]
               .reset_index()
               .drop("index", axis=1))
        
        avi.index = avi["date"]
        avi = avi[select_cols].groupby(pd.Grouper(freq='M')).sum()
        
        # Drop last month because of the half-month data
        avi = avi.reset_index().iloc[:-1, :]
        avi["date"] = avi["date"] - pd.offsets.MonthBegin()
        
        self.data = avi.merge(self.data, how="left", on="date")
        display(self.data.head(5))


class VARPipeline(MultiTSData):
    def __init__(self, country, var_name, data=None):
        super().__init__(country, data)
        self.var_name = var_name

    def test_stationarity(self):
        from .ts_utils import get_adf_df
        adf_df = get_adf_df(self.data[self.var_name], self.var_name)
        
        order = 0
        while np.average(adf_df["p-value"]) > 0.05:
            self.stationary_data = self.data[self.var_name].diff().dropna()
            adf_df = get_adf_df(self.stationary_data, self.var_name)
            print(f"order = {order}: no stationarity obtained.")
            order += 1
        else:
           print(f"order = {order}: stationarity obtained.")
           display(adf_df)

    def transform(self):
        print("Transformation has finished.")

    def varma_search(self, exog: pd.DataFrame):

        from statsmodels.tsa.api import VARMAX
        from sklearn.model_selection import ParameterGrid

        param_grid = {'p': [1, 2, 3],
                      'q': [1, 2, 3],
                      'tr': ['n', 'c', 't', 'ct']}
        pg = list(ParameterGrid(param_grid))

        model_res = {
            "model": [],
            "result": []
        }
        
        for idx, params in enumerate(pg):
            print(f' Running for {params}')
            p = params.get('p')
            q = params.get('q')
            tr = params.get('tr')
            model = VARMAX(self.data[self.var_name],
                           exog=self.data[self.exog],
                           order=(p, q),
                           trend=tr).fit(disp=False)
            model_res["model"].append((p, q, tr))
            model_res["result"].append(model.aic)

        return model_res
    

class RatioPipe(MultiTSData):
    def __init__(self, country, var_name, data=None):
        super().__init__(country, data)
        self.var_name = var_name

    def transform(self):
        ratios = (self.data[self.var_name[0]])/(self.data[self.var_name[-1]])
        for idx, ratio in enumerate(ratios):
            if ratio >= 1 or ratio == 0:
                print("Abnormal value produced.")
                ratios[idx] = ((ratios[idx-1] + ratios[idx+1]))/2
        self.data["ratio"] = ratios

    def fit(self):
        import statsmodels.formula.api as smf
        self.data["quarter"] = self.data["date"].dt.quarter
        self.model_df = self.data[["date", "ratio", "covid", "quarter",
                                   "stringency_index", str(self.country) + "_travel"]]
        self.res = smf.wls(
            "ratio~covid * stringency_index + C(quarter) +" +
            str(self.country) + "_travel",
            data=self.model_df).fit()
        print(self.res.summary())