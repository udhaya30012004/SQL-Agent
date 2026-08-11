import pandas as pd 
import numpy as np
import os 

'''
this file is used to extract meta data from from the csv
'''
def extract_data(df:pd.DataFrame,sample_size :int = 3) -> dict:
    ''' 
    function for extracting data were sample value = 5 which means df.head(5)
    '''
    schema ={
        'columns' : list(df.columns),
        'dtypes' : {
            columns : str(dtypes) # converts and maps the data type with the column names 
            for columns, dtypes in df.dtypes.items()
        },
        'row_count' : len(df),

        'sample_rows' :(df.head(sample_size)).to_dict(orient = 'records') # converts the first 3 rows to json 
        # oriented = records  means stores values as data frame records 
        }
    return schema
    
'''
output of the json looks like this 
{
    "columns": [
        "customer_id",
        "customer_name",
        "revenue",
        "region"
    ],

    "dtypes": {
        "customer_id": "int64",
        "customer_name": "object",
        "revenue": "float64",
        "region": "object"
    },

    "row_count": 1000,

    "sample_rows": [
        {
            "customer_id": 1,
            "customer_name": "John",
            "revenue": 1000,
            "region": "North"
        }
    ]
}'''
