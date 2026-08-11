"""
Central schema manager.

Responsible for:
1. Loading schema from cache
2. Building schema if cache does not exist
3. Refreshing schema when requested
"""

from typing import Dict, Any
from sqlalchemy.engine import Engine

from SQL_Agent.schema.schema_cache import (
    cache_exists,
    load_schema_cache,
    refresh_schema_cache
)


def get_schema(
    engine: Engine,
    force_refresh: bool = False
) -> Dict[str, Any]:

    if force_refresh:
        return refresh_schema_cache(engine)

    if cache_exists():
        return load_schema_cache()

    return refresh_schema_cache(engine)
