"""
Chat Router

All endpoints are protected by JWT authentication.
Sessions are scoped to the authenticated user — a user can only
see, create, and interact with their own sessions.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.app.core.security import get_current_user
from api.app.db.session import get_db
from api.app.models.chat import ChatMessage, ChatSession
from api.app.models.user import User
from api.app.schemas.chat import (
    ChatMessageResponse,
    ChatRequest,
    ChatSessionResponse,
    SessionCreateRequest,
)
from api.app.services.sql_agent_service import run_sql_agent
from api.app.services.pandas_agent_service import run_pandas_agent

router = APIRouter(prefix="/chat", tags=["Chatbot"])


# ==========================================
# SESSION CRUD
# ==========================================

@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    payload: SessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Initialize a new conversational session thread for the authenticated user.
    """
    if payload.agent_type not in ["sql", "pandas"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent type. Must be 'sql' or 'pandas'.",
        )

    session_id = str(uuid.uuid4())
    db_session = ChatSession(
        id=session_id,
        user_id=current_user.id,
        agent_type=payload.agent_type,
        title=payload.title or f"New {payload.agent_type.upper()} Chat",
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all conversation sessions belonging to the authenticated user.
    """
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session_by_id(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get session details and complete chat logs for a specific thread.
    Only the session owner can access it.
    """
    db_session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    return db_session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a session and all its messages. Only the session owner can delete.
    """
    db_session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    db.delete(db_session)
    db.commit()
    return


# ==========================================
# CHAT / AGENT INTERACTION
# ==========================================

@router.post("/", response_model=ChatMessageResponse)
async def ask_agent(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to a session thread and run the agent workflow.
    The session must belong to the authenticated user.
    """
    # 1. Fetch Session (scoped to the current user)
    db_session = (
        db.query(ChatSession)
        .filter(ChatSession.id == payload.session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    if payload.response_mode not in {"answer", "chart", "both"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="response_mode must be one of: answer, chart, both.",
        )

    # 2. Record User Message in history DB
    user_msg = ChatMessage(
        session_id=payload.session_id,
        role="user",
        content=payload.question,
    )
    db.add(user_msg)
    db.commit()

    # 3. Process according to Agent Type
    try:
        if db_session.agent_type == "sql":
            # Run SQL Agent
            result = await run_sql_agent(
                session_id=payload.session_id,
                question=payload.question,
                connection_string=payload.connection_string,
                response_mode=payload.response_mode,
            )

            # Format answers and artifacts from state
            if payload.response_mode == "chart":
                answer_content = "Chart generated from the query result."
            else:
                answer_content = result.get("answer") or "Could not generate a structured answer."
            sql_query = result.get("sql_query")
            error = result.get("error")

            chart_path = None
            chart_spec = None
            chart_output = result.get("chart_output")
            if (
                payload.response_mode in {"chart", "both"}
                and chart_output
                and chart_output.get("type") == "plotly_html"
            ):
                chart_path = chart_output.get("path")
                chart_spec = result.get("chart_spec")

        else:
            # Run Pandas Agent
            csv_file = "../Pandas_Agent/data/nigeria_messy_sales_dataset.csv"
            if db_session.title and db_session.title.endswith(".csv"):
                csv_file = db_session.title

            result = await run_pandas_agent(
                session_id=payload.session_id,
                question=payload.question,
                file_path=csv_file,
            )

            messages = result.get("messages") or []
            answer_content = messages[-1].content if messages else "No response generated."
            sql_query = None
            chart_path = None
            chart_spec = None
            error = None

        # 4. Save Assistant Response to Database
        assistant_msg = ChatMessage(
            session_id=payload.session_id,
            role="assistant",
            content=answer_content,
            sql_query=sql_query,
            chart_path=chart_path,
            error=error,
        )
        if chart_spec:
            assistant_msg.chart_spec = chart_spec

        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)
        return assistant_msg

    except Exception as e:
        # Create an assistant error message if execution fails
        error_msg = ChatMessage(
            session_id=payload.session_id,
            role="assistant",
            content=f"An error occurred while running the agent: {str(e)}",
            error=str(e),
        )
        db.add(error_msg)
        db.commit()
        db.refresh(error_msg)
        return error_msg
