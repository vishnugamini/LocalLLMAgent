from flask import Flask, render_template, request
import time
from flask_socketio import SocketIO, emit
import threading
import json
import logging
import uuid
from LLM_response import llm, add_context, refresh
from execute_code import exec_code
from agents import PerpSearch, PicSearch, InstallModule, Sub_Agent, Code_Fixer
from terminal_ui.terminal_animation import (
    kill_child_agent,
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*",async_mode='threading')
search = PerpSearch()
picture = PicSearch()
install = InstallModule()

processing_tasks = {}


def handle_agent_logic(prompt, sid, stop_event):
    try:
        if prompt.lower() == "refresh":
            response = refresh()
            emit_response = {"type": "refresh", "content": response}
            socketio.emit("agent_response", emit_response, room=sid)
            return

        add_context("user", prompt)
        agent_call = "true"

        socketio.emit("agent_status", {"status": "true"}, room=sid)

        while agent_call.lower() == "true":

            if stop_event.is_set():
                logger.info(f"Processing terminated by user for session {sid}")
                break

            socketio.emit("agent_status", {"status": "true"}, room=sid)
            time.sleep(0.1)

            response = llm()
            response_json = json.loads(response)
            msg_to_user = response_json.get("message_to_the_user", "")
            agent_call = response_json.get("call_myself", "false")

            socketio.emit("agent_status", {"status": agent_call}, room=sid)

            socketio.emit(
                "agent_response",
                {"type": "agent_message", "content": msg_to_user},
                room=sid,
            )
            time.sleep(1)

            if agent_call.lower() == "true":

                tool = response_json.get("tool", {}).get("tool_name", "")
                code = response_json.get("tool", {}).get("code", "None")
                query = response_json.get("tool", {}).get("query", "None")
                think = response_json.get("tool", {}).get("thinking_phase", "None")
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
                    time.sleep(1)
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "thinking_message",
                            "content": think,
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    time.sleep(1)

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
                                "output": output['output']
                            },
                            room=sid,
                        )
                        time.sleep(1)
                        msg_ids = str(uuid.uuid4())

                        socketio.emit(
                            "agent_response",
                            {
                                "type": "loading_message",
                                "content": "Corresponding with Error Solver Agent",
                                "msg_id": msg_ids,
                            },
                            room=sid,
                        )
                        time.sleep(1)

                        whole = f'CODE: {code} \n ERROR: {output["output"]}'
                        fixer = Code_Fixer(whole)
                        solution = fixer.initiate()
                        solution = json.loads(solution)
                        a = solution["error_description"]
                        b = solution["code"]
                        c = f"{a}"
                        print(c)
                        add_context(
                            "user",
                            f"Suggestion to fix the code from another agent. Follow this to mitigate the error. {c} \n YOU CAN Always DO A WEB SEARCH IF YOU HAVE TO",
                        )
                        logger.info(f"Solution from Code Fixer: {c}")

                        socketio.emit(
                            "agent_response",
                            {
                                "type": "success_message",
                                "content": "Solution Found",
                                "msg_id": msg_ids,
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
                        time.sleep(1)

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
                        time.sleep(1)

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
                    time.sleep(1)
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
                    time.sleep(1)

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
                    time.sleep(1)
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
                    time.sleep(1)

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
                    time.sleep(1)
                    output = search.search(query)
                    add_context(
                        "user",
                        f"OUTPUT FROM SEARCH RESULTS (NOT VISIBLE TO USER, must be summarized in message to user if needed in great and decorative README FORMAT. use different colors if needed): {output}",
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
                    time.sleep(1)

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
                    time.sleep(1)

                    results_pictures = picture.picSearch(query)
                    add_context(
                        "user",
                        f"OUTPUT FROM PICTURE SEARCH RESULTS {results_pictures}. Now you can proceed to download these using python if the user asked. Also before downloading the pictures, display the download links in readme format to the user in this manner '![Alt text](image-url)'. number them as well. DO the displaying work in msg_to_user section.",
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
                    time.sleep(1)

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
                    time.sleep(1)

                    sub_agent = Sub_Agent()
                    sub_response = sub_agent.initiate(query)
                    socketio.sleep(2)
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "success_message",
                            "content": f"Sub-agent for '{query}' completed.",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    time.sleep(2)
                    add_context(
                        "user",
                        f"SUMMARY FROM SUB AGENT: {sub_response}. You must explain the outcome to the user and then proceed to next task if it exists",
                    )
                    kill_child_agent()
    except Exception as e:
        logger.error(f"Error in handle_agent_logic: {e}")
        emit_response = {
            "type": "error",
            "content": "An error occurred while processing your request.",
        }
        socketio.emit("agent_response", emit_response, room=sid)
    finally:

        socketio.emit("agent_status", {"status": "false"}, room=sid)

        if sid in processing_tasks:
            del processing_tasks[sid]
        logger.info(f"Processing task for session {sid} has ended.")


@socketio.on("user_prompt")
def handle_user_prompt(data):
    prompt = data.get("prompt")
    sid = request.sid

    if prompt:
        if sid in processing_tasks:

            emit_response = {
                "type": "error",
                "content": "A task is already in progress. Please wait or end the current task.",
            }
            emit("agent_response", emit_response, room=sid)
            return

        stop_event = threading.Event()

        thread = socketio.start_background_task(
            handle_agent_logic, prompt=prompt, sid=sid, stop_event=stop_event
        )

        processing_tasks[sid] = {"thread": thread, "stop_event": stop_event}
    else:
        emit_response = {"type": "error", "content": "No prompt provided."}
        emit("agent_response", emit_response, room=sid)


@socketio.on("end_processing")
def handle_end_processing():
    sid = request.sid

    if sid in processing_tasks:

        processing_tasks[sid]["stop_event"].set()
        emit_response = {"type": "info", "content": "Processing has been terminated."}
        emit("agent_response", emit_response, room=sid)
    else:
        emit_response = {
            "type": "error",
            "content": "No active processing to terminate.",
        }
        emit("agent_response", emit_response, room=sid)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app)
