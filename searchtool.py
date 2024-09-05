import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

class PerpSearch:
    def __init__(self):
        self.key = os.getenv("PERPLEXITY_API")
        self.url = "https://api.perplexity.ai/chat/completions"
        self.msg = [
        {
            "role": "system",
            "content": "Be very precise as the tokens you produce will affect another LLM's response. The information should be up to date, you will be mostly used for searches. Provide valid responses to the LLM. Do not provide extraneous, unsolicited content."
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
            "frequency_penalty": 1
        }
        self.headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
    
    def search(self,query):
        self.msg.append({"role": "user", "content": query})
        response = requests.request("POST", self.url, json=self.payload, headers=self.headers)
        response = json.loads(response.text)
        response = response['choices'][0]['message']['content'] 
        self.msg.append({"role": "assistant", "content": response})
        return response
