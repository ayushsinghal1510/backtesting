from pandas import DataFrame

class PivotPoints() : 
    
    def __init__(self , **kwargs) -> None : 

        pass
    
    def add_pivot_points(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['high' , 'low' , 'prev_close']) : 

            raise ValueError('high, low, and prev_close required in df')
        
        df['pivot'] = (df['high'] + df['low'] + df['prev_close']) / 3
        df['r1'] = 2 * df['pivot'] - df['low']
        df['s1'] = 2 * df['pivot'] - df['high']
        df['r2'] = df['pivot'] + (df['high'] - df['low'])
        df['s2'] = df['pivot'] - (df['high'] - df['low'])
        df['r3'] = df['high'] + 2 * (df['pivot'] - df['low'])
        df['s3'] = df['low'] - 2 * (df['high'] - df['pivot'])
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_pivot_points(df)

        return df
