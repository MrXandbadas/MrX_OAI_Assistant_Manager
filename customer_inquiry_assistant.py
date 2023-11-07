import asyncio
import json
import os
from openai._client import AsyncOpenAI
import gpt3_tokenizer

api_key = 'YOUR_API_KEY'
organization_id = 'YOUR_ORG_ID'
client = AsyncOpenAI(api_key=api_key, organization=organization_id)

json_file = 'thread_data.json'

async def list_messages(thread_id, limit=20, order='desc', after=None, before=None):
    """
    Lists messages from a specific thread.

    Args:
        thread_id (str): The ID of the thread to list messages from.
        limit (int, optional): Number of messages to return. Defaults to 20.
        order (str, optional): Order of messages ('asc' or 'desc'). Defaults to 'desc'.
        after (str, optional): Cursor for pagination to fetch messages after a certain ID.
        before (str, optional): Cursor for pagination to fetch messages before a certain ID.

    Returns:
        list: A list of message objects.
    """
    return await client.beta.threads.messages.list(thread_id=thread_id, limit=limit, order=order, after=after, before=before)

async def retrieve_message(thread_id, message_id):
    """
    Retrieves a specific message from a thread.

    Args:
        thread_id (str): The ID of the thread containing the message.
        message_id (str): The ID of the message to retrieve.

    Returns:
        dict: The message object.
    """
    return await client.beta.threads.messages.retrieve(thread_id=thread_id, message_id=message_id)



async def create_thread(messages=None, metadata=None):
    """
    Creates a new thread with optional starting messages and metadata.
    
    Args:
        messages (list, optional): A list of messages to start the thread with.
        metadata (dict, optional): Metadata associated with the thread.

    Returns:
        dict: The created thread object.
    """
    return await client.beta.threads.create(messages=messages, metadata=metadata)

async def retrieve_thread(thread_id):
    """
    Retrieves details of a specific thread by its ID.
    
    Args:
        thread_id (str): The ID of the thread to retrieve.

    Returns:
        dict: The thread object.
    """
    return await client.beta.threads.retrieve(thread_id)

async def modify_thread(thread_id, metadata):
    """
    Modifies a thread's metadata.
    
    Args:
        thread_id (str): The ID of the thread to modify.
        metadata (dict): The new metadata for the thread.

    Returns:
        dict: The modified thread object.
    """
    return await client.beta.threads.modify(thread_id, metadata=metadata)

async def delete_thread(thread_id):
    """
    Deletes a thread by its ID.
    
    Args:
        thread_id (str): The ID of the thread to delete.

    Returns:
        dict: The deletion status.
    """
    return await client.beta.threads.delete(thread_id)

async def delete_assistant(assistant_id):
    """
    Deletes an assistant by its ID.
    
    Args:
        assistant_id (str): The ID of the assistant to delete.
        
    Returns:
        The response from the API after deleting the assistant.
    """
    return await client.beta.assistants.delete(assistant_id)


async def retrieve_assistant(assistant_id):
    """
    Retrieves details of a specific assistant by its ID.
    
    Args:
        assistant_id (str): The ID of the assistant to retrieve.
        
    Returns:
        The details of the specified assistant.
    """
    return await client.beta.assistants.retrieve(assistant_id)


async def create_assistant_file(assistant_id, file_id):
    """
    Attaches a file to an assistant.
    
    Args:
        assistant_id (str): The ID of the assistant.
        file_id (str): The ID of the file to attach.

    Returns:
        The response from the API after attaching the file.
    """
    return await client.beta.assistants.files.create(assistant_id=assistant_id, file_id=file_id)

async def delete_assistant_file(assistant_id, file_id):
    """
    Deletes a file attached to an assistant.
    
    Args:
        assistant_id (str): The ID of the assistant.
        file_id (str): The ID of the file to delete.

    Returns:
        The response from the API after deleting the file.
    """
    return await client.beta.assistants.files.delete(assistant_id, file_id)


async def list_assistant_files(assistant_id):
    """
    Lists all files attached to an assistant.
    
    Args:
        assistant_id (str): The ID of the assistant.

    Returns:
        A list of files attached to the specified assistant.
    """
    return await client.beta.assistants.files.list(assistant_id)


