from pandas import DataFrame

class RSI() : 
    
    def __init__(self , period : int = 14 , **kwargs) -> None : 

        self.period : int = period
    
    def add_rsi(self , df : DataFrame) -> DataFrame : 

        if 'prev_close' not in df.columns : 
            raise ValueError('prev_close not found in df')
        
        delta = df['prev_close'].diff()
        gain = (delta.where(delta > 0 , 0)).rolling(window = self.period).mean()
        loss = (-delta.where(delta < 0 , 0)).rolling(window = self.period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_rsi(df)

        return df