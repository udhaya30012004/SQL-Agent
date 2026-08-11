"""
Production Table Selector

Responsibilities:
1. Build bidirectional relationship graph
2. Rank tables by keyword relevance
3. Expand tables using relationships
4. Apply relationship bonus
5. Return final ranked tables

Future:
- Embedding similarity
- Hybrid retrieval
"""

import re
from typing import Dict, Any, List, Tuple, Set


class TableSelectorWithGraph:
    RELATIONSHIP_WEIGHT = 3

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.graph = self._build_bidirectional_graph()

    # ==================== RELATIONSHIP GRAPH ====================

    def _build_bidirectional_graph(self) -> Dict[str, Set[str]]:
        """Build bidirectional relationship graph from foreign keys."""
        graph = {table: set() for table in self.schema}

        for table_name, table_info in self.schema.items():
            foreign_keys = table_info.get("foreign_keys", [])

            for fk in foreign_keys:
                referred_table = fk.get("referred_table")

                if referred_table and referred_table in self.schema:
                    graph[table_name].add(referred_table)
                    graph[referred_table].add(table_name)

        return graph

    # ==================== TEXT PROCESSING ====================

    @staticmethod
    def normalize(text: str) -> str:
        """Convert text to lowercase and remove special characters."""
        return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

    @staticmethod
    def singularize(token: str) -> str:
        """Convert plural tokens into singular form for matching."""
        if not token:
            return token

        if token.endswith("ies") and len(token) > 4:
            return token[:-3] + "y"

        if token.endswith("es") and len(token) > 3:
            return token[:-2]

        if token.endswith("s") and len(token) > 2 and not token.endswith("ss"):
            return token[:-1]

        return token

    def tokenize(self, text: str) -> Set[str]:
        """Tokenize text into singular forms."""
        tokens = self.normalize(text).split()
        return {self.singularize(token) for token in tokens if token}

    # ==================== SCORING ====================

    def keyword_score(self, question: str, text: str) -> int:
        """Calculate intersection of question and text tokens."""
        question_tokens = self.tokenize(question)
        text_tokens = self.tokenize(text)
        return len(question_tokens.intersection(text_tokens))

    def calculate_table_score(self, question: str, table_name: str, table_info: Dict[str, Any]) -> int:
        """Calculate relevance score for table based on keyword matches."""
        score = 0

        # Table name match (weight: 5x) - strong signal
        score += self.keyword_score(question, table_name) * 5

        # Column name match (weight: 2x) - helps with specific column queries
        column_list = table_info.get("columns", [])
        column_names = " ".join([col["name"] for col in column_list])
        score += self.keyword_score(question, column_names) * 2

        return score

    def rank_tables(self, question: str) -> List[Tuple[str, int]]:
        """Rank all tables by keyword relevance score."""
        ranked = [(table_name, self.calculate_table_score(question, table_name, table_info))
                  for table_name, table_info in self.schema.items()]

        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    # ==================== RELATIONSHIP EXPANSION ====================

    def expand_relationships(self, selected_tables: List[str], max_depth: int = 1) -> Set[str]:
        """Expand selected tables using bidirectional relationship graph."""
        expanded = set(selected_tables)
        current_level = set(selected_tables)

        for _ in range(max_depth):
            next_level = set()

            for table in current_level:
                related_tables = self.graph.get(table, set())
                next_level.update(related_tables)

            expanded.update(next_level)
            current_level = next_level

        return expanded

    # ==================== RELATIONSHIP BONUS ====================

    def relationship_bonus(self, table_name: str, primary_tables: List[str]) -> int:
        """Calculate relationship bonus - count links to primary tables."""
        related_tables = self.graph.get(table_name, set())
        return sum(1 for table in primary_tables if table in related_tables)

    # ==================== SEMANTIC SCORE (FUTURE) ====================

    def semantic_score(self, question: str, table_name: str) -> float:
        """Placeholder for future embedding-based semantic similarity scoring."""
        return 0.0

    # ==================== FINAL RANKING ====================

    def final_ranking(self, question: str, expanded_tables: Set[str], primary_tables: List[str]) -> List[str]:
        """Rank expanded tables by combined score (keyword + relationship + semantic)."""
        scored_tables = []

        for table in expanded_tables:
            base_score = self.calculate_table_score(question, table, self.schema[table])
            relationship_score = self.relationship_bonus(table, primary_tables) * self.RELATIONSHIP_WEIGHT
            semantic_score = self.semantic_score(question, table)
            total_score = base_score + relationship_score + semantic_score

            scored_tables.append((table, total_score))

        scored_tables.sort(key=lambda x: x[1], reverse=True)
        return [table for table, _ in scored_tables]

    # ==================== MAIN ENTRY POINT ====================
    
    def select_tables(self,question: str,top_k: int = 3,expand_depth: int = 1) -> List[str]:
      
      """
      Select relevant tables for a question.

      Keeps backward compatibility with the existing SQL agent.

      Returns:
          ["film", "inventory", "rental"]
      """

      scored_tables = self.select_tables_with_scores(
          question=question,
          top_k=top_k,
          expand_depth=expand_depth
      )

      return [
          item["table"]
          for item in scored_tables
      ]
    
    def select_tables_with_scores(self,question: str,top_k: int = 3,expand_depth: int = 1) -> List[Dict[str, Any]]:
      """
      Select relevant tables and return keyword/graph scores.

      Used by the future hybrid retriever.

      Returns:
          [
              {
                  "table": "film",
                  "score": 10.0,
                  "base_score": 10.0,
                  "relationship_score": 0.0,
                  "semantic_score": 0.0,
                  "source": "keyword"
              }
          ]
      """

      ranked_tables = self.rank_tables(question)

      if not ranked_tables:
        return []

      candidates = [
          table
          for table, score in ranked_tables[:top_k]
          if score > 0
      ]

      if not candidates:
        candidates = [ranked_tables[0][0]]

      expanded_tables = self.expand_relationships(
          selected_tables=candidates,
          max_depth=expand_depth
      )

      scored_tables = []

      for table in expanded_tables:

        if table not in self.schema:
           continue

        base_score = self.calculate_table_score(
              question=question,
              table_name=table,
              table_info=self.schema[table]
          )

        relationship_score = (
              self.relationship_bonus(
                  table_name=table,
                  primary_tables=candidates
              )
              * self.RELATIONSHIP_WEIGHT
          )

        semantic_score = self.semantic_score(
              question=question,
              table_name=table
          )

        total_score = (
              base_score
              + relationship_score
              + semantic_score
          )

        if total_score <= 0:
              continue

        scored_tables.append({
              "table": table,
              "score": float(total_score),
              "base_score": float(base_score),
              "relationship_score": float(relationship_score),
              "semantic_score": float(semantic_score),
              "source": "keyword"
          })

      scored_tables.sort(
          key=lambda item: item["score"],
          reverse=True
      )

      return scored_tables


    



    