async def create_run(thread_id, assistant_id, model=None, instructions=None, tools=None):
    """
    Creates a run for a thread with a specified assistant.
    
    Args:
        thread_id (str): The ID of the thread.
        assistant_id (str): The ID of the assistant.
        model (str, optional): Model ID to be used.
        instructions (str, optional): Instructions for the assistant.
        tools (list, optional): Tools available for the assistant.

    Returns:
        The run object created.
    """
    return await client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id, model=model, instructions=instructions, tools=tools)

async def retrieve_run(thread_id, run_id):
    """
    Retrieves a specific run for a given thread.
    
    Args:
        thread_id (str): The ID of the thread.
        run_id (str): The ID of the run to retrieve.

    Returns:
        The specified run object.
    """
    return await client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

async def cancel_run(thread_id, run_id):
    """
    Cancels an in-progress run.
    
    Args:
        thread_id (str): The ID of the thread.
        run_id (str): The ID of the run to cancel.

    Returns:
        The run object after cancellation.
    """
    return await client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)

async def list_runs(thread_id):
    """
    Lists all runs for a given thread.
    
    Args:
        thread_id (str): The ID of the thread.

    Returns:
        A list of run objects for the specified thread.
    """
    return await client.beta.threads.runs.list(thread_id=thread_id)


async def list_run_steps(thread_id, run_id):
    """
    Lists all steps for a specific run in a thread.
    
    Args:
        thread_id (str): The ID of the thread.
        run_id (str): The ID of the run.

    Returns:
        A list of run step objects for the specified run.
    """
    return await client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run_id)

async def retrieve_run_step(thread_id, run_id, step_id):
    """
    Retrieves a specific run step.
    
    Args:
        thread_id (str): The ID of the thread.
        run_id (str): The ID of the run.
        step_id (str): The ID of the run step to retrieve.

    Returns:
        The specified run step object.
    """
    return await client.beta.threads.runs.steps.retrieve(thread_id=thread_id, run_id=run_id, step_id=step_id)


async def submit_tool_outputs(thread_id, run_id, tool_outputs):
    """
    Submits the outputs from tool calls for a run that requires action.
    
    Args:
        thread_id (str): The ID of the thread.
        run_id (str): The ID of the run.
        tool_outputs (list): Outputs from the tool calls.

    Returns:
        The modified run object after submitting the tool outputs.
    """
    return await client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)


def read_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

def write_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)

async def get_or_create_thread():
    """
    Get or create a thread of Messages/content.

    This function reads a JSON file to get the ID of an existing thread. If the thread ID is not found, a new thread is created
    using the `client.beta.threads.create()` method. The ID of the new thread is then returned.

    :return: The ID of the thread.
    :rtype: str
    """
    data = read_json(json_file)
    thread_id = data.get('thread_id')

    if not thread_id:
        thread = await client.beta.threads.create()
        thread_id = thread.id
        # Save the thread ID to the JSON file
        data['thread_id'] = thread_id
        write_json(json_file, data)

    return thread_id

async def list_assistants():
    response = await client.beta.assistants.list()
    return {assistant.name: assistant.id for assistant in response.data}

async def find_or_create_assistant(name, instructions, tools, model):
    """
    Finds an existing assistant by name or creates a new one. 
    If the assistant exists but with different arguments, it updates the assistant.

    Args:
        name (str): The name of the assistant.
        instructions (str): Instructions for the assistant.
        tools (list): List of tools for the assistant.
        model (str): Model ID for the assistant.
    
    Returns:
        str: The ID of the found or created assistant.
    """

    assistants = await list_assistants()
    if name in assistants:
        assistant_id = assistants[name]
        existing_assistant = await retrieve_assistant(assistant_id)
        
        # Check if existing assistant's configuration matches the new arguments
        if existing_assistant.instructions != instructions or existing_assistant.tools != tools or existing_assistant.model != model:
            # Update the assistant with new arguments
            await update_assistant(assistant_id, name=name, description=existing_assistant.description, instructions=instructions, tools=tools)
        
        return assistant_id
    else:
        # Create a new assistant if not found
        assistant = await client.beta.assistants.create(
            instructions=instructions,
            name=name,
            tools=tools,
            model=model
        )
        return assistant.id


async def update_assistant(assistant_id, name=None, description=None, instructions=None, tools=None):
    """
    Update an existing assistant with the given ID.

    :param assistant_id: The ID of the assistant to update.
    :type assistant_id: str
    :param name: The new name of the assistant (optional).
    :type name: str
    :param description: The new description of the assistant (optional).
    :type description: str
    :param instructions: The new instructions for using the assistant (optional).
    :type instructions: str
    :param tools: The new tools used by the assistant (optional).
    :type tools: list[str]
    :return: The updated assistant object.
    :rtype: dict
    """
    update_fields = {}
    if name is not None:
        update_fields['name'] = name
    if description is not None:
        update_fields['description'] = description
    if instructions is not None:
        update_fields['instructions'] = instructions
    if tools is not None:
        update_fields['tools'] = tools

    return await client.beta.assistants.update(assistant_id, **update_fields)

