'''
Detects partition (child) tables in the connected database.

Supports:
  - PostgreSQL  (pg_inherits system catalog)
  - MySQL       (INFORMATION_SCHEMA.PARTITIONS)
  - SQL Server  (sys.tables + sys.partitions)

Returns a set of child table names that should be SKIPPED
during schema extraction, so only the parent table is kept.
'''

# pyrefly: ignore [missing-import]
from sqlalchemy.engine import Engine
# pyrefly: ignore [missing-import]
from sqlalchemy import text
from typing import Set


# DATABSE SPECIFIC QUERY FOR SKIPPING PARTITIONS

# PostgreSQL: Uses table inheritance (pg_inherits)
# Returns child table names that inherit from a parent table
POSTGRES_PARTITION_QUERY = text("""SELECT
    child_class.relname AS child_table
FROM
    pg_inherits
    JOIN pg_class AS child_class
        ON pg_inherits.inhrelid = child_class.oid
    JOIN pg_namespace
        ON child_class.relnamespace = pg_namespace.oid
WHERE
    pg_namespace.nspname = 'public'
    AND child_class.relkind = 'r'
    """)


# MySQL: Checks INFORMATION_SCHEMA.PARTITIONS for tables with named partitions
# Returns table names that have partitions (the parent name — partitions are internal in MySQL)
MYSQL_PARTITION_QUERY = text("""
    SELECT DISTINCT
        CONCAT(TABLE_NAME, '_', PARTITION_NAME) AS child_table
    FROM
        INFORMATION_SCHEMA.PARTITIONS
    WHERE
        TABLE_SCHEMA = DATABASE()
        AND PARTITION_NAME IS NOT NULL
""")


# SQL Server: Uses sys.tables and sys.partition_schemes
# Returns partition function-bound table names
MSSQL_PARTITION_QUERY = text("""
    SELECT
        t.name AS child_table
    FROM
        sys.tables t
        INNER JOIN sys.indexes i        ON t.object_id = i.object_id
        INNER JOIN sys.partition_schemes ps ON i.data_space_id = ps.data_space_id
    WHERE
        i.index_id IN (0, 1)
""")


# DETECTION WHICH DATABASE AND RUNNING THAT DABASES RESPECTIVE PARTITION DETECTION TABLE QUERY TO STORE AND SKIP IT DURING THE EMBEDDING

PARTITION_QUERIES = {
    "postgresql": POSTGRES_PARTITION_QUERY,
    "mysql":      MYSQL_PARTITION_QUERY,
    "mssql":      MSSQL_PARTITION_QUERY,
}


def detect_partitions(engine: Engine) -> Set[str]:
    """
    Detect partition child tables in the connected database.

    Uses the engine's dialect to pick the correct system catalog query.
    Returns a set of child table names that should be excluded
    from schema extraction.

    If the dialect is unsupported or the query fails, returns an empty set
    (no tables skipped — safe fallback).
    """
    dialect_name = engine.dialect.name  # e.g. 'postgresql', 'mysql', 'mssql'

    query = PARTITION_QUERIES.get(dialect_name)

    if query is None:
        print(f"[Partition Detection] Dialect '{dialect_name}' not supported — skipping detection.")
        return set()

    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            partition_tables = {row[0] for row in result}

        if partition_tables:
            print(f"[Partition Detection] Found {len(partition_tables)} "
                  f"partition child tables to skip: {sorted(partition_tables)}")
        else:
            print("[Partition Detection] No partition tables detected.")

        return partition_tables

    except Exception as e:
        print(f"[Partition Detection] Query failed: {e} — skipping detection.")
        return set()


