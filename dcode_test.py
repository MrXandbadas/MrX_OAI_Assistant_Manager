# %pip install "pyautogen~=0.2.0b5


## Function Schema and implementation:
import asyncio
import logging
import os
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen import UserProxyAgent
from assistant_manager.assistant_manager import OAI_Assistant
from openai.types.beta.assistant import Assistant
import assistant_manager.functions.dynamic.dynamic_functions as dynamic_functions
from assistant_manager.utils import file_operations, special_functions


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
    org_id = 'org'
    api_key='apikey'
    assistantManager = OAI_Assistant(api_key=api_key, organization=org_id)

    tool_list = assistantManager.re_tool(autogen=True, tool_names=["append_new_tool_function_and_metadata"])

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

    
    llm_config_notool = {
        "config_list": config_list,
        "assistant_id": assistant_id,
    }

    llm_config = {
        "config_list": config_list,
        "assistant_id": assistant_id,
        "tools": tool_list
    }
    function_mapy = assistantManager.get_function_map(tool_list)


    oss_analyst = GPTAssistantAgent(
        name="OSS Analyst",                            
        instructions=(
            "Hello, Open Source Project Analyst. You'll conduct comprehensive evaluations of open source projects/organizations/projects on the GitHub and Arxiv platforms, "
            "analyzing project trajectories, contributor engagements, open source trends, and other vital parameters. "
            "Please carefully read the context of the conversation to identify the current analysis question or problem that needs addressing."
        ),
        llm_config=llm_config,
    )
    print(f"fmapy: {function_mapy}")
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
