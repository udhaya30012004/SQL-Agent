from langchain_core.messages import HumanMessage
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Pandas_Agent.data.csv_loader import load_data
from Pandas_Agent.schema.schema import extract_data
from Pandas_Agent.graph.workflow import graph

from Pandas_Agent.data import data_store


# Load Dataset
df = load_data(
    "nigeria_messy_sales_dataset.csv"
)

# Store DataFrame Globally
data_store.GLOBAL_DF = df

# Extract Schema
schema = extract_data(df)


print("\nPandas Agent Ready")
print("Type 'exit' to quit.\n")


# Memory Session
thread_id = "user_1"


while True:

    question = input(
        "\nAsk Question: "
    )

    if question.lower() == "exit":
        break

    try:

        result = graph.invoke(

            {
                "messages": [
                    HumanMessage(
                        content=question
                    )
                ],

                "schema": schema,

                "code": "",

                "result": None,
                
                "last_context": {}
            },

            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }

        )

        print(
            "\nGenerated Code:\n"
        )

        print(
            result["code"]
        )

        print(
            "\nAnswer:\n"
        )

        print(
            result["messages"][-1].content
        )

    except Exception as e:

        print(
            f"\nError: {str(e)}"
        )
