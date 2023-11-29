
#import inspect
#import time
import logging
#import json
#from assistant_manager.oai_base import OAI_Base
from assistant_manager.assistant_chat import AssistantChat
from assistant_manager.interface_base import InterfaceBase
from assistant_manager.assistant_tools import Tooling
#import dynamic_functions

#from utils.file_operations import save_json, read_json
#from utils.special_functions import append_new_tool_function_and_metadata

class OAI_Assistant(AssistantChat,InterfaceBase):
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
        
        #Set up some defaults to keep track of the current assistant, thread and run
        self.current_assistant = None or OAI_Assistant
        self.autogen_assistants = None



    def swap_assistant(self, new_assistant_id):
        """
        Takes the assistant ID and swaps the assistant
        """
        self.change_assistant_id = new_assistant_id
        # queue the update
        self.queue_update("change_assistant")
        return new_assistant_id
    
    def change_assistant(self):
        """
        Changes the assistant ID
        """
        self.assistant_id = self.change_assistant_id
        return self.assistant_id
    

    
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

    
    ###
    # Section for running functions in relation to the assistant dynamically.... ;)

    # Que the assistant to update
    
    def queue_update(self, function_call, **kwargs):
        """
        Queues the assistant to update

        Args:
            function_call: The function to call holding information about the update required to the oai class
            kwargs: The arguments to pass to the function
        """
        self.update_queue.append((function_call, kwargs))

        return True
    
    def get_update_queue(self):
        """
        Returns the update queue

        Returns:
            list: The update queue
        """
        return self.update_queue
    

    def check_update_assistant(self):
        """
        Checks the update queue and runs the functions in the queue
        """
        output_results = {}
        # Check if the update queue is empty
        if len(self.update_queue) == 0:
            return None
            
        
        # Run the functions in the queue
        for function_name, kwargs in self.update_queue:
            function = getattr(self, function_name)
            function_output = function(**(kwargs))
            output_results[function_name] = function_output
            self.logger.debug(f"Function: {function_name} | Output: {function_output}")
        
        # Empty the queue
        self.update_queue = []
        if output_results is not None or {}:
            return output_results

    ###
