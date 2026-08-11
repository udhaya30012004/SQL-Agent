# Agentic Data Analyst Backend

FastAPI backend for the SQL/Pandas agent system. Backend metadata such as users,
chat sessions, and chat messages is stored in PostgreSQL database
`agent_backend`.

## Prerequisites

- Windows PowerShell
- Python virtual environment already created at `.\venv`
- PostgreSQL running locally
- PostgreSQL database created:

```powershell
createdb -U postgres agent_backend
```

- `.env` configured in the project root with at least:

```env
GROQ_API='your_groq_api_key'
PINECONE_API_KEY='your_pinecone_api_key'
PINECONE_INDEX_NAME='sql-agent'
SECRET_KEY='your_secret_key'
DATABASE_URL='postgresql+psycopg2://postgres:1234@localhost:5432/agent_backend'
```

Update the username, password, host, and port in `DATABASE_URL` if your local
PostgreSQL setup is different.

## Start The Backend

Run these commands from the project root:

```powershell
cd F:\DA_Project
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once for the current terminal:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

Install or update dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install -r api\requirements.txt
```

Reset backend metadata tables:

```powershell
python -m api.app.db.reset_metadata_db
```

Start the FastAPI app:

```powershell
python -m uvicorn api.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Quick Backend Checks

Verify the app imports:

```powershell
python -c "from api.app.main import app; print(app.title)"
```

Verify PostgreSQL metadata tables:

```powershell
python -c "from sqlalchemy import inspect; from api.app.db.session import engine; print(inspect(engine).get_table_names(schema='public'))"
```

Expected tables:

```text
users
chat_sessions
chat_messages
```

Verify table row counts:

```powershell
python -c "from api.app.db.session import SessionLocal; from api.app.models.user import User; from api.app.models.chat import ChatSession, ChatMessage; db=SessionLocal(); print(db.query(User).count(), db.query(ChatSession).count(), db.query(ChatMessage).count()); db.close()"
```

## API Flow

1. Create user:

```http
POST /api/v1/auth/signup
```

2. Login:

```http
POST /api/v1/auth/login
```

3. Use the returned access token as:

```http
Authorization: Bearer <access_token>
```

4. Create a SQL chat session:

```http
POST /api/v1/chat/sessions
```

Example body:

```json
{
  "agent_type": "sql",
  "title": "SQL Chat"
}
```

5. Ask the SQL agent:

```http
POST /api/v1/chat/
```

Example body:

```json
{
  "session_id": "your-session-id",
  "question": "How many films are in the database?"
}
```

Optional custom SQL target database:

```json
{
  "session_id": "your-session-id",
  "question": "How many films are in the database?",
  "connection_string": "postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
}
```

## Important Commands

Stop the server:

```powershell
Ctrl+C
```

Reset only backend metadata tables:

```powershell
python -m api.app.db.reset_metadata_db
```

Run with a different port:

```powershell
python -m uvicorn api.app.main:app --host 127.0.0.1 --port 8001 --reload
```

Deactivate the virtual environment:

```powershell
deactivate
```

## Run With Docker

This project includes Docker packaging for the FastAPI backend and Vite/React
frontend.

Prerequisites:

- Docker Desktop installed and running
- A valid `.env` file in the project root

Start the full app from the project root:

```powershell
docker compose up --build
```

Open the frontend:

```text
http://localhost:3000
```

Open the backend API docs through the frontend proxy:

```text
http://localhost:3000/docs
```

The Docker setup uses a persistent Docker volume for backend metadata:

```env
DATABASE_URL=sqlite:////app/data/agent_backend.db
```

If the SQL agent needs to connect to PostgreSQL running on your Windows host,
use `host.docker.internal` in `CONNECTION_STRING`, for example:

```env
CONNECTION_STRING=postgresql+psycopg2://postgres:1234@host.docker.internal:5432/pagila
```

To stop the app:

```powershell
docker compose down
```

To stop the app and remove Docker-managed metadata/chart volumes:

```powershell
docker compose down -v
```
