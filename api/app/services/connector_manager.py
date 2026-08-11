import asyncio
import datetime
import uuid
from typing import Any, Dict, Tuple

from fastapi import WebSocket


class ConnectorUnavailableError(Exception):
    pass


class ConnectorJobError(Exception):
    pass


class ConnectorManager:
    def __init__(self) -> None:
        self._connections: Dict[str, WebSocket] = {}
        self._user_connectors: Dict[str, str] = {}
        self._pending_jobs: Dict[str, Tuple[str, asyncio.Future]] = {}
        self._lock = asyncio.Lock()

    async def register(self, connector_id: str, user_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            old_socket = self._connections.get(connector_id)
            if old_socket:
                try:
                    await old_socket.close()
                except Exception:
                    pass
            self._connections[connector_id] = websocket
            self._user_connectors[user_id] = connector_id

    async def unregister(
        self,
        connector_id: str,
        user_id: str,
        websocket: WebSocket | None = None,
    ) -> None:
        async with self._lock:
            current_socket = self._connections.get(connector_id)
            if websocket is not None and current_socket is not websocket:
                return

            self._connections.pop(connector_id, None)
            if self._user_connectors.get(user_id) == connector_id:
                self._user_connectors.pop(user_id, None)

            for job_id, (job_connector_id, future) in list(self._pending_jobs.items()):
                if job_connector_id != connector_id:
                    continue
                if not future.done():
                    future.set_exception(ConnectorUnavailableError("Connector disconnected."))
                self._pending_jobs.pop(job_id, None)

    def is_online(self, connector_id: str) -> bool:
        return connector_id in self._connections

    async def send_job(
        self,
        user_id: str,
        job_type: str,
        payload: Dict[str, Any],
        timeout_seconds: int = 120,
    ) -> Dict[str, Any]:
        connector_id = self._user_connectors.get(user_id)
        if not connector_id:
            raise ConnectorUnavailableError("Local connector is not online.")

        websocket = self._connections.get(connector_id)
        if not websocket:
            raise ConnectorUnavailableError("Local connector is not online.")

        job_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending_jobs[job_id] = (connector_id, future)

        await websocket.send_json(
            {
                "type": "job",
                "job_id": job_id,
                "job_type": job_type,
                "payload": payload,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        )

        try:
            message = await asyncio.wait_for(future, timeout=timeout_seconds)
        finally:
            self._pending_jobs.pop(job_id, None)

        if message.get("status") == "failed":
            raise ConnectorJobError(message.get("error") or "Connector job failed.")

        return message.get("result") or {}

    def resolve_job(self, message: Dict[str, Any]) -> None:
        job_id = message.get("job_id")
        if not job_id:
            return

        pending_job = self._pending_jobs.get(job_id)
        if not pending_job:
            return

        _, future = pending_job
        if future and not future.done():
            future.set_result(message)


connector_manager = ConnectorManager()
