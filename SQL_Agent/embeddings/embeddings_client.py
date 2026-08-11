import os 
from typing import List
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

DEFAULT_EMBEDDING_MODEL = 'gemini-embedding-001'
DEFAULT_OUTPUT_DIMENSIONALITY = 768

class EmbeddingClient:
    def __init__(self,model_name : str = DEFAULT_EMBEDDING_MODEL,output_dimension : str = DEFAULT_OUTPUT_DIMENSIONALITY):
        self.api_key = os.getenv('GOOGLE_API_KEY')

        if not self.api_key:
            raise ValueError('GOOGLE API INVALID OR NOT AVAILABLE')
        
        self.model_name = model_name
        self.output_dimension = output_dimension

        self.client = genai.Client(
            api_key=self.api_key
        )
    
    def embed_query(self,text:str):
        '''
        embed user question for retrieval
        '''
        response = self.client.models.embed_content(
            model = self.model_name,
            contents = text,
            config = types.EmbedContentConfig(
                task_type='RETRIEVAL_QUERY',
                output_dimensionality=self.output_dimension
            )
        )

        return response.embeddings[0].values
    
    ### embedding table schema

    def embed_document(self, text: str) -> List[float]:
        """
        Embed one schema document for storage in Pinecone.
        """
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(
                  task_type="RETRIEVAL_DOCUMENT",
                  output_dimensionality=self.output_dimension
              )
          )

        return response.embeddings[0].values

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple schema documents.
        """
        response = self.client.models.embed_content(
              model=self.model_name,
              contents=texts,
              config=types.EmbedContentConfig(
                  task_type="RETRIEVAL_DOCUMENT",
                  output_dimensionality=self.output_dimension
              )
          )

        return [embedding.values for embedding in response.embeddings]

 


        