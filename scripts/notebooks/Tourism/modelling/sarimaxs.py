import numpy as np
import pandas as pd

from scripts.python.tsa.utsmodel import *

def run_sarimax(country, y_vars,
                method: str,
                exog_var: list):

    # Set parameter range
    p, d, q = range(0, 3), range(0, 2), range(0, 3)
    P, D, Q, s = range(0, 3), range(0, 2), range(0, 3), [12]

    # list of all parameter combos
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = list(itertools.product(P, D, Q, s))
    all_param = list(itertools.product(pdq, seasonal_pdq))
    df = pd.DataFrame()

    for y_var in y_vars:

        mod = SARIMAXPipeline(country=country, y_var=y_var,
                              data=None,
                              exog_var=exog_var,
                              transform_method=method,
                              training_ratio=1,
                              verbose=False)
        mod.read_and_merge()
        display(mod.data.head(5))

        mod.transform()
        print(f"The Benchmark Evaluation for {y_var}".upper(), "\n")
        mod.get_benchmark_evaluation()
        print(
            f"Started to conduct stepwise searching for {y_var}".upper(), "\n")
        mod.stepwise_search()

        print(f"Started to conduct Grid searching for {y_var}".upper(), "\n")
        mod_msres = mod.manual_search(params=all_param)
        mod_msres.sort(key=lambda x: x[1])

        mod_swm = mod.stepwise_model
        if mod_msres[0][-1] == (mod_swm["order"], mod_swm["seasonal_order"]):
            best_mod = mod_msres[0][0]
            best_mod_pred = mod.get_prediction_df(
                best_mod, mod.test_size, mod.exog[-mod.test_size:])
        else:
            cv_models = []
            cv_models.append(pm.ARIMA(
                mod_swm["order"], mod_swm["seasonal_order"],  exog=mod.exog[:mod.training_size]))

            # Append top five GridSearch results
            for res in mod_msres[:5]:
                ic = res[1]
                if ic > 100: 
                    order, seasonal_order = res[-1]
                    model = pm.ARIMA(order, seasonal_order,
                                     exog=mod.exog[:mod.training_size])
                    cv_models.append(model)

            print(
                f"Started to conduct Cross-validation for {y_var}".upper(), "\n")
            mod_cv_comp = mod.compare_models(
                y=mod.transformed_y, exog=mod.exog, models=cv_models)
            best_cv_idx = np.nanargmin(mod_cv_comp["avg_error"])
            print(
                f"Best Models from Cross-validation is {cv_models[best_cv_idx]}", "\n")

            if best_cv_idx > 0:
                best_mod = mod_msres[best_cv_idx-1][0]
                best_mod_pred = mod.get_prediction_df(
                    best_mod, mod.test_size, mod.exog[-mod.test_size:])
        
        if method == "scaledlogit": 
            lower = mod.data[y_var].min() - 1
            upper = mod.data[y_var].max() + 1
            for col_idx, col in enumerate(best_mod_pred.columns):
                for row_idx, _ in enumerate(best_mod_pred[col]):
                    best_mod_pred.iloc[row_idx, col_idx] = mod.inverse_scaledlogit(
                        best_mod_pred.iloc[row_idx, col_idx], upper, lower)

        # Merge the prediction with actual values
        best_mod_pred.columns.name = None
        best_mod_pred = pd.concat(
            [mod.data[["date", y_var]], best_mod_pred], axis=1)
        best_mod_pred = (best_mod_pred[["date", y_var, "train_pred"]]
                         .rename({"train_pred": str(y_var) + "_pred"}, axis=1))

        if df.empty:
            best_mod_pred["total"] = mod.data["total"]
            df = best_mod_pred

        else:
            df = df.merge(best_mod_pred, how="left", on="date")

    df = df.drop_duplicates()
    return df