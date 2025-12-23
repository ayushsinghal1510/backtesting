import os
from requests import Response
import requests


class API : 

    def __init__(self) -> None : pass 

    def get_stock_data(self , symbol : str , interval : int) -> dict : 

        response : Response = requests.get(
            url = 'https://www.alphavantage.co/query' , 
            params = {
                'fucntion' : 'TIME_SERIES_INTRADAY' , 
                'symbol' : symbol , 
                'interval' : interval , 
                'apikey' : os.environ['ALPHA_VANTAGE_API_KEY']
            }
        )

        return response.json()