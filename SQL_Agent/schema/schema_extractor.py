'''
extacts schema data deom the sql tables 
and builds the schema catlog which consist of all data from the tables in tat data base

'''


# pyrefly: ignore [missing-import]
from sqlalchemy import inspect
# pyrefly: ignore [missing-import]
from sqlalchemy.engine import Engine
from  typing import Dict, Any
from SQL_Agent.schema.partition_detection import detect_partitions


def _format_column_metadata(column: Dict[str, Any]) -> Dict[str, Any]:
    column_type = column["type"]
    metadata = {
        "name": column["name"],
        "type": str(column_type),
        "nullable": column["nullable"],
        "native_type": column_type.__class__.__name__,
    }

    enum_values = getattr(column_type, "enums", None)
    if enum_values:
        metadata["enum_values"] = list(enum_values)

    return metadata
   
def extract_schema(engine:Engine) -> Dict[str,Any]:
    '''
    extract all the table names  ad columns for sending it to llm for generation  '''

    inspector = inspect(engine)

    schema : Dict[str,Any] = {}

    # implementng the partition table function to skip those tables for cleaner embeding 

    partition_tables = detect_partitions(engine)

    table_inspector = inspector.get_table_names() # it stores all the table names

    for table in table_inspector:

        if table in partition_tables:
            print(f'[SCHEMA EXTRACTION ] : Skipping tables : {table}')
            continue
        # skipping those partition tables 

        columns = inspector.get_columns(table)
        '''
        pk -> Primary key of the table
        fks -> Foriegn Keys of the table
        '''
        pk = inspector.get_pk_constraint(table).get('constrained_columns',[])
        fks = []
        for fk in inspector.get_foreign_keys(table):
            fks.append(
                {
                    'column':fk.get('constrained_columns',[]),
                    'referred_table':fk.get('referred_table'),
                    'referred_columns':fk.get('referred_columns',[]),
                }
            )
        comment = ""

        try:
            comment = inspector.get_table_comment(table).get('text','')

        except Exception:
            comment = ""

        schema[table] = {
            'table_name' : table,
            'columns':[_format_column_metadata(column) for column in columns],
            'primary_keys' : pk,
            'foreign_keys' : fks,
            'description': comment or "",
        }
    return schema



