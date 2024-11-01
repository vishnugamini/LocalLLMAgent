from flask import Flask, render_template, request
from flask import send_from_directory
import time
from flask_socketio import SocketIO, emit
from miscellaneous import shorten_url
import threading
import json
import logging
import uuid
import webbrowser
import os
from LLM_response import llm, add_context, refresh
from execute_code import exec_code
from threading import Event
from agents import (
    PerpSearch,
    PicSearch,
    InstallModule,
    Sub_Agent,
    Code_Fixer,
    GenerateImage,
    file_judger,
    PicDownloader,
    Labels,
    DeepResearch,
    ReseachSummary
)
from terminal_ui.terminal_animation import (
    kill_child_agent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
search = PerpSearch()
picture = PicSearch()
install = InstallModule()
image = GenerateImage()
processing_tasks = {}
research = DeepResearch()
summary = ReseachSummary()
lab = Labels()

def handle_search_logic(prompt, sid, stop_event):
    try:
        @socketio.on("refresh")
        def refresh_memory():
            response = refresh()
            summary.refresh()
            research.refresh()
            search.refresh()
            emit_response = {"type": "refresh", "content": response}
            socketio.emit("agent_response", emit_response, room=sid)

        msg_id = str(uuid.uuid4())
        socketio.emit("agent_status", {"status": "true"}, room=sid)
        params = lab.initiate(prompt)
        labels = params["labels"]
        labels.append("Compiling information, please hold on for a moment!")
        think = params["think"]
        length = len(labels)
        content = f"QUERY: {prompt}"
        socketio.emit('search_response', {
        "type": 'init',
        "labels":labels,
        "msg_id": msg_id
        })
        time.sleep(0.5)
        for tasks in range(0,length - 1):
            socketio.emit('search_response', {
            "type": 'update',
            "index": tasks,
            "status": 'searching',
            "msg_id": msg_id
            })
            time.sleep(1)
            answer = research.search(labels[tasks])
            content = content + f"{labels[tasks]} \n {answer} \n"
            socketio.emit('search_response', {
            "type": 'update',
            "index": tasks,
            "status": 'complete',
            "msg_id": msg_id
            })
            time.sleep(2)
        time.sleep(1)
        socketio.emit('search_response', {
        "type": 'update',
        "index": length - 1,
        "status": 'searching',
        "msg_id": msg_id
        })
        time.sleep(1)
        summarize = summary.initiate(content)
        socketio.emit('search_response', {
        "type": 'update',
        "index": length - 1,
        "status": 'complete',
        "msg_id": msg_id,
        })
        time.sleep(1)
        socketio.emit(
            "agent_response",
            {"type": "search_agent_message", "content": summarize},
            room=sid,
        )
        time.sleep(1)

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

def handle_agent_logic(prompt, sid, stop_event):
    try:
        @socketio.on("refresh")
        def refresh_memory():
            response = refresh()
            summary.refresh()
            research.refresh()
            search.refresh()
            emit_response = {"type": "refresh", "content": response}
            socketio.emit("agent_response", emit_response, room=sid)

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
            msg_id = str(uuid.uuid4())
            response_json = json.loads(response)
            msg_to_user = response_json.get("message_to_the_user", "")
            agent_call = response_json.get("call_myself", "false")
            task = response_json.get("immediate_task_to_achieve", "")
            if task != "":
                socketio.emit(
                    "agent_response",
                    {
                        "type": "thinking_message",
                        "content": task,
                        "msg_id": msg_id,
                    },
                    room=sid,
                )
                time.sleep(1)

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
                                "output": output["output"],
                                "code": code,
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
                        c = f"{a} \n CODE to FIX {b}"
                        add_context(
                            "user",
                            f"code to fix the error \n {b}. something to also keep in mind When writing multi-line HTML, CSS, JS, or Python code, always enclose it within triple quotes (\"\"\"\"). "
                            "Ensure that you do not include '\\n' or '\"' in it, as it will cause errors.",
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
                        time.sleep(1)
                    else:
                        f = file_judger(code)
                        g = PicDownloader(code)
                        thread = threading.Thread(target=f.initiate)
                        thread2 = threading.Thread(target=g.initiate)
                        thread.start()
                        thread2.start()
                        socketio.emit(
                            "agent_response",
                            {
                                "type": "success_message",
                                "content": "Executed successfully.",
                                "msg_id": msg_id,
                            },
                            room=sid,
                        )
                        time.sleep(0.4)
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
                        time.sleep(0.1)
                elif tool == "generate" and query != "None":
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "loading_message",
                            "content": f"Generating Picture for '{query}'. This might take a while. Please hold on.",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    time.sleep(0.2)
                    link = image.generate(query)
                    link = shorten_url(link)
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "success_message",
                            "content": f"Pictured Generated Successfully",
                            "msg_id": msg_id,
                        },
                        room=sid,
                    )
                    add_context(
                        "user",
                        f"OUTPUT FROM PICTURE GENERATION {link}. Display it in readme format to the user. This is the format '![Alt text](image-url)'. download  it subsequently if the task involves downloading or displaying it in a html document etc.",
                    )
                elif tool == "suggestions" and query != "None":
                    socketio.emit("suggestions", { "suggestions": query})
                    time.sleep(1)
                    exit_event = Event()

                    while not exit_event.is_set():
                        @socketio.on("selected_suggestions")
                        def selected_suggestions(data):
                            exit_event.set()  
                            sug = data['suggestions']
                            print(sug[0:])
                            add_context("user", f". These are the additional features requested by user based on your suggestions.Make sure to work on implementing these additonal features as well: {sug[0:]}. Mention that so and so features will be implemented and then implement them. All of these features must be implemented when you produce code.")
                                                

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
                            "content": f"Executed Successfully",
                            "msg_id": msg_id
                        },
                        room=sid,
                    )
                    time.sleep(0.4)
                    socketio.emit(
                        "agent_response",
                        {
                            "type": "compiler_message",
                            "content": f"Module '{query}' installed successfully.",
                            "msg_id": msg_id,
                            "code": output["code"]
                        },
                        room=sid,
                    )

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
                    time.sleep(0.4)
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
                    time.sleep(0.3)
                    output = search.search(query)
                    add_context(
                        "user",
                        f"OUTPUT FROM SEARCH RESULTS {output} (NOT VISIBLE TO USER, must be summarized in message_to_the_user only if user explicitly asked or proceed to the next task) in great and decorative README FORMAT in message_to_the_user. use different colors if needed). once summarizing is done, ask the user if he wants the information to be presented in a html document in a beautiful manner. if he says yes, make sure to include a lot of css to beautify it. But if you are in the middle of another task you can skip the step of asking the user",
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
                    time.sleep(0.2)

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
                    time.sleep(0.3)

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
                    time.sleep(0.2)

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
    mode = data.get("mode")
    sid = request.sid

    if prompt and mode == 'agent':
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

    elif prompt and mode == "search":
        if sid in processing_tasks:

            emit_response = {
                "type": "error",
                "content": "A task is already in progress. Please wait or end the current task.",
            }
            emit("agent_response", emit_response, room=sid)
            return

        stop_event = threading.Event()

        thread = socketio.start_background_task(
            handle_search_logic, prompt=prompt, sid=sid, stop_event=stop_event
        )

        processing_tasks[sid] = {"thread": thread, "stop_event": stop_event}
    else:
        emit_response = {"type": "error", "content": "No prompt provided."}
        emit("agent_response", emit_response, room=sid)


@app.route("/render/<path:filename>")
def serve_render_files(filename):
    return send_from_directory("render", filename)


@socketio.on("request_file_contents")
def handle_request_file_contents():
    sid = request.sid
    try:
        files = ["index.html", "styles.css", "test.js"]
        file_contents = {}

        for file_name in files:
            file_path = os.path.join("render", file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                file_contents[file_name] = content

        emit("file_contents", file_contents, room=sid)
    except Exception as e:
        logger.error(f"Error reading files: {e}")
        emit("file_contents", {"error": "Failed to read files."}, room=sid)


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
    app.run()