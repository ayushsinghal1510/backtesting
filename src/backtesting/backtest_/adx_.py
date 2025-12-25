from pandas import DataFrame
import numpy as np 
import pandas as pd
from numpy import ndarray

class ADX() : 
    
    def __init__(self , period : int = 14 , **kwargs) -> None : 

        self.period : int = period
    
    def add_adx(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['high' , 'low' , 'prev_close']) : 

            raise ValueError('high, low, and prev_close required in df')
        
        # * Calculate +DM and -DM
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0) , 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0) , 0)
        
        # * Calculate True Range
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['prev_close'].shift())
        low_close = np.abs(df['low'] - df['prev_close'].shift())
        true_range = pd.concat([high_low , high_close , low_close] , axis = 1).max(axis = 1)
        
        # * Smooth the values
        atr = true_range.rolling(window = self.period).mean()
        plus_di = 100 * (plus_dm.rolling(window = self.period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window = self.period).mean() / atr)
        
        # * Calculate ADX
        dx : ndarray = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df['adx'] = dx.rolling(window=self.period).mean()
        df['plus_di'] = plus_di
        df['minus_di'] = minus_di
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_adx(df)

        return df
