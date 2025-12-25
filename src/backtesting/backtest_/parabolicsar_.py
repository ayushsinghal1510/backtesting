from pandas import DataFrame

class ParabolicSAR() : 
    
    def __init__(self , af_start : float = 0.02 , af_increment : float = 0.02 , af_max : float = 0.2 , **kwargs) -> None : 

        self.af_start : float = af_start
        self.af_increment : float = af_increment
        self.af_max : float = af_max
    
    def add_parabolic_sar(self , df : DataFrame) -> DataFrame : 

        if not all(col in df.columns for col in ['high' , 'low']) : 
            raise ValueError('high and low required in df')
        
        psar = df['low'].iloc[0]
        bull = True
        af = self.af_start
        ep = df['high'].iloc[0]
        
        psar_values = [psar]
        
        for index in range(1 , len(df)) : 

            psar = psar + af * (ep - psar)
            
            if bull : 

                psar = min(psar , df['low'].iloc[index-1])

                if index > 1 : 
                    psar = min(psar , df['low'].iloc[index-2])
                
                if df['low'].iloc[index] < psar : 

                    bull = False
                    psar = ep
                    ep = df['low'].iloc[index]
                    af = self.af_start

                else : 

                    if df['high'].iloc[index] > ep : 

                        ep = df['high'].iloc[index]
                        af = min(af + self.af_increment , self.af_max)

            else : 

                psar = max(psar , df['high'].iloc[index-1])

                if index > 1 : 
                    psar = max(psar, df['high'].iloc[index-2])
                
                if df['high'].iloc[index] > psar : 

                    bull = True
                    psar = ep
                    ep = df['high'].iloc[index]
                    af = self.af_start

                else : 

                    if df['low'].iloc[index] < ep : 

                        ep = df['low'].iloc[index]
                        af = min(af + self.af_increment , self.af_max)
            
            psar_values.append(psar)
        
        df['psar'] = psar_values
        
        return df
    
    def __call__(self , df) -> DataFrame : 

        df = self.add_parabolic_sar(df)

        return df