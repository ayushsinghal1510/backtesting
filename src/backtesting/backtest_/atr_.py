from pandas import DataFrame
import numpy as np 
import pandas as pd

class ATR() : 
    
    def __init__(self , period : int = 14 , **kwargs) -> None : 

        self.period : int = period
    
    def add_atr(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['high' , 'low' , 'prev_close']) :  

            raise ValueError('high, low, and prev_close required in df')
        
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['prev_close'].shift())
        low_close = np.abs(df['low'] - df['prev_close'].shift())
        
        true_range = pd.concat([high_low , high_close , low_close] , axis = 1).max(axis = 1)
        df['atr'] = true_range.rolling(window = self.period).mean()
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_atr(df)

        return df