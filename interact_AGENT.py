import sys
import time
import threading
from LLM_response import llm, add_context, refresh
from execute_code import exec_code
from search_agent import PerpSearch
from terminal_animation import search_dots, thinking_dots
import json
from colorama import Fore, Back, Style

p = PerpSearch()

prompt = ""
while prompt != "exit":
    prompt = input(Style.BRIGHT + Fore.GREEN + "Prompt: " + Style.RESET_ALL)
    
    if prompt.lower() == "refresh":
        response = refresh()
        print(Style.BRIGHT + Back.MAGENTA + Fore.WHITE + response.center(50) + Style.RESET_ALL)
    
    add_context("user", prompt)
    
    if prompt not in ['refresh', 'exit']:
        spinner_thread = threading.Thread(target=thinking_dots)
        spinner_thread.start()

        response  = llm()

        spinner_thread.do_run = False
        spinner_thread.join()
        print()

        response_json = json.loads(response)
        msg_to_user = response_json["message_to_the_user"]
        # print(Fore.BLUE,json.dumps(response_json,indent=4)) ((USE THIS FOR VERBOSE OUTPUT))
        print(Style.BRIGHT + Back.BLUE + Fore.YELLOW + msg_to_user.center(50) + Style.RESET_ALL + '\n')
        time.sleep(2)
        agent_call = response_json['call_myself']
        while agent_call == 'true':
            tool = response_json['tool']['tool_name']
            code = response_json['tool']['code']
            query = response_json['tool']['query']
            
            if tool == 'python' and code != 'None':
                output = exec_code(code)
                print(Style.BRIGHT + Fore.YELLOW + "=" * 50)  
                print(Style.BRIGHT + Fore.CYAN + "COMPILER OUTPUT".center(50)) 
                print(Style.BRIGHT + Fore.YELLOW + "=" * 50)  
                print(Style.NORMAL + Fore.WHITE + output['output'] + Style.RESET_ALL) 
                print(Style.BRIGHT + Fore.YELLOW + "=" * 50 + '\n')  
                add_context('user', f"OUTPUT FROM PYTHON COMPILER {output['output']}")
                time.sleep(2)
            
            elif tool == 'search' and query != "None":
                spinner_thread = threading.Thread(target=search_dots)
                spinner_thread.start()

                output = p.search(query)

                spinner_thread.do_run = False
                spinner_thread.join()
                print()

                print(Style.BRIGHT + Back.GREEN + Fore.BLACK + "Search Complete. Sending results to Execution Agent".center(50) + Style.RESET_ALL + '\n')
                add_context('user', f"OUTPUT FROM SEARCH RESULTS (NOT VISIBLE TO USER, must be summarized in message to user): {output}")
                time.sleep(2)

            spinner_thread = threading.Thread(target=thinking_dots)
            spinner_thread.start()

            response = llm()

            spinner_thread.do_run = False
            spinner_thread.join()
            print()

            response_json = json.loads(response)
            # print(Fore.BLUE,json.dumps(response_json,indent=4)) ((USE THIS FOR VERBOSE OUTPUT))
            msg_to_user = response_json["message_to_the_user"]
            print(Style.BRIGHT + Back.BLUE + Fore.YELLOW + msg_to_user.center(50) + Style.RESET_ALL + '\n')

            agent_call = response_json['call_myself']
