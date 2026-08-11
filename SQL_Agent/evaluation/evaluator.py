'''
This file evaluates the Table Retriever using benchmark questions.
'''

import json
import csv
from pathlib import Path

from SQL_Agent.evaluation.metrics import RetrievalEvaluator
from SQL_Agent.retrieval.table_selector import TableSelectorWithGraph
from SQL_Agent.schema.schema_extractor import extract_schema
from SQL_Agent.db.db_connector import connect_database
from SQL_Agent.retrieval.pinecone_sematic_retriever import PineconeSemanticRetriever
from SQL_Agent.retrieval.candidate_merge import CandidateMerger

CONNECTION_STRING = (
    "postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
)
engine = connect_database(CONNECTION_STRING)


class BenchmarkEvaluator:

    def __init__(self):

        # Load schema
        self.schema = extract_schema(engine)

        # Initialize table selector
        self.selector = TableSelectorWithGraph(self.schema)
        self.semantic_retriever = PineconeSemanticRetriever()
        self.merger = CandidateMerger()

        # Load benchmark questions
        benchmark_path = Path(__file__).parent / "benchmark.json"

        with open(benchmark_path, "r", encoding="utf-8") as file:
            self.benchmark = json.load(file)

        # Store all evaluation results
        self.results = []

    # =======================================================
    # Main Evaluation Function
    # =======================================================

    def evaluate(self):

        total_precision = 0
        total_recall = 0
        total_f1 = 0

        print("=" * 100)
        print("TABLE RETRIEVER BENCHMARK")
        print("=" * 100)

        for sample in self.benchmark:

            question = sample["question"]
            difficulty = sample["difficulty"]
            ground_truth = sample["ground_truth"]

            # -----------------------------------------
            # Run Hybrid Retriever
            # -----------------------------------------

            # 1. Get raw keyword matches
            ranked_tables = self.selector.rank_tables(question)
            keyword_candidates = [
                {"table": table, "score": float(score), "source": "keyword"}
                for table, score in ranked_tables
                if score > 0
            ]

            # 2. Get semantic matches from Pinecone
            try:
                raw_semantic = self.semantic_retriever.search(question=question, top_k=5)
                semantic_candidates = [
                    {"table": c["table"], "score": c["score"], "source": "semantic"}
                    for c in raw_semantic
                ]
            except Exception as e:
                print(f"\n[Warning] Semantic search failed: {e}")
                semantic_candidates = []

            # 3. Merge both candidates
            merged_candidates = self.merger.merge(
                keyword_candidates=keyword_candidates,
                semantic_candidates=semantic_candidates,
                top_k=3
            )
            seed_tables = [c["table"] for c in merged_candidates]

            # 4. Expand using relationship graph
            expanded_tables = self.selector.expand_relationships(
                selected_tables=seed_tables,
                max_depth=2
            )

            # 5. Deduplicate retrieved tables
            retrieved_tables = list(expanded_tables)

            # -----------------------------------------
            # Evaluate Metrics
            # -----------------------------------------

            metrics = RetrievalEvaluator.evaluate(
                ground_truth=ground_truth,
                retrieved=retrieved_tables
            )

            # -----------------------------------------
            # Update Overall Scores
            # -----------------------------------------

            total_precision += metrics.precision
            total_recall += metrics.recall
            total_f1 += metrics.f1_score

            # -----------------------------------------
            # Store CSV Result
            # -----------------------------------------

            self.results.append({

                "Difficulty": difficulty,

                "Question": question,

                "Ground Truth":
                    ", ".join(sorted(metrics.ground_truth_tables)),

                "Retrieved":
                    ", ".join(sorted(metrics.retrieved_tables)),

                "Matched":
                    ", ".join(sorted(metrics.matched_tables)),

                "Extra":
                    ", ".join(sorted(metrics.extra_tables)),

                "Missing":
                    ", ".join(sorted(metrics.missing_tables)),

                "TP": metrics.true_positive,

                "FP": metrics.false_positive,

                "FN": metrics.false_negative,

                "Precision":
                    round(metrics.precision, 4),

                "Recall":
                    round(metrics.recall, 4),

                "F1":
                    round(metrics.f1_score, 4)

            })

            # -----------------------------------------
            # Print Individual Result
            # -----------------------------------------

            print("\n" + "-" * 100)

            print(f"Question      : {question}")
            print(f"Difficulty    : {difficulty}")

            print()

            print(f"Ground Truth  : {metrics.ground_truth_tables}")

            print(f"Retrieved     : {metrics.retrieved_tables}")

            print()

            print(f"Matched       : {metrics.matched_tables}")

            print(f"Extra         : {metrics.extra_tables}")

            print(f"Missing       : {metrics.missing_tables}")

            print()

            print(f"Precision     : {metrics.precision:.2%}")

            print(f"Recall        : {metrics.recall:.2%}")

            print(f"F1 Score      : {metrics.f1_score:.2%}")

        # =======================================================
        # Overall Statistics
        # =======================================================

        total_questions = len(self.benchmark)

        avg_precision = total_precision / total_questions
        avg_recall = total_recall / total_questions
        avg_f1 = total_f1 / total_questions

        print("\n")
        print("=" * 100)

        print("FINAL BENCHMARK RESULTS")

        print("=" * 100)

        print(f"Total Questions     : {total_questions}")

        print(f"Average Precision   : {avg_precision:.2%}")

        print(f"Average Recall      : {avg_recall:.2%}")

        print(f"Average F1 Score    : {avg_f1:.2%}")

        # Save CSV
        self.save_csv()

    # =======================================================
    # Save CSV
    # =======================================================

    def save_csv(self):

        csv_path = Path(__file__).parent / "retrieval_report.csv"

        with open(
            csv_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.results[0].keys()
            )

            writer.writeheader()
            writer.writerows(self.results)

        print("\n")
        print(f"CSV Report Saved -> {csv_path}")


# =======================================================
# Main
# =======================================================

if __name__ == "__main__":

    evaluator = BenchmarkEvaluator()

    evaluator.evaluate()
