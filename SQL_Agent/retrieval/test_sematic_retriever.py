from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from SQL_Agent.retrieval.pinecone_sematic_retriever import PineconeSemanticRetriever


def main():
    retriever = PineconeSemanticRetriever()

    questions = [
          "Which movie has the longest duration?",
          "Which actor generated the highest rental revenue?",
          "Top 5 customers by payment",
          "Which movies have never been rented?",
          "Which category contains the most films?"
      ]

    for question in questions:
        print("=" * 80)
        print(f"QUESTION: {question}")
        print("-" * 80)

        candidates = retriever.search(
              question=question,
              top_k=5
          )

        for candidate in candidates:
            print(
                  f"{candidate['table']:<25} "
                  f"{candidate['score']:.4f} "
                  f"{candidate['source']}"
              )

    print("=" * 80)


if __name__ == "__main__":
    main()
