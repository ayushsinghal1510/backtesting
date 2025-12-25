from pandas import DataFrame

class MACD() : 
    
    def __init__(self , fast : int = 12 , slow : int = 26 , signal : int = 9 , **kwargs) -> None : 

        self.fast : int = fast
        self.slow : int = slow
        self.signal : int = signal
    
    def add_macd(self , df : DataFrame) -> DataFrame : 

        if 'prev_close' not in df.columns : 

            raise ValueError('prev_close not found in df')
        
        ema_fast = df['prev_close'].ewm(span = self.fast , adjust = False).mean()
        ema_slow = df['prev_close'].ewm(span = self.slow , adjust = False).mean()
        
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span = self.signal , adjust = False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_macd(df)

        return df