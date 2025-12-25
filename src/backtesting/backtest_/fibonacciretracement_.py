from pandas import DataFrame

class FibonacciRetracement() : 
    
    def __init__(self , period : int = 50 , **kwargs) -> None : 

        self.period : int = period
    
    def add_fibonacci_retracement(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['high' , 'low']) : 
            raise ValueError('high and low required in df')
        
        rolling_high = df['high'].rolling(window = self.period).max()
        rolling_low = df['low'].rolling(window = self.period).min()
        diff = rolling_high - rolling_low
        
        df['fib_0'] = rolling_high
        df['fib_236'] = rolling_high - 0.236 * diff
        df['fib_382'] = rolling_high - 0.382 * diff
        df['fib_500'] = rolling_high - 0.500 * diff
        df['fib_618'] = rolling_high - 0.618 * diff
        df['fib_786'] = rolling_high - 0.786 * diff
        df['fib_100'] = rolling_low
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_fibonacci_retracement(df)

        return df