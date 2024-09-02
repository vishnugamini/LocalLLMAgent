from LLM_prompt import msg
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("OPENAI_API")
class Context():
    def __init__(self) -> None:
        pass

    def summarize_memory(self):
        memory =  memory[5:]
        print(memory)


        
