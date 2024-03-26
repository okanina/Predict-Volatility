import pandas as pd
import numpy as np
import os, config, joblib, sqlite3
from glob import glob
from arch import arch_model
from data import AlphaVantageAPI, SQLRepository

class GarchModel:
    def __init__(self, ticker, repo, use_new_data=False):
        self.ticker=ticker
        self.repo=repo
        self.use_new_data=use_new_data
        self.model_directory=config.model_directory

    def wrangle(self, n_observations):
        '''This method extract table data from the database and calculate returns'''

        if self.use_new_data:
            api=AlphaVantageAPI()
            new_data=api.get_daily(ticker=self.ticker)
            self.repo.insert_df(self.ticker, records=new_data, if_exists="replace")

        df=self.repo.read_table(self.ticker, limit = n_observations+1)

        df.sort_index(ascending=True, inplace=True)

        df["returns"]= (df["closing_price"].pct_change()) *100

        self.data = df["returns"].dropna()
    
    def fit(self, p, q):

        '''This method fit the modl to data and calculate variance'''

        self.model=arch_model(self.data, p=p, q=q, rescale=False).fit(disp=0)
        self.aic=self.model.aic
        self.bic=self.model.bic

    def __clean_predictions(self, predictions):
        
        start_date=predictions.index[0] + pd.DateOffset(days=1)

        #range for a businessdays
        prediction_dates=pd.bdate_range(start=start_date, periods=predictions.shape[1])
        
        #prediction index in isoformat.
        prediction_index=[d.isoformat() for d in prediction_dates]

        data=predictions.values.flatten()

        prediction_index=pd.Series(data, prediction_index)

        return prediction_index.to_dict()
         
    def predict_volatility(self, horizon):

        prediction=self.model.forecast(horizon=horizon, reindex=False).variance**0.5

        predict_formatted=self.__clean_predictions(prediction)

        return predict_formatted
    
    def dump(self):
        '''saving model to self.model.directory'''

        # creating a directory
        os.makedirs(self.model_directory, exist_ok=True)

        timestamp=pd.Timestamp.now().isoformat()       

        filepath=os.path.join(self.model_directory, f"{timestamp}_{self.ticker}.pkl")

        #removing special characters
        filepath=filepath.replace(":", ".")

        with open(filepath, "wb") as file_obj:
            joblib.dump(self.model, file_obj)

        return filepath


    def load(self):

        pattern=os.path.join(self.model_directory, f"*{self.ticker}.pkl")

        try:
            model_path=sorted(glob(pattern))[-1]
        except IndexError:
            raise Exception(f"No file with {self.ticker} found.")
        
        #load model
        self.model = joblib.load(model_path)
        print(self.model)









