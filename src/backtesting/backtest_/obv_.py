from pandas import DataFrame

class OBV() : 
    
    def __init__(self , **kwargs) -> None : 

        pass
    
    def add_obv(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['prev_close' , 'volume']) : 
            raise ValueError('prev_close and volume required in df')
        
        obv = [0]
        for index in range(1 , len(df)) : 

            if df['prev_close'].iloc[index] > df['prev_close'].iloc[index-1] : 
                obv.append(obv[-1] + df['volume'].iloc[index])

            elif df['prev_close'].iloc[index] < df['prev_close'].iloc[index-1] : 
                obv.append(obv[-1] - df['volume'].iloc[index])

            else : 
                obv.append(obv[-1])
        
        df['obv'] = obv
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_obv(df)

        return df