'''
this file is used for connecting with multiple DATA BASES 

but here we only use Realational database can be connected such as 
1) MYSQL
2)ORACLE
3)POSTGRESQL
4)SQL LITE
4)MICROSOFR SQL SERVER
'''
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from SQL_Agent.db import db_store

def connect_database(connection_string:str):
    '''
    this function creates a engine with connection string and verifues the 
    connections'''

    try:
        engine = create_engine(connection_string)
        # verifies connetion
        with engine.connect() as conn:
            pass
        db_store.GLOBAL_ENGINE = engine

        print('DATABASE CONNECTION SUCCESSFUL ')

        return engine
    
    except SQLAlchemyError as e:
        raise Exception (
            f"DataBase Connection Failed :{str(e)}"
        )
    


    
