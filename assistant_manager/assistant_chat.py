import inspect
import time
from assistant_manager.runs_manager import Run_Manager
from assistant_manager.assistant_tools import Tooling

import logging
import json

#
# This module contains the functions for chatting with an assistant.
#


class AssistantChat(Run_Manager, Tooling):
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


       
    def re_tool(self, autogen=False):
        self.message_user("Enabling tools")
        #Grab the tools from the assistant function metadata
        tools = self.load_tool_metadata()
        choices = self.get_multiple_choice_multiple_input(tools)
        print(choices)
        #Collect the information about the selection. int has been returned which we need to use to grab the correct dict item
        tools_list = []
        correct_info = [{
            "type": "function",
            "function": {}
        }]
        tool_metadata = None
        #metadata = {}
        #tools is a dict and choices is a int, we need to grab the correct item via the int
        #grab the item from the dict in a way that uses the int. We need to convert the dict to a list first
        for choice in choices:
            #grab the correct info from the list
            tool_name = choice["tool_name"]
            tool_required = choice["tool_required"]
            tool_description = choice["tool_description"]
            tool_properties = choice["tool_properties"]
            if autogen:
                tool_meta_description = choice["tool_meta_description"]
                tool_metadata = self.make_autogen_tool_metadata(tool_name=tool_name, tool_required=tool_required, tool_description=tool_description, tool_properties=tool_properties, tool_meta_description=tool_meta_description)
            else:
                tool_metadata = self.make_tool_metadata(tool_name=tool_name, tool_required=tool_required, tool_description=tool_description, tool_properties=tool_properties)
            # add the tool to the metadata dict

            if tool_metadata is not None:
                correct_info = {
                "type": "function",
                "function": tool_metadata
                }
                #add the tool to the tools list
                tools_list.append(correct_info)
            else:
                self.message_user("Tool not added, there was an error with the metadata")
            
        #Check if the user wants to enable the tools
        self.message_user("Are you sure you want to enable these tools? (Y/N)")
        choice = self.get_multiple_choice_input(["Y", "N"])

        if choice == "Y":
            #enable the tools
            if autogen == False:
                assistant_new = self.enable_tools(self.assistant_id, tools_list)
                self.assistant_id = assistant_new.id
            return True, tools_list

        else:
            self.message_user("Tools not enabled")
            return False, assistant_new.id
        
        

    def main_run(self, assistant_id,thread_id):
        while True:
            check_updates = self.check_update_assistant()
            #
            if check_updates is not None:
                #display the updates
                for function_name, function_output in check_updates.items():
                    #Lets debug it incase somthing goes wrong
                    self.logger.debug(f"Function Dynamically updated: {function_name} | Output: {function_output}")
                    

            # Get the input from the user
            # Remind the users of their chat controls
            self.message_user("""------------
            Your chat controls are as follows:
            To quit the chat enter 'Q'/'q' | To start a new thread enter 'swapT' | To swap assistants enter 'swapA'
            Please enter your message or a chat control.
            ------------
            """)
            message = self.get_user_input()
            #Check the users response for logic commands
            # Q for quit, new for new thread. takes one arg "thread Name" and saved the ID to the assistant object appropriately
            # swapA is for swapping the assistant, it initiates the agent selection process again

            if message == "Q" or message == "q":
                break
            elif message == "tool":
                self.re_tool()
                continue
            elif message == "swapT":
                thread_swapped = self.user_chat_swap_Thread()

                if thread_swapped is not None:
                    thread_id = thread_swapped
                    self.current_thread = thread_id
                continue

            elif message == "swapA":
                self.setup_assistant_chat()
                continue

            ThreadMessage = self.create_message(thread_id=thread_id, role="user", content=message)
            user_message_id = ThreadMessage.id
            self.chat_ids.append(user_message_id)
            self.perform_run(thread_id)

            
    

    
    def user_chat_swap_Thread(self):
        #Ask the user for the thread name or ID
        options = ["Name", "ID", "Multiple Choice (Save Locally)"]
        selected = self.get_multiple_choice_input(options)
        # If the user selected name, ask for the name
        if selected == "Name":
            self.message_user("Please enter the name of the thread")
            thread_name = self.get_user_input()

            thread_id = self.setup_thread(input_thread_name=thread_name)
            return thread_id
        # If the user selected ID, ask for the ID
        elif selected == "ID":
            self.message_user("Please enter the ID of the thread")
            thread_id = self.get_user_input()
            thread_id = self.setup_thread(input_thread_id=thread_id)
            return thread_id
        # If the user selected Multiple Choice, Provide a list of threads and ask the user to select one
        elif selected == "Multiple Choice (Save Locally)":
            #load the threads in teh json file
            with open('assistant_manager/thread_ids.json') as json_file:
                data = json.load(json_file)
                local_threads = []
                for thread_name, thread_id in data.items():
                    local_threads.append(thread_name)

                selected = self.get_multiple_choice_input(local_threads)
                thread_id = data.get(selected)
                if thread_id is None:
                    self.message_user(f"No thread found with name {selected}")
                    return

                thread_id = self.setup_thread(input_thread_id=thread_id)

                #check for messages in the thread
                history = self.list_thread_history()
                #message_user(f"History: {history}")
                if history is not None:
                    for message in reversed(history):
                        self.message_user("------------")
                        data = self.retrieve_message(thread_id=thread_id, message_id=message)
                        #data.content[0].text.value
                        self.message_user(f"{data.role}: {data.content[0].text.value}")
                return thread_id
            
    def setup_assistant_chat(self):
        """
        Takes assistant API object and returns the ID of the selected assistant Uses chat to facillitate selection process.

        Args:
            the_assistant (OAI_Assistant): An instance of the OAI_Assistant class.

        Returns:
            str: The ID of the selected assistant.
        """
        # Lets start by getting the list of assistants
        assistants = self.assistants
        # Print list in a readable format it is a SyncCursorPage
        #message_user('List of assistants:')
        #message_user(f"{assistants}")
        local_assistants = []
        for i, assistant in enumerate(assistants.data):
            local_assistants.append(assistant.name)

        # Lets ask the user to select an assistant
        selected = self.get_multiple_choice_input(local_assistants)

        self.message_user(f"You selected {selected}")
        self.message_user("Lets begin the chat")

        # Lets grab the assistant ID
        assistant_id = assistants.data[local_assistants.index(selected)].id
        self.assistant_id = assistant_id
        self.message_user(f"Assistant ID: {assistant_id}")

        return True