'''
this file is used to extract entites like column name from thw last conversation so that llm can have imporoved memeory accuracy 
we willl store this is last_context as dictionalry '''
import re

def extract_context(question: str,schema: dict):

    question_lower = question.lower()

    for column in schema["columns"]:

        if column.lower() in question_lower:

            words = question.split()

            for word in words:

                if word.lower() == column.lower():
                    continue

                return {
                    "entity": word,
                    "column": column
                }

    return {}