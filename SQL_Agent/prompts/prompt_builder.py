"""
Prompt Builder for SQL Agent

Builds SQL generation prompts using only selected candidate tables
to reduce hallucination and keep prompts focused.
"""

from typing import Dict, Any, List
from SQL_Agent.prompts.prompts import SQL_GENERATION_PROMPT

def format_selected_schema_for_prompt(selected_schema: Dict[str, Any]) -> str:
    """
    Format selected tables and their schema for the SQL generation prompt.
    
    Shows only:
    - Table names
    - Columns with data types
    - Primary keys
    - Foreign key relationships (for joins)
    """
    lines = []
    
    for table_name, table_info in selected_schema.items():
        lines.append(f"TABLE: {table_name}")
        
        # Description if available
        description = table_info.get("description", "")
        if description:
            lines.append(f"  Description: {description}")
        
        # Columns
        columns = table_info.get("columns", [])
        if columns:
            lines.append("  Columns:")
            for col in columns:
                col_name = col.get("name", "")
                col_type = col.get("type", "")
                native_type = col.get("native_type", "")
                enum_values = col.get("enum_values", [])
                nullable = col.get("nullable", False)
                nullable_str = "NULLABLE" if nullable else "NOT NULL"
                type_parts = [col_type]
                if native_type and native_type != col_type:
                    type_parts.append(f"native: {native_type}")
                if enum_values:
                    type_parts.append(f"enum values: {', '.join(enum_values)}")
                lines.append(f"    - {col_name}: {'; '.join(type_parts)} [{nullable_str}]")
        
        # Primary Keys
        pk = table_info.get("primary_keys", [])
        if pk:
            lines.append(f"  Primary Key: {', '.join(pk)}")
        
        # Foreign Keys (for join context)
        fks = table_info.get("foreign_keys", [])
        if fks:
            lines.append("  Foreign Keys:")
            for fk in fks:
                col = fk.get("column", [])
                ref_table = fk.get("referred_table", "")
                ref_cols = fk.get("referred_columns", [])
                
                col_str = ", ".join(col) if isinstance(col, list) else str(col)
                ref_col_str = ", ".join(ref_cols) if isinstance(ref_cols, list) else str(ref_cols)
                
                lines.append(f"    - {col_str} → {ref_table}({ref_col_str})")
        
        lines.append("")  # Blank line between tables
    
    return "\n".join(lines)


def build_sql_prompt_with_selected_tables(
    question: str,
    selected_schema: Dict[str, Any],
    selected_table_names: List[str]
) -> str:
    """
    Build SQL generation prompt with ONLY selected tables.
    
    Args:
        question: User's natural language question
        selected_schema: Dict of only the selected tables and their schema
        selected_table_names: List of selected table names
    
    Returns:
        it combines SQL GENRATION PROMT with the context like 
        table_name + schema_text + Question and comnibed 
        with generation prompt sent to llm in generation node 
    """
    
    schema_text = format_selected_schema_for_prompt(selected_schema)
    tables_list = ", ".join(selected_table_names)

    context = f"""
=================================================
SELECTED TABLES
=================================================

{tables_list}

=================================================
SELECTED SCHEMA
=================================================

{schema_text}

=================================================
USER QUESTION
=================================================

{question} 

""" 
    
    return  SQL_GENERATION_PROMPT + context


# not required LATER CAN BE IMPLEMENTED
'''
def build_sql_prompt_with_context(
    question: str,
    selected_schema: Dict[str, Any],
    selected_table_names: List[str],
    conversation_history: List[Dict[str, str]] = None
) -> str:
    """
    Build SQL prompt with multi-turn conversation context.
    
    Useful for follow-up questions that reference previous queries.
    """
    
    schema_text = format_selected_schema_for_prompt(selected_schema)
    tables_list = ", ".join(selected_table_names)
    
    history_text = ""
    if conversation_history:
        history_text = "\n========================================================\nPREVIOUS CONTEXT\n========================================================\n\n"
        for turn in conversation_history[-2:]:
            history_text += f"User: {turn.get('question', '')}\n"
            history_text += f"SQL: {turn.get('sql', '')}\n\n"
    
    prompt = f"""You are an expert SQL Data Analyst.

Your task is to generate a SQL query that answers the user's question using ONLY the provided database schema.

========================================================
CRITICAL INSTRUCTIONS
========================================================

1. Use ONLY these tables: {tables_list}
2. Use ONLY columns from these tables
3. Never invent table or column names
4. If joining tables, use Foreign Key relationships shown in schema
5. Generate executable SQL only
6. Return ONLY the SQL query (no explanations, comments, or markdown)
7. Generate a SINGLE SELECT query only

========================================================
DATABASE SCHEMA (SELECTED TABLES ONLY)
========================================================

{schema_text}

{history_text}

========================================================
USER QUESTION
========================================================

{question}

========================================================
GENERATE SQL QUERY:
========================================================
"""
    
    return prompt

    '''
