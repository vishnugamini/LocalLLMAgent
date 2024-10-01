from terminal_ui.terminal_animation import initializer
import threading
spinner_thread = threading.Thread(target=initializer)
spinner_thread.start()
from LLM_response import llm, add_context, refresh
from execute_code import exec_code
from agents import PerpSearch, PicSearch, InstallModule, Sub_Agent
from terminal_ui.terminal_animation import (
    search_dots,
    thinking_dots,
    picture_message,
    search_message,
    compiler_message,
    user_message,
    refresh_message,
    initial_message,
    install_module,
    uninstall_module,
    child_agent_message,
    kill_child_agent
)
import json
from colorama import Fore, Style, Back

search = PerpSearch()
picture = PicSearch()
install = InstallModule()

prompt = ""
spinner_thread.do_run = False
spinner_thread.join()
initial_message()
agent_call = "false"  

while prompt != "exit":
    prompt = input(
        Style.BRIGHT + Fore.WHITE + Back.BLACK + "Prompt: " + Style.RESET_ALL
    )
    
    if prompt.lower() == "refresh":
        response = refresh()
        refresh_message(response)

    if prompt not in ["refresh", "exit"]:
        add_context("user", prompt)

    while prompt not in ["refresh", "exit"]:
        spinner_thread = threading.Thread(target=thinking_dots)
        spinner_thread.start()
        
        response = llm()
        
        spinner_thread.do_run = False
        spinner_thread.join()
        
        response_json = json.loads(response)
        msg_to_user = response_json["message_to_the_user"]
        user_message(msg_to_user)

        agent_call = response_json.get("call_myself")

        if agent_call == "true":
            tool = response_json["tool"]["tool_name"]
            code = response_json["tool"]["code"]
            query = response_json["tool"]["query"]

            if tool == "python" and code != "None":
                output = exec_code(code)
                add_context("user", f"OUTPUT FROM PYTHON COMPILER {output['output']}")
                compiler_message(output)

            elif tool == "install" and query != "None":
                install_module(query)
                output = install.install(query)
                compiler_message(output)
                add_context("user", f"OUTPUT FROM INSTALLATION {output}")

            elif tool == "uninstall" and query != "None":
                uninstall_module(query)
                output = install.uninstall(query)
                compiler_message(output)
                add_context("user", f"OUTPUT FROM INSTALLATION {output}")

            elif tool == "search" and query != "None":
                spinner_thread = threading.Thread(target=search_dots)
                spinner_thread.start()
                output = search.search(query)
                spinner_thread.do_run = False
                spinner_thread.join()
                search_message()
                add_context(
                    "user",
                    f"OUTPUT FROM SEARCH RESULTS (NOT VISIBLE TO USER, must be summarized in message to user if needed): {output}",
                )

            elif tool == "picture" and query != "None":
                picture_message()
                results = picture.picSearch(query)
                add_context(
                    "user",
                    f"OUTPUT FROM PICTURE SEARCH RESULTS {results}. Now you can proceed to download these using python if the user asked",
                )

            elif tool == "agent" and query != "None":
                print(query)
                child_agent_message()
                sub_agent = Sub_Agent()
                response = sub_agent.initiate(query)
                add_context("user", f"SUMMARY FROM SUB AGENT: {response}. You must explain the outcome to the user and then proceed to next task if it exists")
                kill_child_agent()
                

        if agent_call != "true":
            break
