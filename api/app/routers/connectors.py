import datetime
import secrets
import string
from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from api.app.core.security import get_current_user
from api.app.db.session import SessionLocal, get_db
from api.app.models.connector import Connector
from api.app.models.user import User
from api.app.schemas.connector import (
    ConnectorConnectionTestResponse,
    ConnectorJobRequest,
    ConnectorQueryRequest,
    ConnectorQueryResponse,
    ConnectorResponse,
    ConnectorSchemaResponse,
    ConnectorStatusResponse,
    PairingCodeResponse,
)
from api.app.services.connector_manager import (
    ConnectorJobError,
    ConnectorUnavailableError,
    connector_manager,
)

router = APIRouter(prefix="/connectors", tags=["Local Connectors"])


def _new_pairing_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _latest_connector(db: Session, user_id: str) -> Connector | None:
    return (
        db.query(Connector)
        .filter(Connector.user_id == user_id)
        .order_by(Connector.created_at.desc())
        .first()
    )


@router.post("/pairing-code", response_model=PairingCodeResponse)
def create_pairing_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pairing_code = _new_pairing_code()
    connector = Connector(
        user_id=current_user.id,
        name="Local Connector",
        pairing_code=pairing_code,
        status="pending",
    )
    db.add(connector)
    db.commit()
    db.refresh(connector)

    return PairingCodeResponse(
        connector_id=connector.id,
        pairing_code=connector.pairing_code,
        status=connector.status,
    )


@router.get("/status", response_model=ConnectorStatusResponse)
def get_connector_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connector = _latest_connector(db, current_user.id)
    if not connector:
        return ConnectorStatusResponse(status="offline")

    online = connector_manager.is_online(connector.id)
    status_value = "online" if online else connector.status
    if status_value == "online" and connector.status != "online":
        connector.status = "online"
        db.commit()
    elif not online and connector.status == "online":
        connector.status = "offline"
        db.commit()
        status_value = "offline"

    return ConnectorStatusResponse(
        connector_id=connector.id,
        status=status_value,
        last_seen_at=connector.last_seen_at,
    )


@router.get("", response_model=List[ConnectorResponse])
def list_connectors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Connector)
        .filter(Connector.user_id == current_user.id)
        .order_by(Connector.created_at.desc())
        .all()
    )


@router.post("/connections/test", response_model=ConnectorConnectionTestResponse)
async def test_connector_connection(
    payload: ConnectorJobRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await connector_manager.send_job(
            user_id=current_user.id,
            job_type="test_connection",
            payload={"connection_string": payload.connection_string},
            timeout_seconds=60,
        )
    except ConnectorUnavailableError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ConnectorJobError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ConnectorConnectionTestResponse(
        status="success",
        message=result.get("message") or "Database connection verified through local connector.",
    )


@router.post("/schema", response_model=ConnectorSchemaResponse)
async def extract_connector_schema(
    payload: ConnectorJobRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await connector_manager.send_job(
            user_id=current_user.id,
            job_type="extract_schema",
            payload={"connection_string": payload.connection_string},
        )
    except ConnectorUnavailableError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ConnectorJobError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    schema = result.get("schema") or {}
    return ConnectorSchemaResponse(
        status="success",
        tables_count=len(schema),
        schema=schema,
    )


@router.post("/query", response_model=ConnectorQueryResponse)
async def execute_connector_query(
    payload: ConnectorQueryRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await connector_manager.send_job(
            user_id=current_user.id,
            job_type="execute_sql",
            payload={
                "connection_string": payload.connection_string,
                "sql": payload.sql,
            },
        )
    except ConnectorUnavailableError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ConnectorJobError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ConnectorQueryResponse(
        status="success",
        rows=result.get("rows") or [],
        result_profile=result.get("result_profile") or {},
    )


@router.websocket("/ws")
async def connector_websocket(websocket: WebSocket):
    pairing_code = websocket.query_params.get("pairing_code")
    if not pairing_code:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = SessionLocal()
    connector = None
    try:
        connector = (
            db.query(Connector)
            .filter(Connector.pairing_code == pairing_code)
            .order_by(Connector.created_at.desc())
            .first()
        )
        if not connector:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()
        connector.status = "online"
        connector.last_seen_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        await connector_manager.register(connector.id, connector.user_id, websocket)
        await websocket.send_json(
            {
                "type": "registered",
                "connector_id": connector.id,
                "status": "online",
            }
        )

        while True:
            message = await websocket.receive_json()
            message_type = message.get("type")

            if message_type == "heartbeat":
                connector.last_seen_at = datetime.datetime.now(datetime.timezone.utc)
                connector.status = "online"
                db.commit()
                await websocket.send_json({"type": "heartbeat_ack"})
            elif message_type == "job_result":
                connector_manager.resolve_job(message)

    except WebSocketDisconnect:
        pass
    finally:
        if connector:
            await connector_manager.unregister(connector.id, connector.user_id, websocket)
            connector.status = "offline"
            connector.last_seen_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()
        db.close()
