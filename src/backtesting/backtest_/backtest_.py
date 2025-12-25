from io import StringIO
import operator
import os
from pandas import DataFrame
import numpy as np
import pandas as pd
from requests import Response
import requests

from .adx_ import ADX 
from .atr_ import ATR
from .bollingerbands_ import BollingerBands
from .cci_ import CCI 
from .ema_ import EMA 
from .fibonacciretracement_ import FibonacciRetracement
from .macd_ import MACD 
from .mfi_ import MFI 
from .obv_ import OBV 
from .parabolicsar_ import ParabolicSAR
from .pivotpoints_ import PivotPoints
from .roc_ import ROC 
from .rsi_ import RSI 
from .sma_ import SMA 
from .standarddeviation_ import StandardDeviation 
from .stochasticoscillator_ import StochasticOscillator
from .volumema_ import VolumeMA
from .vwap_ import VWAP

class BACKTEST(ADX , ATR , BollingerBands , CCI , EMA , FibonacciRetracement , MACD , MFI , OBV , ParabolicSAR , PivotPoints , ROC , RSI , SMA , StandardDeviation , StochasticOscillator , VolumeMA , VWAP) : 

    def __init__(self , symbol : str , interval : str , parameters : dict , strategy : dict , capital : int = 1_00_000 , slippage_pct : float = 0.0005 , brokerage_per_trade : int = 20 , tax_pct : float = 0.001) -> None : 

        self.ops = {
            '>' : operator.gt , 
            '<' : operator.lt , 
            '>=' : operator.ge , 
            '<=' : operator.le , 
            '==' : operator.eq , 
            '!=' : operator.ne
        }

        self.df = self.construct_df(symbol , interval)

        self.strategy = strategy

        self.capital : int= capital 
        self.slippage_pct : float = slippage_pct
        self.brokerage_per_trade : int = brokerage_per_trade 
        self.tax_pct : float = tax_pct
        self.parameters = parameters 

        if 'adx' in self.parameters : 

            ADX.__init__(self , **self.parameters['adx'])

            self.df = self.add_adx(self.df)

        if 'atr' in self.parameters :

            ATR.__init__(self , **self.parameters['atr'])

            self.df = self.add_atr(self.df)

        if 'bollingerbands' in self.parameters :

            BollingerBands.__init__(self , **self.parameters['bollingerbands'])

            self.df = self.add_bollinger_bands(self.df)

        if 'cci' in self.parameters :

            CCI.__init__(self , **self.parameters['cci'])

            self.df = self.add_cci(self.df)

        if 'ema' in self.parameters :

            EMA.__init__(self , **self.parameters['ema'])

            self.df = self.add_ema(self.df)

        if 'fibonacciretracement' in self.parameters : 

            FibonacciRetracement.__init__(self , **self.parameters['fibonacciretracement'])

            self.df = self.add_fibonacci_retracement(self.df)

        if 'macd' in self.parameters : 

            MACD.__init__(self , **self.parameters['macd'])

            self.df = self.add_macd(self.df)

        if 'mfi' in self.parameters : 

            MFI.__init__(self , **self.parameters['mfi'])

            self.df = self.add_mfi(self.df)

        if 'obv' in self.parameters :

            OBV.__init__(self , **self.parameters['obv'])

            self.df = self.add_obv(self.df)

        if 'parabolicsar' in self.parameters : 

            ParabolicSAR.__init__(self , **self.parameters['parabolicsar'])

            self.df = self.add_parabolic_sar(self.df)

        if 'pivotpoints' in self.parameters : 

            PivotPoints.__init__(self , **self.parameters['pivotpoints'])

            self.df = self.add_pivot_points(self.df)

        if 'roc' in self.parameters : 

            ROC.__init__(self , **self.parameters['roc'])

            self.df = self.add_roc(self.df)

        if 'rsi' in self.parameters :
             
            RSI.__init__(self , **self.parameters['rsi'])

            self.df = self.add_rsi(self.df)

        if 'sma' in self.parameters : 

            SMA.__init__(self , **self.parameters['sma'])

            self.df = self.add_sma(self.df)

        if 'standarddeviation' in self.parameters : 

            StandardDeviation.__init__(self , **self.parameters['standarddeviation'])

            self.df = self.add_standard_deviation(self.df)

        if 'stochasticoscillator' in self.parameters : 

            StochasticOscillator.__init__(self , **self.parameters['stochasticoscillator'])

            self.df = self.add_stochastic_oscillator(self.df)

        if 'volumema' in self.parameters : 

            VolumeMA.__init__(self , **self.parameters['volumema'])

            self.df = self.add_volume_ma(self.df)

        if 'vwap' in self.parameters :

            VWAP.__init__(self , **self.parameters['vwap'])

            self.df = self.add_vwap(self.df)

    def construct_df(self , symbol : str , interval : str) -> DataFrame : 

        stock_data : str = self.get_stock_data(symbol , interval)

        df : DataFrame = pd.read_csv(StringIO(stock_data))
        if ('close' not in df.columns or 'open' not in df.columns) : raise ValueError(f'Didndt received full data , {df.columns}')

        # * Standardize the columns
        df.columns = [col.lower() for col in df.columns]
        
        # * Sort
        if 'timestamp' in df.columns: 

            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp' , inplace = True)
        
        df.sort_index(ascending=True, inplace=True)
        
        # We shift close by 1 to represent "Previous Close" available at the start of today
        # This prevents look-ahead bias.
        df['prev_close'] = df['close'].shift(1)

        return df

    def get_stock_data(self , symbol : str , interval : str , function : str = 'TIME_SERIES_INTRADAY' , datatype : str = 'csv') -> str  : 
        
        response: Response = requests.get('https://www.alphavantage.co/query' , params = {
            'function' : function , 'symbol' : symbol , 'interval' : interval , 'apikey' : os.environ['API_KEY'] , 'datatype' : datatype
        })

        if response.status_code != 200 : 

            print(response.status_code , response.json())

            raise ValueError('Could not retreive value of stock')

        return response.text

    def construct_signal(self) -> DataFrame : 

        self.df['signal'] = 'Neutral'

        def evaluate(conditions) : 

            mask = pd.Series(True , index = self.df.index)

            for cond in conditions : 

                left = self.df[cond['left']] 
                # * right can be column or number
                right = self.df[cond['right']] if isinstance(cond['right'] , str) and cond['right'] in self.df.columns else cond['right']
                offset = cond['offset']

                if isinstance(offset , str) and offset.endswith('%') : 

                    pct_decimal = float(offset.replace('%' , '')) / 100

                    targe_value = right * (1 + pct_decimal)
                
                else : 

                    targe_value = right + float(offset)
                op = self.ops[cond['op']]

                mask &= op(left , targe_value)

            return mask

        if 'buy' in self.strategy : 

            buy_mask = evaluate(self.strategy['buy'])
            self.df.loc[buy_mask , 'signal'] = 'Buy'

        if 'sell' in self.strategy : 

            sell_mask = evaluate(self.strategy['sell'])
            self.df.loc[sell_mask , 'signal'] = 'Sell'

        return self.df

    def __call__(self) : 

        self.df = self.construct_signal()

        # We only care when the signal *changes* (e.g., from Sell to Buy)
        self.df['signal_changed'] = self.df['signal'] != self.df['signal'].shift(1)
        
        # Filter for rows where a signal change occurred (potential entry/exit points)
        # We drop NaNs created by rolling window/shifting
        signal_df = self.df[self.df['signal_changed']].dropna()
        
        # 4. Backtesting Loop
        trades = []
        in_position = False
        entry_details = {}
        
        for index, row in signal_df.iterrows() : 

            if row['signal'] == 'Buy' and not in_position : 

                # Entry with Slippage (Buying slightly higher)
                entry_price = row['open'] * (1 + self.slippage_pct)
                qty = int(self.capital / entry_price)
                
                # Entry Costs
                entry_tax = (entry_price * qty) * self.tax_pct
                total_entry_cost = self.brokerage_per_trade + entry_tax
                
                entry_details = {
                    'Entry Time' : index , 
                    'Entry Price' : entry_price , 
                    'Qty' : qty , 
                    'Entry Cost' : total_entry_cost
                }
                in_position = True
                
            elif row['signal'] == 'Sell' and in_position: 

                # Exit with Slippage (Selling slightly lower)

                exit_price = row['open'] * (1 - self.slippage_pct)
                qty = entry_details['Qty']
                
                # Exit Costs
                exit_tax = (exit_price * qty) * self.tax_pct
                total_exit_cost = self.brokerage_per_trade + exit_tax
                
                # CALCULATE NET PnL
                gross_pnl = (exit_price - entry_details['Entry Price']) * qty
                total_fees = entry_details['Entry Cost'] + total_exit_cost
                net_pnl = gross_pnl - total_fees
                
                trades.append({'Net PnL': net_pnl})
                in_position = False

        # --- COMPILE FINAL STATS ---
        if trades : 

            results_df = pd.DataFrame(trades)
            total_net_pnl = float(results_df['Net PnL'].sum())
            roi_percentage = (total_net_pnl / self.capital) * 100
            
            return {
                "starting_capital" : self.capital , 
                "total_net_profit_loss" : round(total_net_pnl ,  2) , 
                "percentage_return" : round(roi_percentage ,  2) , 
                "trade_count" : len(trades) , 
                'detailed_net_profit_loss' : results_df['Net PnL'].tolist()
            }
        
        return {"message" : "No trades generated"}
