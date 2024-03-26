#libraries
import requests
import config
import pandas as pd

class AlphaVantageAPI:

    def __init__(self, api_key=config.api_key):
        self.__api_key=api_key 
   

    def get_daily(self, ticker, output_size="full"):

    
        url=("https://www.alphavantage.co/query?"
        "function=TIME_SERIES_DAILY&"
        f"outputsize={output_size}&"
        f"symbol={ticker}&"
        f"apikey={self.__api_key}")

        response=requests.get(url)

        response_data=response.json()
        
        
        if "Time Series (Daily)" not in response_data.keys():
            raise Exception(f"Invalid API call. Check that the '{ticker}' is correct.")           
                        

        df=pd.DataFrame().from_dict(response_data["Time Series (Daily)"], orient="index", dtype=float) # keys to indx   
        df["symbol"]=ticker

        df.index=pd.to_datetime(df.index)
        df.index.name="date"        

        df.rename(columns={"1. open":"openning_price", 
                           "2. high":"high_price", 
                           "3. low":"low_price",  
                           "4. close":"closing_price",
                           "5. volume":"trading_volume"
                           },inplace=True)
        return df  
      
class SQLRepository:

    def __init__(self, connection):
        self.connection=connection

    def insert_df(self, table_name, records, if_exists="replace"):

        n_inserted=records.to_sql(table_name, con=self.connection, if_exists=if_exists)

        return {"Transaction Successful": True, "Records Inserted":n_inserted}


    def read_table(self, table_name, limit=None):

        if limit:
            sql=f"SELECT * FROM {table_name} LIMIT {limit}"

        else:
            sql=f"SELECT * FROM {table_name}"
            
        df=pd.read_sql(sql=sql, con=self.connection, parse_dates=["date"], index_col="date")

        return df 


# def main():

#     av=AlphaVantageAPI()    
#     connection=sqlite3.connect(config.db_name)
#     repo=SQLRepository(connection=connection)
#     tickers=["CPI", "MTNOY"]
#     for ticker in tickers:
#         df=av.get_daily(ticker)
#         report=repo.insert_df(table_name=ticker, records=df)  
        
# if __name__=="__main__":
#        main()

