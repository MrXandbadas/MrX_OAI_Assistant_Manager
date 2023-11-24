# %pip install "pyautogen~=0.2.0b5


## Function Schema and implementation:
import asyncio
import logging
import os
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)




ossinsight_api_schema = {
  "name": "ossinsight_data_api",
  "parameters": {
    "type": "object",
    "properties": {
      "question": {
        "type": "string",
        "description": (
            "Enter your GitHub data question in the form of a clear and specific question to ensure the returned data is accurate and valuable. "
            "For optimal results, specify the desired format for the data table in your request."
        ),
      }
    },
    "required": [
      "question"
    ]
  },
  "description": "This is an API endpoint allowing users (analysts) to input question about GitHub in text format to retrieve the realted and structured data."
}

def get_ossinsight(question):
    """
    Retrieve the top 10 developers with the most followers on GitHub.
    """
    url = "https://api.ossinsight.io/explorer/answer"
    headers = {"Content-Type": "application/json"}
    data = {
        "question": question,
        "ignoreCache": True
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        answer = response.json()
    else:
        return f"Request to {url} failed with status code: {response.status_code}"

    report_components = []
    report_components.append(f"Question: {answer['question']['title']}")
    if answer['query']['sql']  != "":
        report_components.append(f"querySQL: {answer['query']['sql']}")

    if answer.get('result', None) is None or len(answer['result']['rows']) == 0:
        result = "Result: N/A"
    else:
        result = "Result:\n  " + "\n  ".join([str(row) for row in answer['result']['rows']])
    report_components.append(result)

    if  answer.get('error', None) is not None:
        report_components.append(f"Error: {answer['error']}")
    return "\n\n".join(report_components)

from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen import UserProxyAgent
from assistant_manager import OAI_Assistant
from openai.types.beta.assistant import Assistant
import dynamic_functions
from utils import file_operations, special_functions


async def create_agent(Assistant_config,assistantManager: OAI_Assistant):
    name = Assistant_config["name"]
    instructions = Assistant_config["instructions"]
    tools = Assistant_config["tools"]
    model = Assistant_config["model"]

    assistant_obj: Assistant = assistantManager.client.assistants.create(
        name=name,
        instructions=instructions,
        tools=tools,
        model=model
    )

    assistant_id = assistant_obj.id

    return assistant_id
async def main_app():
        # Create an assistant manager{
    api_key = "APIKEYHERE"
    org_id = "ORGIDHERE"

    assistantManager = OAI_Assistant(api_key=api_key, organization=org_id)

    retooling, tool_list = assistantManager.re_tool(autogen=True)

    oss_analyst_default = {
    "name":"Customer Service Assistant_01",
    "instructions":"""Hello, Open Source Project Analyst. You'll conduct comprehensive evaluations of open source projects/organizations/projects on the GitHub and Arxiv platforms,
    analyzing project trajectories, contributor engagements, open source trends, and other vital parameters.
    Please carefully read the context of the conversation to identify the current analysis question or problem that needs addressing.""",
    "tools":tool_list,
    "model":"gpt-4-1106-preview"
    }

    config_list = [
            { 
                "model": "gpt-4-1106-preview",  # 0631 or newer is needed to use functions
                "api_key": api_key
            }
    ]

    # Search for existing assistant
    assistant = assistantManager.client.assistants.list()
    # Returns a sync cursor page. We need to search it for the assistant we want
    assistant_id = None
    for a in assistant.data:
        if a.name == oss_analyst_default["name"]:
            assistant_id = a.id
            break
    if assistant_id is None:
        assistant_id = await create_agent(oss_analyst_default,assistantManager)
        print(f"Created new assistant with id: {assistant_id}")
    else:
        print(f"Found existing assistant with id: {assistant_id}")

    

    llm_config = {
        "config_list": config_list,
        "assistant_id": assistant_id,
        "tools": tool_list
    }
    function_mapy = {}

    if retooling == True:
        for tool in tool_list:
            if tool["type"] == "function":
                #Check tht it is in dynamic_functions if not check special_functions or file_operations
                if tool["function"]["name"] in dynamic_functions.__dict__:
                    print(f"Found {tool['function']['name']} in dynamic_functions")
                    # Now it has been found add it to the function_mapy using a callable function trick
                    function: callable = dynamic_functions.__dict__[tool["function"]["name"]]
                    function_mapy[tool["function"]["name"]] = function
                elif tool["function"]["name"] in special_functions.__dict__:
                    print(f"Found {tool['function']['name']} in special_functions")
                    # Now it has been found add it to the function_mapy
                    function: callable = special_functions.__dict__[tool["function"]["name"]]
                    function_mapy[tool["function"]["name"]] = function
                elif tool["function"]["name"] in file_operations.__dict__:
                    print(f"Found {tool['function']['name']} in file_operations")
                    # Now it has been found add it to the function_mapy
                    function: callable = file_operations.__dict__[tool["function"]["name"]] 
                    function_mapy[tool["function"]["name"]] = function            
    else:
        function_mapy = {
            "oos_insight": get_ossinsight,
        }



    oss_analyst = GPTAssistantAgent(
        name="OSS Analyst",                            
        instructions=(
            "Hello, Open Source Project Analyst. You'll conduct comprehensive evaluations of open source projects/organizations/projects on the GitHub and Arxiv platforms, "
            "analyzing project trajectories, contributor engagements, open source trends, and other vital parameters. "
            "Please carefully read the context of the conversation to identify the current analysis question or problem that needs addressing."
        ),
        llm_config=llm_config,
    )
    oss_analyst.register_function(
    function_map=function_mapy,
    )

    user_proxy = UserProxyAgent(name="user_proxy",
        code_execution_config={
            "work_dir": "coding"
        },
        is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1)


    user_proxy.initiate_chat(oss_analyst, message="Please find the 10 latest papers on the advancements in Large Language Models and their applications in Assistants or Agents")
    

# Run the main app
asyncio.run(main_app())
