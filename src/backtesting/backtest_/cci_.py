from pandas import DataFrame
import numpy as np

class CCI() : 
    
    def __init__(self , period : int = 20 , **kwargs) -> None : 

        self.period : int = period
    
    def add_cci(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['high' , 'low' , 'prev_close']) : 

            raise ValueError('high, low, and prev_close required in df')
        
        tp = (df['high'] + df['low'] + df['prev_close']) / 3
        sma_tp = tp.rolling(window = self.period).mean()
        mad = tp.rolling(window = self.period).apply(lambda value : np.abs(value - value.mean()).mean())
        
        df['cci'] = (tp - sma_tp) / (0.015 * mad)
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_cci(df)

        return df