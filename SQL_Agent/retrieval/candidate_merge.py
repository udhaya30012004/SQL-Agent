
"""
  Candidate Merger

  Merges candidates from:
  1. Keyword / graph retriever
  2. Semantic Pinecone retriever

  Input examples:

  keyword_candidates:
  [
      {
          "table": "customer",
          "score": 10.0,
          "base_score": 7.0,
          "relationship_score": 3.0,
          "source": "keyword"
      }
  ]

  semantic_candidates:
  [
      {
          "table": "payment",
          "score": 0.6725,
          "source": "semantic"
      }
  ]

  Output:
  [
      {
          "table": "payment",
          "score": 0.95,
          "keyword_score": 0.82,
          "semantic_score": 0.67,
          "sources": ["keyword", "semantic"]
      }
  ]
"""

from typing import Dict, Any, List


class CandidateMerger:
    def __init__(self,keyword_weight: float = 0.45,semantic_weight: float = 0.45,both_sources_bonus: float = 0.10):
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight
        self.both_sources_bonus = both_sources_bonus

    def normalize_scores(self,candidates: List[Dict[str, Any]]) -> Dict[str, float]:
        """
          Normalize candidate scores to 0-1 range.

          Keyword scores may be 3, 9, 10...
          Semantic scores are usually already 0-1.

          This makes both retrievers comparable.
        """
        if not candidates:
            return {}

        max_score = max(
              float(candidate.get("score", 0.0))
              for candidate in candidates
          )

        if max_score <= 0:
            return {
                  candidate["table"]: 0.0
                  for candidate in candidates
                  if candidate.get("table")
              }

        normalized = {}

        for candidate in candidates:
            table = candidate.get("table")

            if not table:
                continue

            score = float(candidate.get("score", 0.0))
            normalized[table] = score / max_score

        return normalized

    def merge(self,keyword_candidates: List[Dict[str, Any]],semantic_candidates: List[Dict[str, Any]],top_k: int = 8) -> List[Dict[str, Any]]:
        """
          Merge keyword and semantic candidates into one ranked list.

          Args:
              keyword_candidates: output from TableSelectorWithGraph.select_tables_with_scores()
              semantic_candidates: output from PineconeSemanticRetriever.search()
              top_k: maximum number of merged candidates to return

          Returns:
              List of merged candidate dictionaries.
        """
        keyword_scores = self.normalize_scores(keyword_candidates)
        semantic_scores = self.normalize_scores(semantic_candidates)

        all_tables = set(keyword_scores.keys()) | set(semantic_scores.keys())

        merged_candidates = []

        for table in all_tables:
            keyword_score = keyword_scores.get(table, 0.0)
            semantic_score = semantic_scores.get(table, 0.0)

            sources = []

            if table in keyword_scores:
                  sources.append("keyword")

            if table in semantic_scores:
                  sources.append("semantic")

            both_bonus = (
                  self.both_sources_bonus
                  if len(sources) == 2
                  else 0.0
              )

            final_score = (
                  self.keyword_weight * keyword_score
                  + self.semantic_weight * semantic_score
                  + both_bonus
              )

            merged_candidates.append({
                  "table": table,
                  "score": float(final_score),
                  "keyword_score": float(keyword_score),
                  "semantic_score": float(semantic_score),
                  "sources": sources
              })

        merged_candidates.sort(
              key=lambda candidate: candidate["score"],
              reverse=True
          )

        return merged_candidates[:top_k]

    def merge_to_table_names(self,keyword_candidates: List[Dict[str, Any]],semantic_candidates: List[Dict[str, Any]],top_k: int = 8) -> List[str]:
        """
          Convenience method.

          Returns only table names from merged candidates.
        """
        merged_candidates = self.merge(
              keyword_candidates=keyword_candidates,
              semantic_candidates=semantic_candidates,
              top_k=top_k
          )

        return [
              candidate["table"]
              for candidate in merged_candidates
          ]
