from contextlib import asynccontextmanager
from logging import Logger
import os
from .loader import load_all_clients
from .api import API
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .services import env_str_to_bool , env_str_to_list
import uvicorn

from dotenv import load_dotenv
from .backtest_ import BACKTEST

load_dotenv()

class AppState : 

    config : dict
    logger : Logger
    api_client : API

state = AppState()

@asynccontextmanager
async def lifespan(app : FastAPI) : 

    api_client , config , logger = load_all_clients()
    
    state.config = config
    state.logger = logger
    state.api_client = api_client
    
    logger.info("System Startup: Models and Config Loaded.")
    
    yield
    
    logger.info("System Shutdown.")

app = FastAPI(lifespan = lifespan)

app.add_middleware(
    CORSMiddleware , 
    allow_origins = env_str_to_list(os.environ['ALLOWED_ORIGINS']) , 
    allow_credentials = env_str_to_bool(os.environ['ALLOWED_CREDENTIALS']) , 
    allow_methods = env_str_to_list(os.environ['ALLOWED_METHODS']) , 
    allow_headers = env_str_to_list(os.environ['ALLOWED_HEADERS']) 
)

@app.post('/backtest')
async def backetest(request : Request) : 

    data = await request.json()

    if ('symbol' not in data or 'interval' not in data or 'parameters' not in data or 'strategy' not in data) : raise HTTPException(status_code = 400 , detail = '"symbol" or "interval" was not provided')

    symbol = data['symbol']
    interval = data['interval']
    parameters = data['parameters']
    strategy = data['strategy']

    backtest : BACKTEST = BACKTEST(symbol , interval , parameters , strategy)
    results = backtest()
    
    return results



def main() : uvicorn.run(
    app , 
    host = '0.0.0.0' , 
    port = 8888
)