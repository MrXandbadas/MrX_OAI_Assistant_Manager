from assistant_manager import OAI_Assistant
import json

#import env variables
import os

org_id = os.environ.get('ORG_ID')
api_key = os.environ.get('API_KEY')



#### Main Program ####
# Lets connect to openAI assistant Endpoints
assistant = OAI_Assistant(api_key=api_key, organization=org_id)

# Interact with the user to select an assistant
assistant_id = assistant.setup_assistant_chat()

# Interact with the user to select a thread
thread_id = assistant.swap_Thread()



#check for messages in the thread
history = assistant.list_thread_history()
#message_user(f"History: {history}")
if history is not None:
    for message in reversed(history):
        assistant.message_user("------------")
        data = assistant.retrieve_message(thread_id=thread_id, message_id=message)
        #data.content[0].text.value
        assistant.message_user(f"{data.role}: {data.content[0].text.value}")


#start the chat
assistant.message_user("------------")
assistant.message_user("Your Chat has begun")

assistant.main_run(assistant_id,thread_id)
