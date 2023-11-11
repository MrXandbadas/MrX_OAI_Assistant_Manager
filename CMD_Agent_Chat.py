from assistant_manager import OAI_Assistant
import time
import os

# Untested, i usually put mine in manually even tho its bad practice.
org_id = os.environ.get('ORG_ID')
api_key = os.environ.get('API_KEY')

#End Untested


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
    assistants = the_assistant.list_assistant_cache()
    # Print list in a readable format it is a SyncCursorPage
    message_user('List of assistants:')
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
    options = ["Name", "ID"]
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

#### End of chat working functions ####

def main_run(assistant: OAI_Assistant, assistant_id,thread_id):

    while True:
        # Get the input from the user
        # Remind the users of their chat controls

        message_user("------------")
        message_user("Your chat controls are as follows:")
        message_user("To quit the chat enter 'Q'/'q' | To start a new thread enter 'new' | To swap assistants enter 'swapA'")
        message_user("Please enter your message or a chat control.")
        message = get_input()
        #Check the users response for logic commands
        # Q for quit, new for new thread. takes one arg "thread Name" and saved the ID to the assistant object appropriately
        # swapA is for swapping the assistant, it initiates the agent selection process again

        if message == "Q" or message == "q":
            break
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
            elif run.status == "failed":
                message_user("The run failed.")
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
