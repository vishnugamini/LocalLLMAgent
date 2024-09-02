from LLM_response import llm, add_context
from LLM_response import update_context
from execute_code import exec_code
from context import Context
import time
import json
from colorama import Fore

c = Context()

prompt = ""
while prompt != "exit":
    prompt = input(Fore.GREEN + "Prompt: ")
    add_context("user",prompt)

    response  = llm()
    response_json = json.loads(response)

    print(Fore.BLUE + json.dumps(response_json,indent=4))

    agent_call = response_json['call_myself']

    while agent_call == 'true':
        tool = response_json['tool']['tool_name']
        code = response_json['tool']['code']
        if tool == 'summarize_memory':
            x = c.summarize_memory()
            update_context(x)
            print(Fore.YELLOW + "context updated")
        if tool == 'python' and code != 'None':
            output = exec_code(code)
            print(Fore.YELLOW + "COMPILER OUTPUT: " + output['output'])
            add_context('user', f"OUTPUT FROM PYTHON COMPILER {output['output']}")
        response = llm()
        response_json = json.loads(response)
        print(Fore.BLUE,json.dumps(response_json,indent=4))
        agent_call = response_json['call_myself']


