from LLM_prompt import msg
from openai import OpenAI
import os
from dotenv import load_dotenv
from LLM_response import get_context
load_dotenv()

key = os.getenv("OPENAI_API")
class Context():
    def __init__(self) -> None:
        pass

    def summarize_memory(self):
        memory = get_context()
        memory =  memory[5:]
        print(memory)
        
        # client = OpenAI(api_key=key)
        # chat_completion = client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[{"role": "system", "content": "You are an AI summarizer. You will be given plethora of json content and you task is to summarize it. Make sure to include all the specific details as this will be fed to an LLM and its crucial to retain all the import details such as file location, what it has achieved, what the user asked for, its response, etc etc"},
        #              {"role": "user", "content": f'summarize this {memory}'} ]
        # )
        # response_message = chat_completion.choices[0].message.content
        # new_msg = msg
        # new_msg.append({"role": "user", "content":f"THIS IS THE SUMMARY OF CONVERSATION WITH THE USER AND YOURSELF {response_message}"})
        # return new_msg


        

        
