import requests
import os
from dotenv import load_dotenv
import json
import sys
import subprocess
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
from prompts.Child_Agent_prompt import system_msg
from execute_code import exec_code
import threading
import copy

from terminal_ui.terminal_animation2 import (
    sub_search_dots,
    sub_thinking_dots,
    sub_picture_message,
    sub_search_message,
    sub_compiler_message,
    sub_user_message,
    sub_install_module,
    sub_uninstall_module
)

load_dotenv()


class PerpSearch:
    def __init__(self):
        self.key = os.getenv("PERPLEXITY_API")
        self.url = "https://api.perplexity.ai/chat/completions"
        self.msg = [
            {
                "role": "system",
                "content": "Be very precise as the tokens you produce will affect another LLM's response. The information should be up to date, you will be mostly used for searches. Provide valid responses to the LLM. Do not provide extraneous, unsolicited content.The content must be Verbose and Valid. If the agent asks for a link, provide th actual link of the whatever's been asked without any wrapper on top",
            },
        ]
        self.payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": self.msg,
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True,
            "search_domain_filter": ["perplexity.ai"],
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "month",
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1,
        }
        self.headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    def search(self, query):
        self.msg.append({"role": "user", "content": query})
        response = requests.request(
            "POST", self.url, json=self.payload, headers=self.headers
        )
        response = json.loads(response.text)
        response = response["choices"][0]["message"]["content"]
        self.msg.append({"role": "assistant", "content": response})
        return response


class PicSearch:
    def __init__(self):
        self.store = []
        self.url = "https://pixabay.com/api/"
        self.params = {
            "key": "45949203-7642853208ee397943d748af1",
            "q": "",
            "image_type": "photo",
            "pretty": "true",
        }

    def picSearch(self, query):
        query = query.split(" ")
        query = "+".join(query)
        self.params["q"] = query
        response = requests.get(self.url, params=self.params)
        results = response.json()
        results = results["hits"]
        try:
            for links in range(3):
                self.store.append(results[links]["webformatURL"])
            return self.store
        except:
            return "no pictures found! make the search query simpler"

        finally:
            self.store = []


class InstallModule:
    def __init__(self):
        pass

    def install(self, module):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", module],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            return {
                "output": f"{module} module installed successfully",
                "error": False,
            }
        except subprocess.CalledProcessError as e:
            return {
                "output": f"Error occurred while installing {module}:\n{e.stderr}",
                "error": True,
            }
    def uninstall(self, module):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", module, '-y'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            return {
                "output": f"{module} module uninstalled successfully",
                "error": False,
            }
        except subprocess.CalledProcessError as e:
            return {
                "output": f"Error occurred while uninstalling {module}:\n{e.stderr}",
                "error": True,
            }
search = PerpSearch()
picture = PicSearch()
install = InstallModule()
original_system_message = copy.deepcopy(system_msg)


class Sub_Agent():
    class Tool(BaseModel):
        tool_name: str
        required: bool
        thinking_phase: str
        important_parameter: str
        print_statement_to_add: str
        code: Optional[str] = None
        query: Optional[str] = None


    class Message(BaseModel):
        message_from_SeniorAgent: str
        tasks_to_achieve: str
        immediate_task_to_achieve: str
        message_to_Senior_agent: str
        tool: 'Sub_Agent.Tool'
        call_myself: str

    def __init__(self):
        self.key = os.getenv("OPENAPI_KEY")
        self.client = OpenAI(api_key = self.key)
        self.msg = system_msg

    def add_context(self,role, message):
        self.msg.append({"role": role, "content": message})
    
    def llm(self):
        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini", # or "gpt-4o-2024-08-06" (expensive but better output in some instances)
                messages = self.msg,
                response_format= self.Message,
            )
            content = completion.choices[0].message.content
            self.add_context("assistant", content)
            return content
        except Exception as e:
            print(f"Error Occured \n {e}")
    
    def initiate(self,query):
        self.add_context("user", f"MESSAGE FROM SUPERIOR AGENT: {query}")
        call_myself = True
        msg_to_agent = ""
        while call_myself != 'false':
            spinner_thread = threading.Thread(target=sub_thinking_dots)
            spinner_thread.start()

            response = self.llm()

            spinner_thread.do_run = False
            spinner_thread.join()

            response_json = json.loads(response)
            msg_to_agent = response_json["message_to_Senior_agent"]
            sub_user_message(msg_to_agent)
            call_myself = response_json["call_myself"]

            tool = response_json["tool"]["tool_name"]
            code = response_json["tool"]["code"]
            query = response_json["tool"]["query"]

            if tool == "python" and code != "None":
                output = exec_code(code)
                error = output["error"]
                if error == True:
                    self.add_context(
                        "user", f"OUTPUT FROM PYTHON COMPILER {output['output']}"
                    )
                else:
                    self.add_context(
                        "user", f"OUTPUT FROM PYTHON COMPILER {output['output']}"
                    )
                sub_compiler_message(output)

            elif tool == "install" and query != "None":
                sub_install_module(query)
                output = install.install(query)
                sub_compiler_message(output)
                self.add_context("user", f"OUTPUT FROM INSTALLATION {output}")

            elif tool == "uninstall" and query != "None":
                sub_uninstall_module(query)
                output = install.uninstall(query)
                sub_compiler_message(output)
                self.add_context("user", f"OUTPUT FROM INSTALLATION {output}")

            elif tool == "search" and query != "None":
                spinner_thread = threading.Thread(target = sub_search_dots)
                spinner_thread.start()

                output = search.search(query)

                spinner_thread.do_run = False
                spinner_thread.join()

                sub_search_message()
                self.add_context(
                    "user",
                    f"OUTPUT FROM SEARCH RESULTS (NOT VISIBLE TO USER, must be summarized in message to user if needed): {output}",
                )

            elif tool == "picture" and query != "None":
                sub_picture_message()
                results = picture.picSearch(query)
                self.add_context(
                    "user",
                    f"OUTPUT FROM PICTURE SEARCH RESULTS {results}. Now you can proceed to download these using python if the user asked",
                )

        self.msg = original_system_message
        return msg_to_agent



from pydantic import BaseModel
class Code_Agent():
    class Code(BaseModel):
        Thinking_Stage: str
        code: str
        

    def __init__(self, query):
        self.key = os.getenv("OPENAPI_KEY")
        self.query = query

    def initiate(self):
        client = OpenAI(api_key = self.key)
        messages = [
            {"role": "system", "content":"You are a specialist in writing HTML, CSS, JAVASCRIPT, PYTHON, or ANY LANGUAGE CODE. while wrtiting code, do not use escape quotes or add unnecessary backslashes as the code you are writing is being passed to another LLM, Make sure to only provide the content specified in the query"},
            {"role": "system", "content": "you will provide output in json format.Here is an example of the required JSON structure {'Thinking_stage': 'use chain of thought process to think through the query and write down what you wish to implement. do not make errors', 'code': 'write down just the code here ad nothing else'}"}
        ]
        messages.append({"role": "user","content": self.query})
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages = messages,
            response_format= self.Code
        )
        content = completion.choices[0].message.content
        messages.append({"role": "assistant","content": content})
        content = json.loads(content)
        print(content['code'])
    
class Code_Error_Fixer():

    def __init__(self, query):
        self.query = query


