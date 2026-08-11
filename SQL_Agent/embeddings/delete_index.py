from pinecone import Pinecone
import os
from dotenv import load_dotenv
load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pc.Index("sql-agent")  # your index name

index.delete(
    delete_all=True,
    namespace="default"
)

print("All vectors deleted.")