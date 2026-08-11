"""
SQL Agent Utility Router

Provides endpoints for testing database connections and
extracting schema metadata. All endpoints require authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from SQL_Agent.db.db_connector import connect_database
from SQL_Agent.schema.schema_extractor import extract_schema
from api.app.core.security import get_current_user
from api.app.models.user import User

router = APIRouter(prefix="/sql", tags=["SQL Agent Utilities"])


class ConnectionTestRequest(BaseModel):
    connection_string: str = Field(..., description="PostgreSQL DB connection string")


@router.post("/connect", status_code=status.HTTP_200_OK)
def test_connection(
    payload: ConnectionTestRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Test if the backend can connect to a specified PostgreSQL database.
    """
    try:
        engine = connect_database(payload.connection_string)
        # Test connection validity
        with engine.connect():
            pass
        return {"status": "success", "message": "Database connection verified successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {str(e)}",
        )


@router.post("/schema", status_code=status.HTTP_200_OK)
def get_database_schema(
    payload: ConnectionTestRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Test database connection and extract table columns, keys, and foreign relationship metadata.
    """
    try:
        engine = connect_database(payload.connection_string)
        schema = extract_schema(engine)
        return {
            "status": "success",
            "tables_count": len(schema),
            "schema": schema,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract database schema: {str(e)}",
        )
