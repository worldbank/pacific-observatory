"""
The module provides cross-validation class compatible with SARIMAX, VECM, and 
VARMAX (TBD) with option of Rolling and SlidingWindow methods.

Last Modified:
    2024-02-01
"""
from .scaler import ScaledLogitScaler, Differencing
from .ts_eval import calculate_evaluation
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.vector_ar.vecm import VECM
from pmdarima.model_selection import RollingForecastCV, SlidingWindowForecastCV
from tqdm import tqdm


class TimeSeriesCrossValidator:
    """
    The Time Series Cross-validation methods.

    To use:
        tscv = TimeSeriesCrossValidator(method="SARIMAX",
                                model_params=mod.stepwise_model,
                                data=mod.y,
                                exog_data=mod.exog,
                                cv_method="Rolling",
                                transformation="scaledlogit")

        initial_size = int(0.75 * len(mod.y))
        cv_errors = tscv.cross_validate(hyper_params={"inital": initial_size})
        print(model[2], np.mean([error["RMSE"] for error in cv_errors])) 
    """
    def __init__(self,
                 method: str,
                 model_params: dict,
                 data,
                 exog_data=None,
                 cv_method=None,
                 transformation=None):
        self.method = method
        self.model_params = model_params
        self.data = data
        self.exog_data = exog_data
        if cv_method not in ["Rolling", "SlidingWindow"]:
            raise AttributeError(
                "Must be either `Rolling` or `SlidingWindow`.")
        else:
            self.cv_method = cv_method
        if transformation not in ["scaledlogit", "difference", None]:
            raise AttributeError("No such transformation exists.")
        else:
            self.transformation = transformation
        self.scaler = None
        self.transformed_data = None
        self.cv = None

    def _transform(self):
        if self.transformation == 'scaledlogit':
            self.scaler = ScaledLogitScaler()
            self.scaler.fit(self.data)
            self.transformed_data = self.scaler.transform(self.data)
        elif self.transformation == "difference":
            self.scaler = Differencing()
            self.transformed_data = self.scaler.transform(self.data)
            self.exog_data = self.exog_data.iloc[self.transformed_data.index]
        else:
            self.transformed_data = self.data

    def _initialize_cv(self, hyper_params=None):
        if self.cv_method == "Rolling":
            self.cv = RollingForecastCV(
                h=12, step=1, initial=hyper_params["initial"])
        elif self.cv_method == "SlidingWindow":
            self.cv = SlidingWindowForecastCV(
                h=12, step=1, window_size=hyper_params["window_size"])

    def _fit_model(self, endog, exog):
        if self.method == "SARIMAX":
            order, seasonal_order = self.model_params["order"], \
                self.model_params["seasonal_order"]
            model = SARIMAX(endog,
                            exog=exog,
                            order=order,
                            seasonal_order=seasonal_order)
            return model.fit(disp=False)
        elif self.method == 'VECM':
            select_order = self.model_params["select_order"]
            model = VECM(endog,
                         exog=exog,
                         k_ar_diff=select_order,
                         coint_rank=1)
            return model.fit()

    def _predict_model(self, res, steps, exog, last_train_value):

        if self.method == "SARIMAX":
            predictions = res.forecast(steps=steps, exog=exog)
            predictions = self.scaler.inverse_transform(predictions)

        elif self.method == "VECM":
            predictions = res.predict(steps=steps, exog_fc=exog)
            if self.transformation == "difference":
                predictions = self.scaler.inverse_transform(
                    predictions, temporary=last_train_value)

        return predictions if predictions is not None else None

    def cross_validate(self, hyper_params):
        """
        Cross-validate for time series models. 

        Args:
          hyper_params (dict): contains the hyper-parameters for Rolling/SlidingWindow Forecast

        Return:
          errors (list): a list of dictionaries

        """
        self._transform()
        self._initialize_cv(hyper_params=hyper_params)
        cv_splits = list(self.cv.split(self.transformed_data))

        errors = []
        with tqdm(total=len(cv_splits)) as pbar:
            for train_idx, test_idx in cv_splits:
                train, test = self.transformed_data.iloc[train_idx], self.data.iloc[test_idx, 0]
                exog_train = self.exog_data.iloc[train_idx,
                                                 :] if self.exog_data is not None else None
                exog_test = self.exog_data.iloc[test_idx,
                                                :] if self.exog_data is not None else None
                res = self._fit_model(train, exog_train)
                predictions = self._predict_model(res, steps=len(exog_test), exog=exog_test,
                                                  last_train_value=train.iloc[-1, :].values)

                if len(test) == len(predictions):
                    predictions = predictions.iloc[:,
                                                   0] if self.method != "SARIMAX" else predictions
                    eval_metrics = calculate_evaluation(
                        test.values, predictions)
                    errors.append(eval_metrics)
                else:
                    raise AttributeError("The predicted data do not")
                pbar.update(1)

        return errors
