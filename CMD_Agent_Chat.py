from assistant_manager import OAI_Assistant
import time
import json
import dynamic_functions
from utils.file_operations import read_file, write_to_file, exec_python, exec_sh
from utils.special_functions import get_stock_price



#import env variables
import os

org_id = os.environ.get('ORG_ID')
api_key = os.environ.get('API_KEY')


#### General Helper Functions ####

def message_user(message):
    print(message)

def get_input():
    message_user("------------")
    return input('>>> ')

def get_multiple_choice_input(options):
    print('Please input Numbers only to select one of the following options or enter Q to leave:')
    for i, option in enumerate(options):
        print(f'{i+1}. {option}')
    while True:
        try:
            choice = input('>>> ')
            if choice == "Q" or choice == "q" or choice == "Quit" or choice == "quit" or choice == "exit":
                return None
            choice = int(choice)
            if choice > len(options) or choice < 1:
                raise ValueError
            return options[choice-1]
        except ValueError:
            print('Please enter a valid option')

def get_multiple_choice_multiple_input(options:dict):
    print('Please input Numbers only to select any of the following options or enter Q to leave:')
    for i, option in enumerate(options):
        print(f'{i+1}. {option}')
    while True:
        try:
            choice = input('>>> ')
            if choice.lower() in ["q", "quit", "exit"]:
                return None
            if "," in choice:
                choices = [int(i) - 1 for i in choice.split(",")]
                if any(choice >= len(options) or choice < 0 for choice in choices):
                    raise ValueError
                return [options[list(options.keys())[choice]] for choice in choices]
            else:
                choice = int(choice) - 1
                if choice >= len(options) or choice < 0:
                    raise ValueError
                return [options[list(options.keys())[choice]]] # Modified line
        except ValueError:
            print('Please enter a valid option')



#### End of General Helper Functions ####


#### chat working functions ####

def setup_assistant_chat(the_assistant: OAI_Assistant):
    """
    Takes assistant API object and returns the ID of the selected assistant Uses chat to facillitate selection process.

    Args:
        the_assistant (OAI_Assistant): An instance of the OAI_Assistant class.

    Returns:
        str: The ID of the selected assistant.
    """
    # Lets start by getting the list of assistants
    assistants = the_assistant.assistants
    # Print list in a readable format it is a SyncCursorPage
    message_user('List of assistants:')
    message_user(f"{assistants}")
    local_assistants = []
    for i, assistant in enumerate(assistants.data):
        local_assistants.append(assistant.name)

    # Lets ask the user to select an assistant
    selected = get_multiple_choice_input(local_assistants)

    message_user(f"You selected {selected}")
    message_user("Lets begin the chat")

    # Lets get the assistant object
    the_assistant = next((assistant for assistant in assistants.data if assistant.name == selected), None)
    if assistant is None:
        message_user(f"No assistant found with name {selected}")
        return
    
    assistant_id = assistant.id
    the_assistant.assistant_id = assistant_id
    message_user(f"Assistant ID: {assistant_id}")

    return assistant_id

def setup_thread(the_assistant: OAI_Assistant, input_thread_name=None, input_thread_id=None) -> int:
    # Create a new thread if thread_id is None
    
    if input_thread_name is not None:
        thread_id = the_assistant.change_thread(input_thread_name)
    elif input_thread_id is not None:
        #change the thread to the thread with the given ID
        thread_id = the_assistant.change_thread(thread_id=input_thread_id)
    else:
        #create a thread with the deafult name
        thread_id = the_assistant.change_thread(thread_name="Default_Thread")


    the_assistant.current_thread = thread_id
    the_assistant.prepare_thread_history(thread_id=thread_id)
    return thread_id


