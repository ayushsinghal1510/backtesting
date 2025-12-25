from pandas import DataFrame

class MFI() : 
    
    def __init__(self , period : int = 14 , **kwargs) -> None : 

        self.period : int = period
    
    def add_mfi(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['high' , 'low' , 'prev_close' , 'volume']) : 
            raise ValueError('high, low, prev_close, and volume required in df')
        
        typical_price = (df['high'] + df['low'] + df['prev_close']) / 3
        money_flow = typical_price * df['volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1) , 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1) , 0)
        
        positive_mf = positive_flow.rolling(window = self.period).sum()
        negative_mf = negative_flow.rolling(window = self.period).sum()
        
        mfi_ratio = positive_mf / negative_mf
        df['mfi'] = 100 - (100 / (1 + mfi_ratio))
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_mfi(df)

        return df