from typing import Optional, TypedDict, List, Dict, Any

'''
this defines the state for this SQL AGENT 
'''

class SQLAgentState(TypedDict):
    response_mode: str

    question: str
    
    schema: dict
    
    sql_query: str
    
    result: object

    result_file : Optional[str]  # Path to a file containing the result, if applicable

    # result_pofile provides the summary of the result for llm to decide which chart to pick 
    # avoids sending the entire result to llm for chart selection

    result_profile : Dict[str, Any]
    
    # LLM-generated chart instruction.
      # Example:
      # {
      #   "render": true,
      #   "chart_type": "bar",
      #   "x_axis": "category",
      #   "y_axis": "total_sales",
      #   "title": "Total Sales by Category"
      # }
    
    chart_spec: Dict[str, Any]

    chart_output: Optional[Dict[str, Any]]

    chart_error : Optional[str]

    answer: str
    
    selected_tables: List[str]              # Tables selected by table selector
    
    selected_schema: Dict[str, Any]         # Schema of only selected tables

    error : str
