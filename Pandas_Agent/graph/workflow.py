from langgraph.graph import StateGraph,START,END
from Pandas_Agent.graph.state import AgentState
from Pandas_Agent.graph.nodes import execute_node,generation_node,explanation_node,context_node
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
builder = StateGraph(AgentState)


# adding node 
builder.add_node('code_generation',generation_node)
builder.add_node('execution',execute_node)
# adding context updating node 
builder.add_node('context_update',context_node)
builder.add_node('explanation',explanation_node)

# connexting these edges 

builder.set_entry_point('code_generation')
builder.add_edge('code_generation','execution')
builder.add_edge('execution','context_update')
builder.add_edge('context_update','explanation')
builder.add_edge('explanation',END)

graph = builder.compile(checkpointer=memory)
