import sys
import time
import threading
from LLM_response import llm, add_context, refresh
from execute_code import exec_code
from searchtool import PerpSearch
from terminal_animation import search_dots,thinking_dots
import json
from colorama import Fore

p = PerpSearch()

prompt = ""
while prompt != "exit":
    prompt = input(Fore.GREEN + "Prompt: ")
    if prompt.lower() == "refresh":
        response = refresh()
        print(Fore.YELLOW + response)
    add_context("user",prompt)
    if prompt not in ['refresh', 'exit']:
        spinner_thread = threading.Thread(target=thinking_dots)
        spinner_thread.start()

        response  = llm()

        spinner_thread.do_run = False
        spinner_thread.join()
        print()

        response_json = json.loads(response)

        print(Fore.BLUE + json.dumps(response_json,indent=4))

        agent_call = response_json['call_myself']
        while agent_call == 'true':
            tool = response_json['tool']['tool_name']
            code = response_json['tool']['code']
            query = response_json['tool']['query']
            if tool == 'python' and code != 'None':
                output = exec_code(code)
                print(Fore.YELLOW + "COMPILER OUTPUT: " + output['output'])
                add_context('user', f"OUTPUT FROM PYTHON COMPILER {output['output']}")
            elif tool == 'search' and query != "None":
                spinner_thread = threading.Thread(target=search_dots)
                spinner_thread.start()

                output = p.search(query)

                spinner_thread.do_run = False
                spinner_thread.join()
                print()
                print(Fore.YELLOW + "Search Complete.Sending results to execution Agent")
                add_context('user', f"OUTPUT FROM SEARCH RESULTS {output}")

            spinner_thread = threading.Thread(target=thinking_dots)
            spinner_thread.start()

            response = llm()

            spinner_thread.do_run = False
            spinner_thread.join()
            print()

            response_json = json.loads(response)
            print(Fore.BLUE,json.dumps(response_json,indent=4))
            agent_call = response_json['call_myself']


