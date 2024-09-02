from LLM_response import llm, add_context
from execute_code import exec_code
import time
import json
from colorama import Fore

prompt = ""
while prompt != "exit":
    prompt = input(Fore.GREEN + "Prompt: ")
    add_context("user",prompt)

    response  = llm()
    response_json = json.loads(response)

    print(Fore.BLUE + json.dumps(response_json,indent=4))

    agent_call = response_json['call_myself']

    while agent_call == 'true':
        code = response_json['tool']['code']
        if code != 'None':
            output = exec_code(code)
            print(Fore.YELLOW + "COMPILER OUTPUT: " + output['output'])
            add_context('user', f"OUTPUT FROM PYTHON COMPILER {output['output']}")
        response = llm()
        response_json = json.loads(response)
        print(Fore.BLUE,json.dumps(response_json,indent=4))
        agent_call = response_json['call_myself']


