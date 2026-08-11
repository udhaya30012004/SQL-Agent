
from langgraph.graph import StateGraph, START, END
from SQL_Agent.graph.state import SQLAgentState
from SQL_Agent.graph.nodes import generation_node,validation_node,explanation_node,execution_node,analytics_node
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()

builder = StateGraph(SQLAgentState)

# Add nodes
builder.add_node("sql_generation", generation_node)
builder.add_node("validation", validation_node)
builder.add_node("execution", execution_node)
builder.add_node("analytics", analytics_node)
builder.add_node("explanation", explanation_node)

def route_after_execution(state: SQLAgentState) -> str:
    mode = state.get("response_mode", "both")

    if mode == "chart":
        return "analytics"

    return "explanation"


def route_after_explanation(state: SQLAgentState) -> str:
    mode = state.get("response_mode", "both")

    if mode == "both":
        return "analytics"

    return END



# Connect edges


builder.set_entry_point("sql_generation")
builder.add_edge("sql_generation", "validation")
builder.add_edge("validation", "execution")
builder.add_conditional_edges(
    "execution",
    route_after_execution,
    {
        "analytics": "analytics",
        "explanation": "explanation",
    },
)
builder.add_conditional_edges(
    "explanation",
    route_after_explanation,
    {
        "analytics": "analytics",
        END: END,
    },
)
builder.add_edge("analytics", END)

# Compile the graph
graph = builder.compile(checkpointer=memory)

# Visualization
'''
try:
    png_data = graph.get_graph().draw_mermaid_png()
    with open("langgraph_diagram.png", "wb") as f:
        f.write(png_data)
    print("Graph diagram saved to langgraph_diagram.png")
except Exception as e:
    print(f"Warning: Could not generate diagram: {e}")


print('>'*50)
print("SQL Agent workflow compiled successfully!")
print('<'*50)'''

