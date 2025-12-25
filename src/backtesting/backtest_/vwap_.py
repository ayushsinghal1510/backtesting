from pandas import DataFrame

class VWAP() : 
    
    def __init__(self , **kwargs) -> None : 

        pass
    
    def add_vwap(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['high' , 'low' , 'prev_close' , 'volume']) : 
            raise ValueError('high, low, prev_close, and volume required in df')
        
        typical_price = (df['high'] + df['low'] + df['prev_close']) / 3
        df['vwap'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_vwap(df)

        return df