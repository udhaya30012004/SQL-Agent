# SQL Agent Local Connector

MVP connector for bridging the Render backend to a database reachable from the
user's machine.

## Run

```powershell
pip install -r local_connector/requirements.txt
python local_connector/connector.py start --backend https://sql-agent-jwi7.onrender.com --pairing-code YOURCODE
```

The connector opens an outbound WebSocket to the backend and waits for jobs:

- `test_connection`
- `extract_schema`
- `execute_sql`

For the MVP, connection strings are forwarded by the backend to the connector
per job. Do not run this connector with untrusted backend URLs.
