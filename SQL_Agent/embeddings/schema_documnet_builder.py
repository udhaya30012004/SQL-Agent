 
"""
  Schema Builder for Embeddings

  Builds rich table-level schema documents for vector embedding.

  This file does not connect to Pinecone.
  It only converts database schema metadata into text documents.

  Output:
  {
      "film": "...rich schema document...",
      "customer": "...rich schema document..."
  }
"""

from typing import Dict, Any, Set, List


class SchemaBuilder:
    def __init__(self, schema: Dict[str, Any],relationship_graph: Dict[str,Set[str]]):
        self.schema = schema
        self.graph = relationship_graph


    def get_tables_at_depth(self, table_name: str, depth: int) -> List[str]:
        if table_name not in self.graph or depth < 1:
              return []

        visited = {table_name}
        current_level = {table_name}

        for _ in range(depth):
            next_level = set()

            for current_table in current_level:
                neighbors = self.graph.get(current_table, set())
                next_level.update(neighbors - visited)

            visited.update(next_level)
            current_level = next_level

            if not current_level:
                break

        return sorted(current_level)

    def build_description(self, table_name: str, table_info: Dict[str, Any]) -> str:
        description = table_info.get("description", "")

        if description:

            return description

        columns = table_info.get("columns", [])
        column_names = [column.get("name", "") for column in columns]

        if column_names:
            return (
                  f"Stores records for {table_name}. "
                  f"Available columns include {', '.join(column_names)}."
              )

        return f"Stores records for {table_name}."

    def build_column_lines(self, table_info: Dict[str, Any]) -> List[str]:
        columns = table_info.get("columns", [])

        if not columns:
            return ["None"]

        lines = []

        for column in columns:
            column_name = column.get("name", "")
            column_type = column.get("type", "")

            lines.append(f"{column_name} {column_type}")

        return lines

    def build_primary_key_lines(self, table_info: Dict[str, Any]) -> List[str]:
        primary_keys = table_info.get("primary_keys", [])

        if not primary_keys:
            return ["None"]

        return [", ".join(primary_keys)]

    def build_foreign_key_lines(self, table_info: Dict[str, Any]) -> List[str]:
        foreign_keys = table_info.get("foreign_keys", [])

        if not foreign_keys:
            return ["None"]

        lines = []

        for fk in foreign_keys:
            local_columns = fk.get("column", [])
            referred_table = fk.get("referred_table", "")
            referred_columns = fk.get("referred_columns", [])

            if isinstance(local_columns, list):
                local_text = ", ".join(local_columns)
            else:
                local_text = str(local_columns)

            if isinstance(referred_columns, list):
                referred_text = ", ".join(referred_columns)
            else:
                referred_text = str(referred_columns)

            lines.append(f"{local_text} -> {referred_table}({referred_text})")

        return lines

    def build_graph_summary_lines(self, table_name: str, one_hop: List[str]) -> List[str]:
        lines = [table_name]

        if not one_hop:
            lines.append("+-- None")
            return lines

        for connected_table in one_hop:
            lines.append(f"+-- {connected_table}")

        return lines

    def build_table_document(self, table_name: str) -> str:
        table_info = self.schema.get(table_name, {})

        one_hop = self.get_tables_at_depth(table_name, depth=1)
        two_hop = self.get_tables_at_depth(table_name, depth=2)
        three_hop = self.get_tables_at_depth(table_name, depth=3)

        lines = []

        lines.append("=" * 44)
        lines.append("")
        lines.append("TABLE NAME")
        lines.append(table_name)

        lines.append("")
        lines.append("DESCRIPTION")
        lines.append(self.build_description(table_name, table_info))

        lines.append("")
        lines.append("COLUMNS")
        lines.extend(self.build_column_lines(table_info))

        lines.append("")
        lines.append("PRIMARY KEY")
        lines.extend(self.build_primary_key_lines(table_info))

        lines.append("")
        lines.append("FOREIGN KEYS")
        lines.extend(self.build_foreign_key_lines(table_info))

        lines.append("")
        lines.append("DIRECTLY CONNECTED TABLES 1 HOP")
        lines.append("")
        lines.extend(one_hop if one_hop else ["None"])

        lines.append("")
        lines.append("SECOND LEVEL TABLES 2 HOP")
        lines.append("")
        lines.extend(two_hop if two_hop else ["None"])

        lines.append("")
        lines.append("THIRD LEVEL TABLES 3 HOP")
        lines.append("")
        lines.extend(three_hop if three_hop else ["None"])

        lines.append("")
        lines.append("GRAPH SUMMARY")
        lines.append("")
        lines.extend(self.build_graph_summary_lines(table_name, one_hop))

        lines.append("")
        lines.append("=" * 44)

        return "\n".join(lines)

    def build_all_documents(self) -> Dict[str, str]:
        documents = {}

        for table_name in self.schema:
            documents[table_name] = self.build_table_document(table_name)

        return documents


def build_schema_documents(schema: Dict[str, Any],relationship_graph:Dict[str,Set[str]]) -> Dict[str, str]:
    builder = SchemaBuilder(schema = schema,relationship_graph=relationship_graph)
    return builder.build_all_documents()

