import re

def validate_query(query: str) -> str:
    """
    Validate generated SQL query.
    
    Ensures the query is read-only (SELECT, WITH, or EXPLAIN) and does not
    contain forbidden keywords (e.g., INSERT, UPDATE, DELETE, etc.) outside
    of string literals and comments.
    
    Returns the query with markdown code blocks stripped.
    """
    if not query:
        raise ValueError("Query is empty.")

    # 1. Strip markdown syntax (e.g. ```sql ... ```) if present
    query = query.strip()
    if query.startswith("```"):
        lines = query.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        query = "\n".join(lines).strip()
    
    markdown_cleaned_query = query

    # 2. Remove SQL comments (both block and single-line comments) to avoid false positives
    # Remove multi-line comments /* ... */
    query = re.sub(r'/\*.*?\*/', ' ', query, flags=re.DOTALL)
    # Remove single-line comments -- ...
    query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)

    # 3. Strip string literals to prevent blocking queries with keywords in text/literal filters
    # Replace single-quoted string literals with a placeholder space
    query = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", ' ', query)
    # Replace double-quoted string literals/identifiers
    query = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', ' ', query)

    # 4. Clean up and normalize whitespace
    query_clean = re.sub(r'\s+', ' ', query).strip().upper()

    # 5. Check allowed starting keyword (allowing SELECT, WITH, or EXPLAIN, including leading parentheses)
    query_stripped = re.sub(r'^[(\s]+', '', query_clean)
    
    allowed_starts = ("SELECT", "WITH", "EXPLAIN")
    if not any(query_stripped.startswith(start) for start in allowed_starts):
        raise ValueError("Only SELECT, WITH, or EXPLAIN queries are allowed.")

    # 6. Check for forbidden keywords using word boundaries to prevent partial matches
    # (e.g. allow columns/tables like "CREATE_DATE" or "UPDATE_TIME")
    forbidden_pattern = re.compile(
        r'\b(INSERT|UPDATE|DELETE|TRUNCATE|DROP|ALTER|CREATE|REPLACE|GRANT|REVOKE)\b',
        re.IGNORECASE
    )
    
    match = forbidden_pattern.search(query_clean)
    if match:
        raise ValueError(f"Forbidden SQL operation detected: {match.group(1)}")

    return markdown_cleaned_query
