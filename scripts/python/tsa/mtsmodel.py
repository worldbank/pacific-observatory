from .utsmodel import SARIMAXData


class VARData(SARIMAXData):
    def __init__(self, country: str, data=None):
        super().__init__(country, data)
        self.aviation_path = os.getcwd() + "/data/tourism/"


def varma_search(data: pd.DataFrame, var_name: list, exog: pd.DataFrame):

    from statsmodels.tsa.api import VARMAX
    from sklearn.model_selection import ParameterGrid

    param_grid = {'p': [1, 2, 3], 'q': [1, 2, 3], 'tr': ['n', 'c', 't', 'ct']}
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
        model = VARMAX(data[var_name],
                       exog=exog,
                       order=(p, q), trend=tr).fit(disp=False)
        model_res["model"].append((p, q, tr))
        model_res["result"].append(model.aic)

    return model_res