from pandas import DataFrame

class EMA() : 
    
    def __init__(self , span : int = 20 , **kwargs) -> None : 
        
        self.span : int = span
    
    def add_ema(self , df : DataFrame) -> DataFrame : 
        
        if 'prev_close' not in df.columns : 
            
            raise ValueError('prev_close not found in df')
        
        df['ema'] = df['prev_close'].ewm(span = self.span , adjust = False).mean()
        
        return df
    
    def __call__(self , df) -> DataFrame : 
        
        df = self.add_ema(df)
        
        return df