from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
from prompts.Agent_prompt import system_msg
import os
import copy
import time
from dotenv import load_dotenv

load_dotenv()


key = os.getenv("OPENAPI_KEY")
client = OpenAI(api_key=key)
msg = copy.deepcopy(system_msg)


class Tool(BaseModel):
    tool_name: str
    required: bool
    thinking_phase: str
    important_parameter: str
    print_statement_to_add: str
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
    original_system_message = copy.deepcopy(system_msg)
    msg = original_system_message
    return "Memory Refreshed"


def add_context(role, message):
    global msg
    msg.append({"role": role, "content": message})


def llm():
    global msg
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",  # or "gpt-4o-mini-2024-07-18" (expensive but better output in some instances)
            messages=msg,
            response_format=Message,
        )
        content = completion.choices[0].message.content
        add_context("assistant", content)
        return content
    except Exception as e:
        print(f"Error Occured \n {e}")
