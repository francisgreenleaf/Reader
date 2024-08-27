#function to run exa search when the user clicks the 'find similar' button

import os 
from exa_py import Exa
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

#config API keys
openai_api_key = os.getenv('openai_api_key')
exa_api_key = os.getenv('exa_api_key')

exa = Exa(exa_api_key)
#initialize the agent - need to figure out how to call this as a utility in the app.py file
@tool 
def search_similar(query: str):
    "Search for web pages similar to the given content"
    return exa.search_similar(
        query, use_autoprompt=True, highlights=True
    )

