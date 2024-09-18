from terminal_animation import initializer
import threading
spinner_thread = threading.Thread(target=initializer)
spinner_thread.start()

from LLM_response import llm, add_context, refresh
from execute_code import exec_code
from agents import PerpSearch, PicSearch, InstallModule
from terminal_animation import (
    search_dots,
    thinking_dots,
    picture_message,
    search_message,
    compiler_message,
    user_message,
    refresh_message,
    initial_message,
    install_module,
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
while prompt != "exit":

    prompt = input(
        Style.BRIGHT + Fore.WHITE + Back.BLACK + "Prompt: " + Style.RESET_ALL
    )

    if prompt.lower() == "refresh":
        response = refresh()
        refresh_message(response)

    if prompt not in ["refresh", "exit"]:
        add_context("user", prompt)
        spinner_thread = threading.Thread(target=thinking_dots)
        spinner_thread.start()

        response = llm()

        spinner_thread.do_run = False
        spinner_thread.join()
        print()

        response_json = json.loads(response)
        msg_to_user = response_json["message_to_the_user"]
        user_message(msg_to_user)
        print(Fore.BLUE,json.dumps(response_json,indent=4)) ##((USE THIS FOR VERBOSE OUTPUT))

        agent_call = response_json["call_myself"]
        while agent_call == "true":
            tool = response_json["tool"]["tool_name"]
            code = response_json["tool"]["code"]
            query = response_json["tool"]["query"]

            if tool == "python" and code != "None":
                output = exec_code(code)
                error = output["error"]
                text = "\n There seems to be an error in the code. Throughly understand why it arised and mitigate it immediately by fixing the code. Do not make the same error again"
                if error == True:
                    add_context(
                        "user", f"OUTPUT FROM PYTHON COMPILER {output['output']} {text}"
                    )
                else:
                    add_context(
                        "user", f"OUTPUT FROM PYTHON COMPILER {output['output']}"
                    )
                compiler_message(output)

            elif tool == "install" and query != "None":
                install_module(query)
                output = install.install(query)
                compiler_message(output)
                add_context("user", f"OUTPUT FROM INSTALLATION {output}")

            elif tool == "search" and query != "None":
                spinner_thread = threading.Thread(target=search_dots)
                spinner_thread.start()

                output = search.search(query)

                spinner_thread.do_run = False
                spinner_thread.join()
                print()

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

            spinner_thread = threading.Thread(target=thinking_dots)
            spinner_thread.start()

            response = llm()

            spinner_thread.do_run = False
            spinner_thread.join()
            print()

            response_json = json.loads(response)
            print(Fore.BLUE,json.dumps(response_json,indent=4))## ((USE THIS FOR VERBOSE OUTPUT))
            msg_to_user = response_json["message_to_the_user"]
            user_message(msg_to_user)
            agent_call = response_json["call_myself"]
