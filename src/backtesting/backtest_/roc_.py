from pandas import DataFrame

class ROC() : 
    
    def __init__(self , period : int = 12 , **kwargs) -> None : 

        self.period : int = period
    
    def add_roc(self , df : DataFrame) -> DataFrame : 

        if 'prev_close' not in df.columns : 
            raise ValueError('prev_close not found in df')
        
        df['roc'] = ((df['prev_close'] - df['prev_close'].shift(self.period)) / 
                     df['prev_close'].shift(self.period)) * 100
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_roc(df)

        return df