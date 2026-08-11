import argparse
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlencode, urlparse

import websockets

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from SQL_Agent.db.db_connector import connect_database
from SQL_Agent.db import db_store
from SQL_Agent.nodes.execute import execute_sql
from SQL_Agent.nodes.validate import validate_query
from SQL_Agent.schema.schema_extractor import extract_schema


HEARTBEAT_SECONDS = 25


def _backend_ws_url(backend: str, pairing_code: str) -> str:
    parsed = urlparse(backend)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    netloc = parsed.netloc
    base_path = parsed.path.rstrip("/")
    query = urlencode({"pairing_code": pairing_code})
    return f"{scheme}://{netloc}{base_path}/api/v1/connectors/ws?{query}"


async def _heartbeat(websocket) -> None:
    while True:
        await asyncio.sleep(HEARTBEAT_SECONDS)
        await websocket.send(json.dumps({"type": "heartbeat"}))


def _json_safe_records(df):
    return json.loads(df.to_json(orient="records", date_format="iso"))


def _test_connection(payload: dict) -> dict:
    connection_string = payload["connection_string"]
    engine = connect_database(connection_string)
    try:
        pass
    finally:
        engine.dispose()
        db_store.GLOBAL_ENGINE = None
    return {"message": "Database connection verified from local connector."}


def _extract_schema(payload: dict) -> dict:
    connection_string = payload["connection_string"]
    engine = connect_database(connection_string)
    try:
        schema = extract_schema(engine)
    finally:
        engine.dispose()
        db_store.GLOBAL_ENGINE = None
    return {"schema": schema}


def _execute_sql(payload: dict) -> dict:
    connection_string = payload["connection_string"]
    sql = validate_query(payload["sql"])
    engine = connect_database(connection_string)
    try:
        df = execute_sql(sql)
    finally:
        engine.dispose()
        db_store.GLOBAL_ENGINE = None

    from SQL_Agent.analytics.result_profile import profile_dataframe

    return {
        "rows": _json_safe_records(df),
        "result_profile": profile_dataframe(df),
    }


def _run_job(job_type: str, payload: dict) -> dict:
    if job_type == "test_connection":
        return _test_connection(payload)
    if job_type == "extract_schema":
        return _extract_schema(payload)
    if job_type == "execute_sql":
        return _execute_sql(payload)
    raise ValueError(f"Unsupported connector job type: {job_type}")


async def _handle_job(websocket, message: dict) -> None:
    job_id = message["job_id"]
    job_type = message["job_type"]
    payload = message.get("payload") or {}

    try:
        result = await asyncio.to_thread(_run_job, job_type, payload)
        response = {
            "type": "job_result",
            "job_id": job_id,
            "status": "success",
            "result": result,
        }
    except Exception as exc:
        response = {
            "type": "job_result",
            "job_id": job_id,
            "status": "failed",
            "error": str(exc),
        }

    await websocket.send(json.dumps(response, default=str))


async def run_connector(backend: str, pairing_code: str) -> None:
    ws_url = _backend_ws_url(backend, pairing_code)
    retry_seconds = 5

    while True:
        try:
            print(f"Connecting to {ws_url}")
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as websocket:
                print("Connector online. Waiting for jobs.")
                heartbeat_task = asyncio.create_task(_heartbeat(websocket))
                try:
                    async for raw_message in websocket:
                        message = json.loads(raw_message)
                        if message.get("type") == "job":
                            await _handle_job(websocket, message)
                        elif message.get("type") == "registered":
                            print(f"Registered connector {message.get('connector_id')}")
                finally:
                    heartbeat_task.cancel()
        except KeyboardInterrupt:
            print("Connector stopped.")
            return
        except Exception as exc:
            print(f"Connector disconnected: {exc}")
            print(f"Retrying in {retry_seconds} seconds...")
            await asyncio.sleep(retry_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="SQL Agent local database connector")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start the local connector")
    start_parser.add_argument("--backend", required=True, help="Backend origin, e.g. https://sql-agent-jwi7.onrender.com")
    start_parser.add_argument("--pairing-code", required=True, help="Pairing code from the web app")

    args = parser.parse_args()

    if args.command == "start":
        asyncio.run(run_connector(args.backend.rstrip("/"), args.pairing_code.strip()))


if __name__ == "__main__":
    main()
