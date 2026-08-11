import asyncio

from api.app.services.connector_manager import ConnectorManager


class FakeWebSocket:
    def __init__(self):
        self.sent = []
        self.closed = False

    async def send_json(self, message):
        self.sent.append(message)

    async def close(self):
        self.closed = True


def test_unregister_only_fails_jobs_for_disconnected_connector():
    async def run():
        manager = ConnectorManager()
        socket_one = FakeWebSocket()
        socket_two = FakeWebSocket()

        await manager.register("connector-one", "user-one", socket_one)
        await manager.register("connector-two", "user-two", socket_two)

        job_task = asyncio.create_task(
            manager.send_job("user-one", "test_connection", {"connection_string": "db"})
        )
        while not socket_one.sent:
            await asyncio.sleep(0)

        await manager.unregister("connector-two", "user-two", socket_two)

        job_id = socket_one.sent[0]["job_id"]
        manager.resolve_job(
            {
                "type": "job_result",
                "job_id": job_id,
                "status": "success",
                "result": {"message": "ok"},
            }
        )

        assert await job_task == {"message": "ok"}

    asyncio.run(run())


def test_stale_socket_unregister_does_not_remove_reconnected_socket():
    async def run():
        manager = ConnectorManager()
        old_socket = FakeWebSocket()
        new_socket = FakeWebSocket()

        await manager.register("connector-one", "user-one", old_socket)
        await manager.register("connector-one", "user-one", new_socket)

        await manager.unregister("connector-one", "user-one", old_socket)

        result_task = asyncio.create_task(
            manager.send_job("user-one", "extract_schema", {"connection_string": "db"})
        )
        while not new_socket.sent:
            await asyncio.sleep(0)

        job_id = new_socket.sent[0]["job_id"]
        manager.resolve_job(
            {
                "type": "job_result",
                "job_id": job_id,
                "status": "success",
                "result": {"schema": {}},
            }
        )

        assert await result_task == {"schema": {}}
        assert old_socket.closed is True

    asyncio.run(run())
