from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os 
load_dotenv()

API_KEY = os.getenv('GROQ_API')

MODEL_NAME = 'openai/gpt-oss-120b'

def get_llm(model_name: str = MODEL_NAME, temperature: float = 0):

    if not API_KEY:
        print('='*60)
        raise ValueError("GROQ API KEY NOT FOUND IN ENVIRONMENT VARIABLE ")
    print('='*50)
    
    return ChatGroq(
        model = model_name,
        api_key=API_KEY,
        temperature=temperature
    )
    
