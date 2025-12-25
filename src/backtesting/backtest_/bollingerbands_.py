from pandas import DataFrame

class BollingerBands() : 
    
    def __init__(self , period : int = 20 , std_dev : float = 2.0 , **kwargs) -> None : 

        self.period : int = period
        self.std_dev : float = std_dev
    
    def add_bollinger_bands(self , df : DataFrame) -> DataFrame : 

        if 'prev_close' not in df.columns : 

            raise ValueError('prev_close not found in df')
        
        df['bb_middle'] = df['prev_close'].rolling(window = self.period).mean()
        std = df['prev_close'].rolling(window = self.period).std()
        
        df['bb_upper'] = df['bb_middle'] + (std * self.std_dev)
        df['bb_lower'] = df['bb_middle'] - (std * self.std_dev)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_bollinger_bands(df)

        return df
