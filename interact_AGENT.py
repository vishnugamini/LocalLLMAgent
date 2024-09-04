from LLM_response import llm, add_context, refresh
from execute_code import exec_code
import time
import json
from colorama import Fore

prompt = ""
while prompt != "exit":
    prompt = input(Fore.GREEN + "Prompt: ")
    if prompt.lower() == "refresh":
        response = refresh()
        print(Fore.YELLOW + response)
    add_context("user",prompt)
    if prompt not in ['refresh', 'exit']:
        response  = llm()
        response_json = json.loads(response)

        print(Fore.BLUE + json.dumps(response_json,indent=4))

        agent_call = response_json['call_myself']
        while agent_call == 'true':
            tool = response_json['tool']['tool_name']
            code = response_json['tool']['code']
            if tool == 'python' and code != 'None':
                output = exec_code(code)
                print(Fore.YELLOW + "COMPILER OUTPUT: " + output['output'])
                add_context('user', f"OUTPUT FROM PYTHON COMPILER {output['output']}")
            response = llm()
            response_json = json.loads(response)
            print(Fore.BLUE,json.dumps(response_json,indent=4))
            agent_call = response_json['call_myself']


