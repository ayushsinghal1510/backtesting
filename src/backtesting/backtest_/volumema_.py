from pandas import DataFrame

class VolumeMA() : 
    
    def __init__(self , period : int = 20 , **kwargs) -> None : 

        self.period : int = period
    
    def add_volume_ma(self , df : DataFrame) -> DataFrame : 

        if 'volume' not in df.columns : 
            raise ValueError('volume not found in df')
        
        df['volume_ma'] = df['volume'].rolling(window = self.period).mean()
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_volume_ma(df)

        return df