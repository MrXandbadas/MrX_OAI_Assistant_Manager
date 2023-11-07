import asyncio
import json
import os
from openai._client import AsyncOpenAI


api_key = 'YOUR_API_KEY'
organization_id = 'YOUR_ORG_ID'
client = AsyncOpenAI(api_key="YOUR_API_KEY", organization="ORGANISATION ID")

json_file = 'thread_data.json'

def read_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

def write_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)

async def get_or_create_thread():
    data = read_json(json_file)
    thread_id = data.get('thread_id')

    if not thread_id:
        thread = await client.beta.threads.create()
        thread_id = thread.id

    return thread_id

async def list_assistants():
    response = await client.beta.assistants.list()
    return {assistant.name: assistant.id for assistant in response.data}

async def find_or_create_assistant(name, instructions, tools, model):
    assistants = await list_assistants()
    if name in assistants:
        return assistants[name]
    else:
        assistant = await client.beta.assistants.create(
            instructions=instructions,
            name=name,
            tools=tools,
            model=model
        )
        return assistant.id

async def update_assistant(assistant_id, name=None, description=None, instructions=None, tools=None):
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

async def send_message(thread_id, content, role="user"):
    return await client.beta.threads.messages.create(
        thread_id=thread_id,
        role=role,
        content=content
    )

async def get_latest_response(thread_id):
    response = await client.beta.threads.messages.list(thread_id=thread_id)
    for message in reversed(response.data):
        if message.role == "assistant":
            return message.content[0]['text']['value']
    return None

async def wait_for_assistant(thread_id, assistant_id):
    while True:
        runs = await client.beta.threads.runs.list(thread_id)
        latest_run = runs.data[0]
        if latest_run.status in ["completed", "failed"]:
            break
        await asyncio.sleep(1)

def append_to_chat_history(thread_id, user_input):
    data = read_json(json_file)
    if 'thread_id' not in data:
        data['thread_id'] = thread_id
        write_json(json_file, data)

async def display_chat_history(thread_id):
    response = await client.beta.threads.messages.list(thread_id=thread_id)
    for message in response.data:
        role = "You" if message.role == "user" else "Assistant"
        print(f"{role}: {message.content[0]['text']['value']}")

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

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break

            # Append the first user message to chat history
            append_to_chat_history(thread_id, user_input)

            await send_message(thread_id, user_input)
            await client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

            await wait_for_assistant(thread_id, assistant_id)
            response = await get_latest_response(thread_id)
            if response:
                print("Assistant:", response)

    finally:
        print("Chat session ended.")

if __name__ == "__main__":
    asyncio.run(handle_customer_inquiries())
