from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3, config
from data import SQLRepository
from model import GarchModel

class FitIn(BaseModel):
    use_new_data: bool
    n_observation: int
    ticker: str
    p:int
    q: int

class FitOut(FitIn):
    success: bool
    message: str

class PredictIn(BaseModel):
    ticker:str
    n_days:int

class PredictOut(PredictIn):
    success: bool
    forecast: dict
    message:str

def build_model(ticker, use_new_data):

    #create sqlite3 connection
    connection=sqlite3.connect(config.db_name, check_same_thread=False)

    #create a repository
    repo=SQLRepository(connection=connection)

    #create a model
    model=GarchModel(ticker=ticker,repo=repo, use_new_data=use_new_data)

    return model

app=FastAPI()

@app.post('/fit', status_code=200, response_model=FitOut)
def fit_model(request:FitIn):

    response=request.dict()

    try:
        model=build_model(ticker=request.ticker, use_new_data=request.use_new_data)

        #wrangle the data
        model.wrangle(request.n_observation)

        #fit the model
        model.fit(p=request.p, q=request.q)

        #save the model
        filename=model.dump()

        #  Add a status to the dictionary
        response["success"]=True

        response["message"]=f"Trained and saved {filename}"
    except Exception as e:
        response["success"]=False
        response["message"] = str(e)
    return response 

@app.post("/predict", status_code=200, response_model=PredictOut)
def get_prediction(request:PredictIn):
    
    response=request.dict()

    try:
        model=build_model(ticker=request.ticker, use_new_data=False)
        model.load()
    
        prediction=model.predict_volatility(horizon=request.n_days)

        response["success"]= True

        response["forecast"] =prediction

        response["message"] =""

    except Exception as e:

        response["success"]= False

        response["forecast"] ={}

        response["message"]= str(e)

    return response 


@app.get('/hello', status_code=200)
def hello():
    "return dictionary with greetings."
    return {"message":"Greetings to you :)"}