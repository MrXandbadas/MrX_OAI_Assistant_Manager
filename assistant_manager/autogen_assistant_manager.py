from assistant_tools import Tooling
from assistant_manager.interface_base import InterfaceBase
import logging

class AutogenAssistantManager(Tooling, InterfaceBase):

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

    
    
    def list_autogen_assistants(self):
        """
        Returns a list of autogen Assistants
        """
        return self.autogen_assistants
    


    def make_autogen_tool_metadata(self, tool_name, tool_required, tool_description, tool_properties, tool_meta_description):
        """
        Registers metadata for a tool.

        Args:
            tool_name (str): The name of the tool.
            tool_required (str): The ID of the tool.
            tool_description (str): The description of the tool.
            tool_schema (dict): The schema of the tool.
            tool_meta_description (str): The meta description of the tool.

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
                },
                "description": tool_meta_description
        }
        # Return the metadata
        return metadata

    