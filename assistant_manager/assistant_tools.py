from assistant_manager.a_m_threads import OAI_Threads
from assistant_manager.utils.file_operations import save_json, read_json
import json
import logging

class Tooling(OAI_Threads):
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

    def get_tool_by_name(self, tool_name):
        """
        Returns a tool object by name
        """
        tools = self.load_tool_metadata()
        self.logger.info(f"Getting tool by name: {tool_name}")
        for tool in tools:
            if tool["tool_name"] == tool_name:
                self.logger.debug(f"Tool found: {tool}")
                return tool
        
        self.logger.error(f"Tool not found: {tool_name}")
        return None

    def list_assistants_names(self):
        """
        Returns a dictionary of assistant names and their corresponding IDs
        """
        assistants = self.assistants
        assistant_dict = {}
        for i, assistant in enumerate(assistants.data):
            assistant_dict[assistant.name] = assistant.id
        self.logger.debug(f"Listing Assistant names: {assistant_dict}")
        return assistant_dict
    
    def list_system_tools(self):
        """
        returns a list of the tool names
        """
        tools = self.load_tool_metadata()
        tool_names = []

        #tools is a dict of named dicts, we need to grab the name from each dict
        #"list_system_tools": {
        #    "tool_name": "list_system_tools",
        #    "tool_required": "",
        #    "tool_description": "Provides a list of all available system tool names",
        #    "tool_properties": {},
        #    "tool_meta_description": "Returns a list of all available tool names."
        #}

        for tool in tools:
            tool_names.append(tool.get("tool_name"))
        
        self.logger.debug(f"Listing System Tool names: {tool_names}")

        return tool_names

    def load_tool_metadata(self) -> dict:
        """
        Loads the metadata from functions_metadata.json file

        Args:
            None

        Returns:
            dict: A dict of tool metadata.
        """
        #attempt to read the functions_metadata.json file
        tool_metadata_dict0 = read_json('assistant_manager/functions/static/default_functions_metadata.json')
        #print(tool_metadata_dict0)
        #print("------")
        tool_metadata_dict1 = read_json('assistant_manager/functions/dynamic/functions_metadata.json')
        #print(tool_metadata_dict1)
        # Merge the two dicts into a new dict
        tool_metadata = {**tool_metadata_dict0, **tool_metadata_dict1}
        


        #if the file is empty, return an empty dict
        if tool_metadata is None:
            self.logger.error("No tool metadata found assistant_tools.py")
            return {}
        else:
            #if the file is not empty, return the dict
            self.tool_metadata = tool_metadata
            self.logger.info("Tool metadata loaded")
            self.logger.debug(f"Tool metadata: {tool_metadata}")
            return self.tool_metadata

    def save_tool_metadata(self, tool_name, tool_required, tool_description, tool_schema):
        """
         Save the metadata into functions_metadata.json file

            Args:
                tool_name (str): The name of the tool.
                tool_required (list): The list of required parameters for the tool.
                tool_description (str): The description of the tool.
                tool_schema (dict): The schema of the tool.

            Returns:
                None
        """
        # Read the existing data from the file
        data = read_json('assistant_manager/functions/dynamic/functions_metadata.json')

        # Add the new entry to the data
        data[tool_name] = {
            "required": tool_required,
            "description": tool_description,
            "schema": tool_schema
        }

        # Write the updated data back to the file
        save_json('assistant_manager/functions/dynamic/functions_metadata.json', data)
        self.logger.info(f"Metadata for tool {tool_name} saved")
        self.logger.debug(f"Metadata for tool {tool_name}: {data}")
        #save to self
        self.tool_metadata = data

    def make_tool_metadata(self, tool_name, tool_required, tool_description, tool_properties):
        """
        Registers metadata for a tool.

        Args:
            tool_name (str): The name of the tool.
            tool_required (str): The ID of the tool.
            tool_description (str): The description of the tool.
            tool_schema (dict): The schema of the tool.

        Returns:
            None
        """
        # Define the metadata for the tool
        metadata = {
                "name": tool_name,
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_properties,
                    "required": [tool_required]
                }
        }
        self.logger.info(f"Metadata for tool {tool_name} created")
        self.logger.debug(f"Metadata for tool {tool_name}: {metadata}")
        # Return the metadata
        return metadata


        
    # Lets enable tool use for the assistant
    def enable_tools(self, assistant_id, tools_list):
        """
        Enables tools for the current assistant.

        Args:
            tools_list (list): A list of tools to enable.

        Returns:
            Assistant id or None
        """
        #enable the tools
        self.logger.info(f"Enabling tools for assistant {assistant_id}")
        self.logger.debug(f"Tools to enable: {tools_list}")
        assistant = self.modify_assistant(assistant_id=assistant_id, tools=tools_list, )
        #save the assistant to the current assistant
        self.current_assistant = assistant
        self.assistant_id = assistant.id
        #return the assistant
        return assistant
    

    def get_tool_list_by_names(self, tool_names):
        """
        Returns a list of tools from the tool names
        """
        tools = []
        tools_list = []
        for tool_name in tool_names:
            tool = self.get_tool_by_name(tool_name)
            tools.append(tool)

        for selected_tool in tools:
            #grab the correct info from the list
            tool_name = selected_tool["tool_name"]
            tool_required = selected_tool["tool_required"]
            tool_description = selected_tool["tool_description"]
            tool_properties = selected_tool["tool_properties"]
            tool_meta_description = selected_tool["tool_meta_description"]
            tool_metadata = self.make_autogen_tool_metadata(tool_name=tool_name, tool_required=tool_required, tool_description=tool_description, tool_properties=tool_properties, tool_meta_description=tool_meta_description)

            if tool_metadata is not None:
                correct_info = {
                "type": "function",
                "function": tool_metadata
                }
                #add the tool to the tools list
                tools_list.append(correct_info)

        
        return tools_list