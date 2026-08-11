'''
this files is  used to exectue code generated form the llm 

'''

import pandas as pd
def execute_code(code:str,df:pd.DataFrame):
    '''
    execute llm generated ppandas code fir processing the Data Frane
    '''
    local_scope = {
        'df' : df,
        'result':None
    } 

    try:
        exec(code,
             {},
             local_scope)
        return local_scope['result']
    
    except Exception as e:
        raise Exception(
            f'Code Execution Failed :\n{str(e)}'
        )