'''
this file is responsible for storing all the data from the table
1) it also loads the schema data 
2) saves the schema data 
3) reloads when use tables are added and sync with existing storage
'''

import json

from typing import Dict, Any
from SQL_Agent.schema.schema_extractor import extract_schema
from sqlalchemy.engine import Engine
from pathlib import Path
from SQL_Agent.db.db_connector import connect_database

CONNECTION_STRING = (
    "postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
)
engine = connect_database(CONNECTION_STRING)

CACHE_PATH = Path(__file__).with_name('schema_cache.json')

# check in CACHE FILE EXIST
def cache_exists(path: str | Path = CACHE_PATH) -> bool :
    return Path(path).exists()

def build_schema_cache(engine:Engine) -> Dict[str,Any]:
    return extract_schema(engine)

# to save this schema 

def save_schema_cache(schema: Dict[str, Any], path: str | Path = CACHE_PATH) -> None:
    with open(path,"w",encoding='utf-8') as f:
        json.dump(schema,f,indent = 2)

# function to load thise schemas 

def load_schema_cache(path: str | Path = CACHE_PATH) -> Dict[str, Any]:
    try:
        with open(path,'r',encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    
# refersh thse schema 

def refresh_schema_cache(engine: Engine, path: str | Path = CACHE_PATH) -> Dict[str, Any]:
    schema = build_schema_cache(engine)
    save_schema_cache(schema,path)
    return schema

