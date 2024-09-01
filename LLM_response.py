from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
from LLM_prompt import msg
import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('OPENAPI_KEY')
client = OpenAI(api_key=key)

class Tool(BaseModel):
    tool_name: str
    required: bool
    code: Optional[str] = None

class Message(BaseModel):
    message_from_the_user: str
    tasks_to_achieve: str
    immediate_task_to_achieve: str
    message_to_the_user: str
    tool: Tool
    call_myself: str

msg = msg

def add_context(role,message):
    global msg
    msg.append({"role":role,"content":message})


def llm():
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=msg,
        response_format=Message
    )
    content = completion.choices[0].message.content
    add_context("assistant",content)
    return content