def swap_Thread(assistant: OAI_Assistant):
    #Ask the user for the thread name or ID
    options = ["Name", "ID", "Multiple Choice (Save Locally)"]
    selected = get_multiple_choice_input(options)
    # If the user selected name, ask for the name
    if selected == "Name":
        message_user("Please enter the name of the thread")
        thread_name = get_input()
        thread_id = setup_thread(assistant, input_thread_name=thread_name)
        return thread_id
    # If the user selected ID, ask for the ID
    elif selected == "ID":
        message_user("Please enter the ID of the thread")
        thread_id = get_input()
        thread_id = setup_thread(assistant, input_thread_id=thread_id)
        return thread_id
    # If the user selected Multiple Choice, Provide a list of threads and ask the user to select one
    elif selected == "Multiple Choice (Save Locally)":
        #load the threads in teh json file
        with open('thread_ids.json') as json_file:
            data = json.load(json_file)
            local_threads = []
            for thread_name, thread_id in data.items():
                local_threads.append(thread_name)

            selected = get_multiple_choice_input(local_threads)
            thread_id = data.get(selected)
            if thread_id is None:
                message_user(f"No thread found with name {selected}")
                return

            thread_id = setup_thread(assistant, input_thread_id=thread_id)

            #check for messages in the thread
            history = assistant.list_thread_history()
            #message_user(f"History: {history}")
            if history is not None:
                for message in reversed(history):
                    message_user("------------")
                    data = assistant.retrieve_message(thread_id=thread_id, message_id=message)
                    #data.content[0].text.value
                    message_user(f"{data.role}: {data.content[0].text.value}")
            return thread_id

#### End of chat working functions ####




