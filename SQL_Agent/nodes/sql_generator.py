"""
SQL Generation Node

Contains the logic for generating SQL queries using table selection
and filtered schema prompts.

Uses shared LLM service from shared/llm.py
"""

# importing retrievers
from SQL_Agent.retrieval.table_selector import TableSelectorWithGraph
from SQL_Agent.retrieval.pinecone_sematic_retriever import PineconeSemanticRetriever
from SQL_Agent.retrieval.candidate_merge import CandidateMerger
# importinf prompts
from SQL_Agent.prompts.prompt_builder import build_sql_prompt_with_selected_tables
# importing Agent State
from SQL_Agent.graph.state import SQLAgentState
from shared.llm import get_llm





def generate_sql(state: SQLAgentState,llm) -> SQLAgentState:
    """
    Generate a SQL query using only selected candidate tables.
    
    Process:
    1. Use TableSelectorWithGraph, PineconeSemanticRetriever, and CandidateMerger
       as a hybrid retriever to select candidate tables (top_k=3, expand_depth=2).
    2. Extract only selected table schema (reduce prompt size)
    3. Build prompt with filtered schema (prevents hallucination)
    4. Call LLM ONCE to generate SQL
    
    Args:
        state: SQLAgentState containing question and schema
        llm: LLM client model instance
    
    Returns:
        Updated state with sql_query, selected_tables, selected_schema
    """
    # Get LLM instance (uses defaults from shared/llm.py)
    question = state.get('question', '')
    full_schema = state.get('schema', {})
    
    # Step 1: Select candidate tables using relationship graph
    selector = TableSelectorWithGraph(full_schema)

    # Step 1.1 : get keywords
    ranked_tables = selector.rank_tables(question)
    keyword_candidates = [
        {"table": table, "score": float(score), "source": "keyword"}
        for table, score in ranked_tables
        if score > 0
    ]

    # step 1.2 : GET SEMATIC SCORES FROM PINECONE
    try:
        semantic_retriever = PineconeSemanticRetriever()
        raw_semantic = semantic_retriever.search(question=question,top_k=3)
        semantic_candidates = [
            {'table':c['table'],'score':c['score'],'source':'semantic'}
            for c in raw_semantic
        ]
    except Exception as e:
        print("Semantic retrieval failed:", e)
        semantic_candidates = []

    # 1.3. Merge both candidates
    merger = CandidateMerger()
    merged_candidates = merger.merge(
        keyword_candidates=keyword_candidates,
        semantic_candidates=semantic_candidates,
        top_k=3
    )
    seed_tables = [c["table"] for c in merged_candidates]


    # 1.4. Expand using relationship graph
    expanded_tables = selector.expand_relationships(
        selected_tables=seed_tables,
        max_depth=2
    )

    # 1.5. Deduplicate and get final table names
    selected_table_names = list(expanded_tables)
    
    
   

    if not selected_table_names:
        state["error"] = "No relevant tables found."
        return state
    
    # Step 2: Extract only selected table schema
    selected_schema = {
        table: full_schema[table]
        for table in selected_table_names
        if table in full_schema
    }
    
    # Step 3: Build prompt with only selected tables
    prompt = build_sql_prompt_with_selected_tables(
        question,
        selected_schema,
        selected_table_names
    )
    
    # Step 4: LLM CALL #1 - Generate SQL
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        state["error"] = str(e)
        return state
    
    # Store results in state
    
    sql_query = response.content.strip()

    if not sql_query:
        state["error"] = "LLM returned empty SQL."
        return state

    state["sql_query"] = sql_query
    state['selected_tables'] = selected_table_names
    state['selected_schema'] = selected_schema
    
    return state