from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import json
import logging
import uuid

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
    kill_child_agent,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "23"
socketio = SocketIO(app, cors_allowed_origins="*")


search = PerpSearch()
picture = PicSearch()
install = InstallModule()


def handle_agent_logic(prompt, sid):
    try:
        if prompt.lower() == "refresh":
            response = refresh()
            socketio.emit(
                "agent_response", {"type": "refresh", "content": response}, room=sid
            )
            return

        add_context("user", prompt)
        agent_call = "true"

        while agent_call.lower() == "true":
            response = llm()
            response_json = json.loads(response)
            msg_to_user = response_json.get("message_to_the_user", "")
            agent_call = response_json.get("call_myself", "false")

            socketio.emit(
                "agent_response",
                {"type": "agent_message", "content": msg_to_user},
                room=sid,
            )
            socketio.sleep(1)
            if agent_call.lower() == "true":
                tool = response_json.get("tool", {}).get("tool_name", "")
                code = response_json.get("tool", {}).get("code", "None")
                query = response_json.get("tool", {}).get("query", "None")

                msg_id = str(uuid.uuid4())

                if tool == "python" and code != "None":

                    socketio.emit(
                        "agent_response",
                        {
                            "type": "loading_message",
                            "content": "Executing code...",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)

                    output = exec_code(code)
                    add_context(
                        "user", f"OUTPUT FROM PYTHON COMPILER {output['output']}"
                    )

                    if output.get("error"):

                        socketio.emit(
                            "agent_response",
                            {
                                "type": "error_message",
                                "content": f"Error executing code. Running again...",
                                "msg_id": msg_id,
                            },
                            room=sid,
                        )
                    else:
                        socketio.emit(
                            "agent_response",
                            {
                                "type": "success_message",
                                "content": "Executed successfully.",
                                "msg_id": msg_id,
                            },
                            room=sid,
                        )

                        socketio.sleep(1)

                        socketio.emit(
                            "agent_response",
                            {
                                "type": "compiler_message",
                                "content": output["output"],
                                "msg_id": msg_id,
                                "code": code,
                            },
                            room=sid,
                        )
                        socketio.sleep(1)

                elif tool == "install" and query != "None":
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "loading_message",
                            "content": f"Installing module '{query}'...",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)
                    install_module(query)
                    output = install.install(query)
                    add_context("user", f"OUTPUT FROM INSTALLATION {output}")

                    socketio.emit(
                        "agent_response",
                        {
                            "type": "success_message",
                            "content": f"Module '{query}' installed successfully.",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)

                elif tool == "uninstall" and query != "None":
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "loading_message",
                            "content": f"Uninstalling module '{query}'...",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)
                    uninstall_module(query)
                    output = install.uninstall(query)
                    add_context("user", f"OUTPUT FROM UNINSTALLATION {output}")

                    socketio.emit(
                        "agent_response",
                        {
                            "type": "success_message",
                            "content": f"Module '{query}' uninstalled successfully.",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)

                elif tool == "search" and query != "None":
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "loading_message",
                            "content": f"Searching for '{query}'...",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)

                    search_thread = threading.Thread(target=search_dots)
                    search_thread.start()

                    output = search.search(query)

                    search_thread.do_run = False
                    search_thread.join()

                    add_context(
                        "user",
                        f"OUTPUT FROM SEARCH RESULTS (NOT VISIBLE TO USER, must be summarized in message to user if needed): {output}",
                    )

                    socketio.emit(
                        "agent_response",
                        {
                            "type": "search_results",
                            "content": f"Search for '{query}' completed.",
                            "results": output,
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)

                elif tool == "picture" and query != "None":
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "loading_message",
                            "content": f"Searching for pictures related to '{query}'...",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)
                    results_pictures = picture.picSearch(query)
                    add_context(
                        "user",
                        f"OUTPUT FROM PICTURE SEARCH RESULTS {results_pictures}. Now you can proceed to download these using python if the user asked",
                    )
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "success_message",
                            "content": f"Picture search for '{query}' completed.",
                            "msg_id": msg_id,
                            "code": code,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)

                elif tool == "agent" and query != "None":
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "loading_message",
                            "content": f"Initiating sub-agent for '{query}'...",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)
                    sub_agent = Sub_Agent()
                    sub_response = sub_agent.initiate(query)
                    add_context(
                        "user",
                        f"SUMMARY FROM SUB AGENT: {sub_response}. You must explain the outcome to the user and then proceed to next task if it exists",
                    )
                    kill_child_agent()

                    socketio.emit(
                        "agent_response",
                        {
                            "type": "success_message",
                            "content": f"Sub-agent for '{query}' completed.",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    socketio.sleep(1)

    except Exception as e:
        logger.error(f"Error in handle_agent_logic: {e}")
        socketio.emit(
            "agent_response",
            {
                "type": "error",
                "content": "An error occurred while processing your request.",
            },
            room=sid,
        )


@socketio.on("user_prompt")
def handle_user_prompt(data):
    prompt = data.get("prompt")
    sid = request.sid
    if prompt:
        socketio.start_background_task(
            target=handle_agent_logic, prompt=prompt, sid=sid
        )
    else:
        socketio.emit(
            "agent_response",
            {"type": "error", "content": "No prompt provided."},
            room=sid,
        )


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app, debug=True)
