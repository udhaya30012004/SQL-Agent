"""
This file defines the shared state used by LangGraph.

The state acts like a global memory that is
passed between all nodes in the workflow.

Each node can read and update the state.
"""

import pandas as pd

from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):

    messages :Annotated[list[BaseMessage],add_messages]

    # question : str

    schema: dict
     
     #data frame object removed 

    code: str

    result: object

    last_context : dict 


    #answer: str