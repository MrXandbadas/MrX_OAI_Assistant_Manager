import asyncio
from agent_class_legacy import OAI_Agent


api_key="APIKEY"
organization_id="ORGID"

client = OAI_Agent(api_key=api_key, organization_id=organization_id)

json_file = 'thread_data.json'
agent_file = 'agent_data.json'

thread_name = "My_First_Chat"
Customer_Service_Assistant = {
    "name":"Customer Service Assistant",
    "instructions":"You are a customer service assistant. Answer user queries courteously and accurately.",
    "tools":[{"type": "retrieval"}],
    "model":"gpt-4-1106-preview"
}


async def create_agent(Assistant_config):
    name = Assistant_config["name"]
    instructions = Assistant_config["instructions"]
    tools = Assistant_config["tools"]
    model = Assistant_config["model"]

    assistant_id = await client.find_or_create_assistant(
        send_name=name,
        instructions=instructions,
        tools=tools,
        model=model
    )

    return assistant_id

# Function to handle customer inquiries
async def handle_customer_inquiries():
    
    assistant_id= await create_agent(Customer_Service_Assistant)

    await client.update_assistant(assistant_id, description="Handles customer service inquiries efficiently.")
    thread_id = await client.get_or_create_thread(thread_name)

    # Display existing chat history
    await client.display_chat_history(thread_id)

    prev_messages = await client.list_messages(thread_id)
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
            tokens_used = client.count_tokens(user_input)
            total_tokens_used += tokens_used
            print(f"Tokens used in message: {tokens_used}")
            print(f"Total tokens used so far: {total_tokens_used}")

            # Get assistant's response and count tokens
            response, tokens_used = await client.get_latest_response(thread_id, assistant_id, user_input)
            total_tokens_used += tokens_used
            print(f"Tokens used in response: {tokens_used}")
            print(f"Total tokens used so far: {total_tokens_used}")

            if response:
                print("Assistant:", response)

    finally:
        print(f"Session ended. Total tokens used: {total_tokens_used}")



if __name__ == "__main__":
    asyncio.run(handle_customer_inquiries())
