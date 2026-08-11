from shared.llm import get_llm
from Pandas_Agent.prompts.prompts import CODE_GENERATION_PROMPT,EXPLANATION_PROMPT
from Pandas_Agent.nodes.executor import execute_code
from Pandas_Agent.graph.state import AgentState
from Pandas_Agent.data import data_store
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from Pandas_Agent.schema.context_extractor import extract_context


llm = get_llm(model_name='openai/gpt-oss-20b', temperature=0.3)

def generation_node(state: AgentState):
    question = (state['messages'][-1].content)
    converstation = '\n'.join(
        [
            f"{msg.type} : {msg.content}"
            for msg in state['messages']
        ]
    )
    last_context = state.get('last_context',{})

    prompt = f"""{CODE_GENERATION_PROMPT}
    LAST_CONTEXT : {last_context}
    CONVERSTATION HISTORY : {converstation}
    SCHEMA : {state['schema']}
    CURRENT QUESTION :{question}
    """

    response = llm.invoke(prompt)
    state['code'] = (response.content.strip())

    return state

    

def execute_node(state:AgentState):

    result = execute_code(
        state["code"],
        data_store.GLOBAL_DF
    )

    state["result"] = str(result)

    return state


def explanation_node(state: AgentState):

    question = (
        state["messages"][-1]
        .content
    )

    prompt = f"""
{EXPLANATION_PROMPT}

QUESTION:

{question}

RESULT:

{str(state['result'])}
"""

    response = llm.invoke(
        prompt
    )

    answer = (
        response.content.strip()
    )

    return {
        "messages": [
            AIMessage(
                content=answer
            )
        ]
    }

# context updating node
def context_node(state:AgentState):
    question = (
        state['messages'][-1].content
    )

    context = extract_context(question,state['schema'])

    if context:
        state['last_context'] = context

    return state


