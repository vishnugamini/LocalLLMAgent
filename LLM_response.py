from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
from LLM_prompt import system_msg
import os
import copy
import time
from dotenv import load_dotenv

load_dotenv()

original_system_message = copy.deepcopy(system_msg)

key = os.getenv("OPENAPI_KEY")
client = OpenAI(api_key=key)
msg = system_msg


class Tool(BaseModel):
    tool_name: str
    required: bool
    thinking_phase: str
    file_location: str
    code: Optional[str] = None
    query: Optional[str] = None


class Message(BaseModel):
    message_from_the_user: str
    tasks_to_achieve: str
    immediate_task_to_achieve: str
    message_to_the_user: str
    tool: Tool
    call_myself: str


def refresh():
    global msg
    msg = original_system_message
    return "Memory Refreshed"


def add_context(role, message):
    global msg
    msg.append({"role": role, "content": message})


def llm():
    global msg
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini", # or "gpt-4o-2024-08-06" (expensive but better output in some instances)
        messages=msg,
        response_format=Message,
    )
    content = completion.choices[0].message.content
    add_context("assistant", content)
    return content