def count_tokens(text):
    """
    Counts the number of tokens in a given text string using gpt3_tokenizer.

    Args:
        text (str): The text to be tokenized.

    Returns:
        int: The number of tokens in the text.
    """
    return gpt3_tokenizer.count_tokens(text)


async def send_message(thread_id, content, role="user"):
    """
    Sends a message in a thread and counts the tokens used.

    Args:
        thread_id (str): The thread ID to send the message to.
        content (str): The content of the message.
        role (str): The role of the sender ('user' or 'assistant').

    Returns:
        dict: The response from the message creation API call.
    """
    # Count the tokens in the user's message
    token_count = count_tokens(content)
    print(f"Tokens used in message: {token_count}")
    return await client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content)


async def wait_for_assistant(thread_id, assistant_id):
    """
    Wait for the assistant to complete or fail a run in a given thread.

    Args:
        thread_id (str): The ID of the thread to check for runs.
        assistant_id (str): The ID of the assistant to wait for.

    Returns:
        None
    """
    while True:
        runs = await client.beta.threads.runs.list(thread_id)
        latest_run = runs.data[0]
        if latest_run.status in ["completed", "failed"]:
            break
        await asyncio.sleep(2) # Wait for 2 seconds before checking again

def append_to_chat_history(thread_id, user_input):
    """
    Appends the user input to the chat history for the given thread ID.

    Args:
        thread_id (str): The ID of the thread to append the chat history to.
        user_input (str): The user's input to add to the chat history.

    Returns:
        None
    """
    data = read_json(json_file)
    if 'thread_id' not in data:
        data['thread_id'] = thread_id
        write_json(json_file, data)

async def display_chat_history(thread_id):
    """
    Retrieves and displays the chat history for a given thread ID.

    Args:
        thread_id (str): The ID of the thread to retrieve chat history for.

    Returns:
        None
    """
    response = await client.beta.threads.messages.list(thread_id=thread_id)
    for message in reversed(response.data):
        role = message.role
        message_text = message.content[0].text.value
        #Fix this silly mistake
        print(f"{role}: {message_text}")

        
# Function to get the latest response and handle the run
async def get_latest_response(thread_id, assistant_id, user_input):
    # Send the user message
    await send_message(thread_id, user_input)

    # Create a new run for the assistant to respond
    await client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    # Wait for the assistant's response
    await wait_for_assistant(thread_id, assistant_id)

    # Retrieve the latest response
    response = await client.beta.threads.messages.list(thread_id=thread_id)
    for message in response.data:
        if message.role == "assistant":
            return message.content[0].text.value, count_tokens(message.content[0].text.value)
    return None, 0

# Function to handle customer inquiries
async def handle_customer_inquiries():
    assistant_id = await find_or_create_assistant(
        name="Customer Service Assistant",
        instructions="You are a customer service assistant. Answer user queries courteously and accurately.",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview"
    )

    await update_assistant(assistant_id, description="Handles customer service inquiries efficiently.")
    thread_id = await get_or_create_thread()

    # Display existing chat history
    await display_chat_history(thread_id)

    prev_messages = await list_messages(thread_id)
    if prev_messages.data != []:
            # Process each message here
        print("Message Found")
            

    else:
        print("No messages found in the thread.")


    # get the thread and count all the message tokens
    total_tokens_used = 0

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break

            # Count and track tokens of user input
            tokens_used = count_tokens(user_input)
            total_tokens_used += tokens_used
            print(f"Tokens used in message: {tokens_used}")
            print(f"Total tokens used so far: {total_tokens_used}")

            # Get assistant's response and count tokens
            response, tokens_used = await get_latest_response(thread_id, assistant_id, user_input)
            total_tokens_used += tokens_used
            print(f"Tokens used in response: {tokens_used}")
            print(f"Total tokens used so far: {total_tokens_used}")

            if response:
                print("Assistant:", response)

    finally:
        print(f"Session ended. Total tokens used: {total_tokens_used}")



if __name__ == "__main__":
    asyncio.run(handle_customer_inquiries())
