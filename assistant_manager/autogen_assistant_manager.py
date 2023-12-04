from assistant_manager.assistant_tools import Tooling
from assistant_manager.interface_base import InterfaceBase
import logging
import assistant_manager.functions.dynamic.dynamic_functions as dynamic_functions
from assistant_manager.utils import file_operations, special_functions

class AutogenAssistantManager(Tooling):

    def __init__(self, api_key, organization, timeout=None, log_level=logging.INFO):
        """
        Initializes an instance of AssistantManager.

        Args:
            api_key (str): The OpenAI API key.
            organization (str): The OpenAI organization ID.
            timeout (Optional[int]): The timeout for API requests, in seconds.
            log_level (Optional[int]): The logging level to use.

        Returns:
            None
        """
        super().__init__(api_key=api_key, organization=organization, timeout=timeout, log_level=log_level)


    async def create_agent(self,Assistant_config):
        name = Assistant_config["name"]
        instructions = Assistant_config["instructions"]
        tools = Assistant_config["tools"]
        model = Assistant_config["model"]

        assistant_obj = self.client.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools,
            model=model
        )

        assistant_id = assistant_obj.id

        return assistant_id
    
    def create_llm_config_list(self, config_list, assistant_id, tools=None):
        llm_config = {
            "config_list": config_list,
            "assistant_id": assistant_id
        }

        if tools is not None:
            if isinstance(tools, list):
                # If tools is a list, add each tool to the configuration
                llm_config["tools"] = [{"type": "function", "function": tool} for tool in tools]
                print(f"Tools: {llm_config['tools']}")
            else:
                llm_config["tools"] = tools

        return llm_config


    async def search_for_assistants(self, assistant_list):
        """
        Searches for assistants by their name property

        """
        assistant_dict_name_id = self.list_assistants_names()
        # Iterate through the default_assistants
        new_list = []
        for assistant_default in assistant_list:
            # Check if the assistant exists
            # Print the names
            print(assistant_default["name"])

            if assistant_default["name"] in assistant_dict_name_id.keys():
                # If it does, get the id
                assistant_default["id"] = assistant_dict_name_id[assistant_default["name"]]
                #add the complete new info to the new list
                new_list.append(assistant_default)
            else:
                # If it doesn't, create it and get the id
                # assistant_default["id"] = await create_agent(assistant_default, assistantManager)
                #Save the ID
                self.message_user(f"I want to create a new {assistant_default['name']} with id: {assistant_default['id']}")
                self.message_user(f"Please confirm the creation of the assistant {assistant_default['name']}")
                options = ["Yes", "No"]
                choice = self.get_multiple_choice_input(options)
                # Choice is a int
                if choice == 0:
                    # Yes
                    self.message_user(f"Creating {assistant_default['name']}...")
                    new_id = await self.create_agent(assistant_default)
                    assistant_default["id"] = new_id
                    #add the complete new info to the new list
                    new_list.append(assistant_default)
                else:
                    # No. Check if the user would like to select an existing assistant
                    self.message_user(f"Would you like to select an existing assistant?")
                    options = ["Yes", "No"]
                    choice = self.get_multiple_choice_input(options)
                    # Choice is a int
                    if choice == 0:
                        # Yes
                        self.message_user(f"Please select an existing assistant")
                        assistant_list = self.list_assistants_names()
                        options = list(assistant_list.keys())
                        choice = self.get_multiple_choice_input(options)
                        # Choice is a int. Lets dynamically return the correct assistant
                        assistant_default["id"] = assistant_list[options[choice]]
                        #add the complete new info to the new list
                        new_list.append(assistant_default)
                        
                    else:
                        # No
                        self.message_user(f"Skipping {assistant_default['name']}...")
                        pass


        # add the assistant to the autogen_assistants
        self.autogen_assistants.append(new_list[0])

        return new_list
    

    
    def get_function_map(self, function_list):
        """
        Returns a dec of functions from the internal system
        """
        function_mapy = {}
        for tool in function_list:
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

        return function_mapy