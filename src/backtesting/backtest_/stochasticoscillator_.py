from pandas import DataFrame

class StochasticOscillator():
    
    def __init__(self , period : int = 14 , smooth_k : int = 3 , smooth_d : int = 3 , **kwargs) -> None : 

        self.period : int = period
        self.smooth_k : int = smooth_k
        self.smooth_d : int = smooth_d
    
    def add_stochastic(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['high' , 'low' , 'prev_close']) : 
            raise ValueError('high, low, and prev_close required in df')
        
        lowest_low = df['low'].rolling(window = self.period).min()
        highest_high = df['high'].rolling(window = self.period).max()
        
        df['stoch_k'] = 100 * ((df['prev_close'] - lowest_low) / (highest_high - lowest_low))
        df['stoch_k'] = df['stoch_k'].rolling(window = self.smooth_k).mean()
        df['stoch_d'] = df['stoch_k'].rolling(window = self.smooth_d).mean()
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_stochastic(df)

        return df