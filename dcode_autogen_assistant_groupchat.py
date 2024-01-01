# %pip install "pyautogen~=0.2.0b5


## Function Schema and implementation:
import asyncio
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen.agentchat.contrib.teachable_agent import TeachableAgent
import autogen
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

    #retooling, tool_list = assistantManager.re_tool(autogen=True)
    tool_list =[]
    retooling = True


    read_write_tools = ['read_file', 'write_file']

    planner_default = {
    "name":"Planner",
    "instructions":"Planner. Responsible for formulating a plan of action for the team to follow.",
    "tools":assistantManager.get_tool_list_by_names(read_write_tools),
    "model":"gpt-4-1106-preview"
    }


    critic_default = {
    "name":"Critic",
    "instructions":"Critic. Responsible for evaluating the quality of the team's work and responses. Provides feedback on the team's performance and approaches.",
    "tools":assistantManager.get_tool_list_by_names(read_write_tools),
    "model":"gpt-4-1106-preview"
    }

    digital_kodie_tools = ['get_weather_forcast', 'append_new_tool_function_and_metadata', 'get_arxiv_papers']
    digital_kodie_tools_list = assistantManager.get_tool_list_by_names(digital_kodie_tools)
    digitalKodie_default = {
    "name":"Digital Kodie",
    "instructions":"Digital Kodie. Digital version of the User using the system. Acts as a inquisitive human user.",
    "tools":digital_kodie_tools_list,
    "model":"gpt-4-1106-preview"
    }

    default_assistants = [planner_default, critic_default, digitalKodie_default]
    


    config_list = [
            { 
                "model": "gpt-4-1106-preview",  # 0631 or newer is needed to use functions
                "api_key": api_key
            }
    ]

    # Search for existing assistant
    assistant = assistantManager.client.assistants.list()
    # Returns a sync cursor page. We need to search it for the assistant we want
    
    assistant_dict_name_id = assistantManager.list_assistants_names()
    #Iterate through the deafult_assistants
    for assistant_deafult in default_assistants:
        #Check if the assistant exists
        if assistant_deafult["name"] in assistant_dict_name_id.keys():
            #If it does, get the id
            assistant_deafult["id"] = assistant_dict_name_id[assistant_deafult["name"]]
        else:
            #If it doesn't, create it and get the id
            #assistant_deafult["id"] = await create_agent(assistant_deafult, assistantManager)
            print(f"I want to create a new {assistant_deafult['name']} with id: {assistant_deafult['id']}")

    
    # Now we have the id's of the assistants we want to use
    # Lets assign the Id's to the variables
    planner_id = planner_default["id"]
    critic_id = critic_default["id"]
    digital_kodie_id = digitalKodie_default["id"]


    llm_config = {
        "config_list": config_list,
        "assistant_id": digital_kodie_id,
        "tools": tool_list
    }
    llm_config_critic = {
        "config_list": config_list,
        "assistant_id": critic_id,
    }
    llm_config_planner = {
        "config_list": config_list,
        "assistant_id": planner_id,
    }
    function_mapy = {}

    if retooling == True:
        # Now w

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
        }
    from autogen.agentchat import AssistantAgent

    # Define user proxy agent
    llm_config = {"config_list": config_list, "cache_seed": 45}
    user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin. Can execute code on behalf of the user and provide the results",
    code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
    human_input_mode="TERMINATE"
    )

    teachable_agent = TeachableAgent(
        name="teachable_agent",
        system_message="Teachable agent. You take note of what has been said, done or used and learn from it. When responding with code please ensure you do not wrap it in code blocks as the system wil ltry to execute it. It should be conversational based and a high level of detail including the code used and the results should be provided. You Always help the team before any action in approved",
        teach_config={
            "reset_db": False,
            "path_to_db_dir": "teachable_agent_db",
        },
        llm_config={
            "config_list": config_list,
        }
    )

    instructionsaa = """You are a high level programmer and assistant. You only follow approved plans and actions. Provide any and all code in code blocks. Ensure any package requirement steps are listed first. 
    """

    # define two GPTAssistants
    coder = GPTAssistantAgent(
        name="Coder",
        llm_config={
            "config_list": config_list,
        },
        instructions=instructionsaa
    )

    planner = GPTAssistantAgent(
        name="Planner",
        llm_config=llm_config_planner,
    )
    digitalkodie = GPTAssistantAgent(
        name="Digital_Kodie",
        instructions="Digital Kodie. Interfaces and talks to the userproxy on behalf of the team.",
        llm_config=llm_config,
        human_input_mode="TERMINATE",

    )
    agents=[digitalkodie,planner, coder, teachable_agent,user_proxy]
    assistantManager.autogen_assistants = []
    
    #iterate through agents
    for agent in agents:
        assistantManager.autogen_assistants.append(agent)


    # define group chat
    groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=10)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    user_proxy.initiate_chat(digitalkodie, message="find papers on LLM applications from arxiv in the last week, create a markdown table of different domains.")
    teachable_agent.learn_from_user_feedback()
    teachable_agent.close_db()

# Run the main app
asyncio.run(main_app())
