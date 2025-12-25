from pandas import DataFrame

class SMA() : 

    def __init__(self , rolling_window : int = 20 , **kwargs) -> None : 

        self.rolling_window : int = rolling_window

    def add_sma(self , df : DataFrame) -> DataFrame : 

        if 'prev_close' not in df.columns : 
            
            raise ValueError('prev_close not found in df')

        df['sma'] = df['prev_close'].rolling(window = self.rolling_window).mean()

        return df

    def __call__(self , df) -> DataFrame : 

        df = self.add_sma(df)

        return df