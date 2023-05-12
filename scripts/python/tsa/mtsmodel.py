import pandas as pd
import numpy as np
import statsmodels
import sklearn
import os
from statsmodels.tsa.api import VARMAX
from scripts.python.tsa.utsmodel import SARIMAXData
from scripts.python.tsa.ts_eval import *
from .ts_utils import *

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
        avi["country"] = avi["country"].str.lower().str.replace(" ", "_")
        avi = (avi[(avi.country == str(self.country)) & (avi.aircraft_type == str(avi_type))]
               .reset_index()
               .drop("index", axis=1))
        
        avi.index = avi["date"]
        avi = avi[select_cols].groupby(pd.Grouper(freq='M')).sum()
        
        # Drop last month because of the half-month data
        avi = avi.reset_index().iloc[:-1, :]
        avi["date"] = avi["date"] - pd.offsets.MonthBegin()
        
        self.data = (self.data.merge(avi, how="left", on="date")
                        .dropna()
                        .reset_index()
                        .drop("index", axis=1))

class VARPipeline(MultiTSData):
    def __init__(self, country, var_name, exog, data=None):
        super().__init__(country, data)
        self.var_name = var_name
        self.x1, self.x2 = var_name
        self.exog = exog

    def test_stationarity(self):
        from .ts_utils import get_adf_df
        adf_df = get_adf_df(self.data[self.var_name], self.var_name)
        
        order = 0
        while np.average(adf_df["p-value"]) > 0.05 and order < 2:
            self.stationary_data = self.data[self.var_name].diff().dropna()
            adf_df = get_adf_df(self.stationary_data, self.var_name)
            print(f"order = {order}: no stationarity obtained.")
            order += 1
            if order >= 2:
                break
        else:
           display(adf_df)
           print(f"order = {order}: stationarity obtained.")

    def transform(self, scaled_logit=True):
        if scaled_logit:
            self.x1_trans = scaledlogit_transform(self.data[self.x1])
            self.x2_trans = scaledlogit_transform(self.data[self.x2])
            self.scaled = pd.DataFrame([self.x1_trans, self.x2_trans]).T

    def varma_search(self):

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
            model = VARMAX(self.scaled,
                           exog=self.data[self.exog],
                           order=(p, q),
                           trend=tr).fit(disp=False)
            model_res["model"].append((p, q, tr))
            model_res["result"].append(model.aic)

        self.model_res_df = (pd.DataFrame(model_res)
                        .sort_values(by="result", ascending=True))
        self.p, self.q, self.tr = self.model_res_df.iloc[0, 0]
        print(f"Best P, Q, Trend Combination: {self.p, self.q, self.tr}")
    
    def fit(self):
        self.mod = VARMAX(self.scaled,
                    exog=self.data[self.exog],
                    order=(self.p, self.q),
                    trend=self.tr).fit(disp=False)
        print(self.mod.summary())

    def get_fittedvalues(self):
        self.fittedvalues = self.mod.fittedvalues
        rev_vals = []
        for raw_val in self.fittedvalues[self.x1]:
            rev_val = inverse_scaledlogit(
                raw_val, upper=self.data[self.x1].max()+1,
                lower=self.data[self.x1].min()-1
            )
            rev_vals.append(rev_val)
        self.data["pred_total"] = rev_vals

    def evaluate_models(self):
        naive_pred = naive_method(self.data[self.x1])
        mean_pred = mean_method(self.data[self.x1])
        
        benchmark = pd.DataFrame()
        for name, pred in zip(["naive", "mean", "VAR (scaled)"], [naive_pred, mean_pred, self.data.pred_total]):
            eval = calculate_evaluation(self.data[self.x1], pred)
            eval_df = pd.DataFrame(eval, index=[name])
            benchmark = pd.concat([benchmark, eval_df], axis=0)
        display(benchmark)


class RatioPipe(MultiTSData):
    def __init__(self, country, 
                 x1: str = "total",
                 x2: str = "seats_arrivals_intl",
                 data=None):
        super().__init__(country, data)
        self.x1 = x1 
        self.x2 = x2

    def transform(self):
        ratios = (self.data[self.x1])/(self.data[self.x2])
        for idx, ratio in enumerate(ratios):
            if ratio >= 1:
                print(f"Abnormal value produced with a value of {ratio}.")
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

    def get_prediction_df(self):
        pred_df = self.res.get_prediction().summary_frame()
        select_cols = ["date", "ratio", self.x1, self.x2]
        self.pred_df = pd.concat([self.data[select_cols], pred_df], axis=1)
        self.pred_df["pred_mean"] = self.pred_df["mean"] * self.pred_df[self.x2]
        display(self.pred_df.head(5))
        
        return self.pred_df
