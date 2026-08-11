from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class PairingCodeResponse(BaseModel):
    connector_id: str
    pairing_code: str
    status: str


class ConnectorStatusResponse(BaseModel):
    connector_id: Optional[str] = None
    status: str
    last_seen_at: Optional[datetime] = None


class ConnectorJobRequest(BaseModel):
    connection_string: str


class ConnectorQueryRequest(ConnectorJobRequest):
    sql: str


class ConnectorConnectionTestResponse(BaseModel):
    status: str
    message: str


class ConnectorSchemaResponse(BaseModel):
    status: str
    tables_count: int
    schema: Dict[str, Any]


class ConnectorQueryResponse(BaseModel):
    status: str
    rows: list[Dict[str, Any]]
    result_profile: Dict[str, Any]


class ConnectorResponse(BaseModel):
    id: str
    name: str
    status: str
    last_seen_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
