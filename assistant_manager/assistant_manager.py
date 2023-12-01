
#import inspect
#import time
import logging
from assistant_manager.assistant_chat import AssistantChat
from assistant_manager.interface_base import InterfaceBase
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





    ###
