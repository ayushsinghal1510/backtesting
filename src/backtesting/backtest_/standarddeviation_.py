from pandas import DataFrame

class StandardDeviation() : 
    
    def __init__(self , period : int = 20 , **kwargs) -> None : 

        self.period : int = period
    
    def add_std(self , df : DataFrame) -> DataFrame : 

        if 'prev_close' not in df.columns : 
            raise ValueError('prev_close not found in df')
        
        df['std_dev'] = df['prev_close'].rolling(window = self.period).std()
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_std(df)

        return df