import asyncio
from agent_class import OAI_Agent

api_key='API KEY'

organization_id='ORG'

client = OAI_Agent(api_key=api_key, organization_id=organization_id)

json_file = 'thread_data.json'

# Function to handle customer inquiries
async def handle_customer_inquiries():
    assistant_id = await client.find_or_create_assistant(
        name="Customer Service Assistant",
        instructions="You are a customer service assistant. Answer user queries courteously and accurately.",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview"
    )

    await client.update_assistant(assistant_id, description="Handles customer service inquiries efficiently.")
    thread_id = await client.get_or_create_thread()

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