def main_run(assistant: OAI_Assistant, assistant_id,thread_id):

    

    while True:
        # Get the input from the user
        # Remind the users of their chat controls

        message_user("------------")
        message_user("Your chat controls are as follows:")
        message_user("To quit the chat enter 'Q'/'q' | To start a new thread enter 'swapT' | To swap assistants enter 'swapA'")
        message_user("Please enter your message or a chat control.")
        message = get_input()
        #Check the users response for logic commands
        # Q for quit, new for new thread. takes one arg "thread Name" and saved the ID to the assistant object appropriately
        # swapA is for swapping the assistant, it initiates the agent selection process again

        if message == "Q" or message == "q":
            break
        elif message == "tool":
            message_user("Enabling tools")
            #Grab the tools from the assistant function metadata
            tools = assistant.load_tool_metadata()
            choices = get_multiple_choice_multiple_input(tools)
            print(choices)
            #Collect the information about the selection. int has been returned which we need to use to grab the correct dict item
            tools_list = []
            correct_info = [{
                "type": "function",
                "function": {}
            }]
            
            #metadata = {}
            #tools is a dict and choices is a int, we need to grab the correct item via the int
            #grab the item from the dict in a way that uses the int. We need to convert the dict to a list first
            for choice in choices:
                #grab the correct info from the list
                tool_name = choice["tool_name"]
                tool_required = choice["tool_required"]
                tool_description = choice["tool_description"]
                tool_properties = choice["tool_properties"]
                tool_metadata = assistant.make_tool_metadata(tool_name=tool_name, tool_required=tool_required, tool_description=tool_description, tool_properties=tool_properties)
                # add the tool to the metadata dict
                correct_info = {
                "type": "function",
                "function": tool_metadata
                }
                #add the tool to the tools list
                tools_list.append(correct_info)
                
                #tools_list.append(assistant.make_tool_metadata(tool_name=choice["tool_name"], tool_required=choice["tool_required"], tool_description=choice["tool_description"], tool_properties=choice["tool_properties"]))
                

            
            
            #Check if the user wants to enable the tools
            #message_user(f"Tools Selected: {tools_list}")
            # grab the tools from the assistant
            
            message_user("Are you sure you want to enable these tools? (Y/N)")
            choice = get_multiple_choice_input(["Y", "N"])

            if choice == "Y":
                #enable the tools
                
                assistant_new = assistant.enable_tools(assistant_id, tools_list)
                assistant.assistant_id = assistant_new.id

            else:
                message_user("Tools not enabled")
            
            continue
        elif message == "swapT":
            thread_swapped = swap_Thread(assistant)

            if thread_swapped is not None:
                thread_id = thread_swapped
                assistant.current_thread = thread_id
            continue

        elif message == "swapA":
            assistant_id = setup_assistant_chat(assistant)
            continue

        ThreadMessage = assistant.create_message(thread_id=thread_id, role="user", content=message)
        user_message_id = ThreadMessage.id
        assistant.chat_ids.append(user_message_id)
        run = assistant.create_run(thread_id=thread_id, assistant_id=assistant_id)
        assistant.current_run = run.id
        while True:
            run = assistant.retrieve_run(thread_id, run.id)
            if run.status == "completed":
                message_list = assistant.list_messages(thread_id)
                for message in message_list.data:
                    if message.id in assistant.chat_ids:
                        continue
                    else:
                        message_user(f'assistant: {message.content[0].text.value}')
                        assistant.chat_ids.append(message.id)
                break
            elif run.status == "requires_action":
                message_user("The run requires action.")
                required_actions_json = run.required_action.submit_tool_outputs.model_dump_json(indent=4)
                message_user(f"Required Actions: {required_actions_json}")
                required_actions = json.loads(required_actions_json)
                tools_output = []
                for action in required_actions["tool_calls"]:
                    if action["function"]["name"] == "get_stock_price":
                        arguments = json.loads(action["function"]["arguments"])
                        stock_price = get_stock_price(arguments["symbol"])
                        tools_output.append({"tool_call_id": action["id"], "output": stock_price})
                    #else if check if its in the dynamic tool code
                    elif action["function"]["name"] == "write_to_file":
                        arguments = json.loads(action["function"]["arguments"])
                        write_to_file(arguments["file_name"], arguments["content"])
                        tools_output.append({"tool_call_id": action["id"], "output": "Success"})
                    elif action["function"]["name"] == "read_file":
                        arguments = json.loads(action["function"]["arguments"])
                        file_content = read_file(arguments["file_name"])
                        tools_output.append({"tool_call_id": action["id"], "output": file_content})
                    elif action["function"]["name"] == "exec_python":
                        arguments = json.loads(action["function"]["arguments"])
                        function_output = exec_python(arguments["cell"])
                        tools_output.append({"tool_call_id": action["id"], "output": function_output})
                    #elif the action is dynamic_{function} then we need to call the function
                    elif action["function"]["name"] in dir(dynamic_functions):
                        
                        arguments = json.loads(action["function"]["arguments"])
                        function_name = action["function"]["name"]
                        function = getattr(dynamic_functions, function_name)
                        function_output = function(**arguments)
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                    else:
                        message_user(f"Function {action['function']['name']} not found")
                #message_user(f"Tools Output: {tools_output}")
                assistant.submit_tool_outputs(thread_id, run.id, tools_output)

            elif run.status == "failed":
                message_user("The run failed.")
                message_user(f"Error: {json.dumps(run, indent=4)}")
                break
            else:
                time.sleep(1)
                continue




#### Main Program ####


# Lets connect to openAI assistant Endpoints
assistant = OAI_Assistant(api_key=api_key, organization=org_id)

# Interact with the user to select an assistant
assistant_id = setup_assistant_chat(assistant)

# Interact with the user to select a thread
thread_id = swap_Thread(assistant)



#check for messages in the thread
history = assistant.list_thread_history()
#message_user(f"History: {history}")
if history is not None:
    for message in reversed(history):
        message_user("------------")
        data = assistant.retrieve_message(thread_id=thread_id, message_id=message)
        #data.content[0].text.value
        message_user(f"{data.role}: {data.content[0].text.value}")


#start the chat
message_user("------------")
message_user("Your Chat has begun")
main_run(assistant, assistant_id,thread_id)
