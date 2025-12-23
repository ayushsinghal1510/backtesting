from io import StringIO
import operator
import os
from pandas import DataFrame
import numpy as np
import pandas as pd
from requests import Response
import requests

from .sma_ import SMA

class BACKTEST(SMA) : 

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

        if 'sma' in self.parameters : 

            SMA.__init__(self , **self.parameters['sma'])

            self.df = self.add_sma(self.df)

    def construct_df(self , symbol : str , interval : str) -> DataFrame : 

        stock_data : str = self.get_stock_data(symbol , interval)

        df : DataFrame = pd.read_csv(StringIO(stock_data))

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
                "percentage_return" : f"{round(roi_percentage ,  2)}%" , 
                "trade_count" : len(trades)
            }
        
        return {"message" : "No trades generated"}
