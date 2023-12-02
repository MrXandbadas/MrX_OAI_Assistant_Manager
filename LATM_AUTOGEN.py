# %pip install "pyautogen~=0.2.0b5


## Function Schema and implementation:
import asyncio
import json
import logging
from typing import Dict, Union
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from assistant_manager.gpt_assistant_custom import GPTAssistantAgent
from autogen.agentchat.contrib.teachable_agent import TeachableAgent
import autogen
from autogen import UserProxyAgent
from assistant_manager.assistant_manager import OAI_Assistant
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread_create_and_run_params import ToolAssistantToolsFunction
import assistant_manager.functions.dynamic.dynamic_functions as dynamic_functions
from assistant_manager.utils import file_operations, special_functions
from assistant_manager.utils.special_functions import append_new_tool_function_and_metadata




async def main_app():
        # Create an assistant manager
    org_id = 'org'
    api_key='apikey'

    assistantManager = OAI_Assistant(api_key=api_key, organization=org_id)

    #retooling, tool_list = assistantManager.re_tool(autogen=True)
    tool_maker_tool_list = assistantManager.re_tool(autogen=True, tool_names=["append_new_tool_function_and_metadata", "write_file", "read_file"])

    #print(f"Tool Maker List: {tool_maker_tool_list}")
    function_mapy = assistantManager.get_function_map(tool_maker_tool_list)          

    with open("assistant_manager/autogen_assistants/tool_maker.json", "r") as tool_maker_json:
        tool_maker = json.load(tool_maker_json)

        tool_maker["tools"] = tool_maker_tool_list
        tool_maker["instructions"] = """##
You must ensure the function calling metadata is provided in the correct format.
Ensure the metadata created has the following sections:
"tool_name", "tool_required",  "tool_description", "tool_properties"
        Properties type must be fully written in a string format list:
        "string", "integer", "boolean"
        ###
        EXAMPLE CORRECT FUNCTION CALLING METATDATA FORMAT:
        "read_File": {
            "tool_name": "read_file",
            "tool_required": "file_name",
            "tool_description": "Read the content of a file",
            "tool_properties": {
                "file_name": {
                    "type": "string",
                    "description": "The name of the file"
                }
            },
        "tool_meta_description": "Takes a file name path and returns text contents.
            }
        ####"""

    #Get the personal assistant from the json file
    with open("assistant_manager/autogen_assistants/personal_assistant.json", "r") as assistant_json:
        personal_assistant = json.load(assistant_json)
        
    #Get the critic assistant from the json file
    with open("assistant_manager/autogen_assistants/critic_default.json", "r") as critic_json:
        critic_default = json.load(critic_json)


    default_assistants = [personal_assistant, critic_default, tool_maker]
    

    personal_assistant["config_list"]= [
            { 
                "model": personal_assistant["model"],  # 0631 or newer is needed to use functions
                "api_key": api_key
            }
    ]
    critic_default["config_list"] = [
            { 
                "model": critic_default["model"],  # 0631 or newer is needed to use functions
                "api_key": api_key
            }
    ]
    tool_maker["config_list"] = [
            { 
                "model": tool_maker["model"],  # 0631 or newer is needed to use functions
                "api_key": api_key,
                "tools": tool_maker["tools"]
            }
    ]

    
    default_assistants = await assistantManager.search_for_assistants(default_assistants)


    # Now we have the id's of the assistants we want to use
    # Lets assign the Id's to the variables

    llm_config =assistantManager.create_llm_config_list(config_list=personal_assistant["config_list"], assistant_id=personal_assistant["id"])
    llm_config_critic = assistantManager.create_llm_config_list(config_list=critic_default["config_list"], assistant_id=critic_default["id"])
    llm_config_tool_maker = assistantManager.create_llm_config_list(config_list=tool_maker["config_list"], assistant_id=tool_maker["id"], tools=tool_maker_tool_list)


    from autogen.agentchat import AssistantAgent



    # Define user proxy agent
    llm_config = {"config_list": [
            { 
                "model": "gpt-4-1106-preview",  # 0631 or newer is needed to use functions
                "api_key": api_key
            }
    ],
    "cache_seed": 45}
    user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin. Can execute code on behalf of the user and provide the results",
    code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
    human_input_mode="TERMINATE"
    )

    # define two GPTAssistants
    toolmaker = GPTAssistantAgent(
        name="ToolMaker",
        llm_config=llm_config_tool_maker,
        instructions=None,
        human_input_mode="TERMINATE",
        function_map=function_mapy
    )

    toolmaker.register_function(
    function_map=function_mapy
    )

    assistant_agent = GPTAssistantAgent(
        name="assistant_manager",
        llm_config=llm_config
    )
    critic = GPTAssistantAgent(
        name="Critic",
        instructions=None,
        llm_config=llm_config_critic

    )
    agents=[critic,assistant_agent, toolmaker,user_proxy]
    assistantManager.autogen_assistants = []
    
    #iterate through agents
    for agent in agents:
        assistantManager.autogen_assistants.append(agent)


    # define group chat
    groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=10)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    user_proxy.initiate_chat(manager, message="Create a tool that can take a screenshot and use openai vision api to query the image.")

# Run the main app
asyncio.run(main_app())
