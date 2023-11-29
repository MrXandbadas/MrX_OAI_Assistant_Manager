import inspect
import time
from assistant_manager.a_m_threads import OAI_Threads
from assistant_manager.assistant_tools import Tooling
from assistant_manager.functions.dynamic import dynamic_functions
from assistant_manager.utils import file_operations, special_functions
from assistant_manager.utils.special_functions import append_new_tool_function_and_metadata
import logging
import json

class AssistantChat(OAI_Threads, Tooling):
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
                thread_swapped = self.swap_Thread()

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
            run = self.create_run(thread_id=thread_id, assistant_id=self.assistant_id)
            run_done = self.process_run(thread_id=thread_id, run_id=run.id)
            #Wait for the run to complete
            if run_done is not None:
                print("Run Completed")
                message_list = self.list_thread_history()
                #check for a new message in the thread
                for message in message_list:
                        message_obj = self.retrieve_message(thread_id=thread_id, message_id=message)
                        if message_obj.id is None:
                            continue
                        if message_obj.id in self.chat_ids:
                            continue
                        else:
                            message
                            self.message_user(f'assistant: {message_obj.content[0].text.value}')
                            self.chat_ids.append(message_obj.id)

            else:
                print(f"Else out? {run.status}")
    
    def process_run(self,thread_id, run_id):
        while True:
            run = self.retrieve_run(thread_id, run_id)
            print(run.status)
            if run.status == "completed":
                message_list = self.list_messages(thread_id)
                for message in message_list.data:
                    if message.id in self.chat_ids:
                        continue
                    else:
                        print(f'assistant: {message.content[0].text.value}')
                        self.chat_ids.append(message.id)
                        return message.content[0].text.value
                break
            elif run.status == "requires_action":
                print("The run requires action.")
                required_actions_json = run.required_action.submit_tool_outputs.model_dump_json(indent=4)
                print(f"Required Actions: {required_actions_json}")
                required_actions = json.loads(required_actions_json)
                tools_output = []
                for action in required_actions["tool_calls"]:
                    if action["function"]["name"] == "append_new_tool_function_and_metadata":
                        arguments = json.loads(action["function"]["arguments"])
                        # get the function name
                        function_name = arguments["function_name"]
                        # get the function code
                        function_code = arguments["function_code"]
                        # get the metadata dict
                        function_metadata = arguments["metadata_dict"]

                        function_meta_description = arguments["tool_meta_description"]
                        #Check if we need to json.loads the metadata
                        if isinstance(function_metadata, str):
                            function_metadata = json.loads(arguments["metadata_dict"])
                        #print(f"Function name: {function_name}")
                        self.logger.debug(f"Function code: {function_code}")
                        #print(f"Function metadata: {function_metadata}")
                        # append the function and metadata to the current assistant
                        function_output = append_new_tool_function_and_metadata(function_name, function_code, function_metadata, function_meta_description)
                        #function_output = append_new_tool_function_and_metadata(self, **(arguments))
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                        continue
                        
                    # Functions Dynamically registered in the utils/special_functions.py file    
                    elif action["function"]["name"] in dir(special_functions):
                        arguments = json.loads(action["function"]["arguments"])
                        function_name = action["function"]["name"]
                        function = getattr(special_functions, function_name)
                        #check if the arguments are a string and if so convert to dict
                        if isinstance(arguments, str):
                            arguments = json.loads(arguments)
                        # Does the function need self?
                        if "assistant" in inspect.getfullargspec(function).args:
                            function_output = function(self, **(arguments))
                        else:
                            function_output = function(**(arguments))
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})

                    # Functions Dynamically registered in the utils/file_operations.py file
                    elif action["function"]["name"] in dir(file_operations):
                        arguments = json.loads(action["function"]["arguments"])
                        if isinstance(arguments, str):
                            arguments = json.loads(arguments)
                        function_name = action["function"]["name"]
                        function = getattr(file_operations, function_name)
                        #check if the arguments are a string and if so convert to dict
                        function_output = function(**(arguments))
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})

                    #functions registerd on self
                    elif action["function"]["name"] in dir(self):
                        arguments = json.loads(action["function"]["arguments"])
                        function_name = action["function"]["name"]
                        function = getattr(self, function_name)
                        #check if the arguments are a string and if so convert to dict
                        print(f"ARGUMENTS {arguments}")
                        if isinstance(arguments, str):
                            arguments = json.loads(arguments)
                        function_output = function(**(arguments))
                        # give it time to process
                        time.sleep(2)
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                        
                    #functions registered in the dynamic_functions.py file
                    elif action["function"]["name"] in dir(dynamic_functions):
                        
                        arguments = json.loads(action["function"]["arguments"])
                        function_name = action["function"]["name"]
                        function = getattr(dynamic_functions, function_name)
                        #check if the arguments are a string and if so convert to dict
                        function_output = function(**(arguments))
                        # give it time to process
                        time.sleep(2)
                        
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                    else:
                        print(f"Function {action['function']['name']} not found")
                #message_user(f"Tools Output: {tools_output}")
                self.submit_tool_outputs(thread_id, run.id, tools_output)

            elif run.status == "failed":
                print("The run failed.")
                print(f"Error: {json.dumps(str(run), indent=4)}")
                return None
            else:
                time.sleep(2)
                continue


    
    def swap_Thread(self):
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