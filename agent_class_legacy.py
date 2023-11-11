import asyncio
import json
from openai._client import AsyncOpenAI
import gpt3_tokenizer

class OAI_Agent():
    def __init__(self, api_key, organization_id):
        self.api_key = api_key
        self.organization_id = organization_id
        self.assistant_id = None
        self.client = AsyncOpenAI(api_key=api_key, organization=organization_id)
        self.json_file = 'thread_data.json'
        self.assistant_file="assistant_data.json"
        
    async def get_json_file(self):
        return self.json_file
    
    async def get_assistant_file(self):
        return self.assistant_file
    

    async def list_messages(self, thread_id, limit=4, order='desc', after=None, before=None):
        """
        Lists messages from a specific thread.

        Args:
            thread_id (str): The ID of the thread to list messages from.
            limit (int, optional): Number of messages to return. Defaults to 4.
            order (str, optional): Order of messages ('asc' or 'desc'). Defaults to 'desc'.
            after (str, optional): Cursor for pagination to fetch messages after a certain ID.
            before (str, optional): Cursor for pagination to fetch messages before a certain ID.

        Returns:
            list: A list of message objects.
        """
        return await self.client.beta.threads.messages.list(thread_id=thread_id, limit=limit, order=order, after=after, before=before)

    async def retrieve_message(self, thread_id, message_id):
        """
        Retrieves a specific message from a thread.

        Args:
            thread_id (str): The ID of the thread containing the message.
            message_id (str): The ID of the message to retrieve.

        Returns:
            dict: The message object.
        """
        return await self.client.beta.threads.messages.retrieve(thread_id=thread_id, message_id=message_id)



    async def create_thread(self, messages=None, metadata=None):
        """
        Creates a new thread with optional starting messages and metadata.
        
        Args:
            messages (list, optional): A list of messages to start the thread with.
            metadata (dict, optional): Metadata associated with the thread.

        Returns:
            dict: The created thread object.
        """
        return await self.client.beta.threads.create(messages=messages, metadata=metadata)

    async def retrieve_thread(self, thread_id):
        """
        Retrieves details of a specific thread by its ID.
        
        Args:
            thread_id (str): The ID of the thread to retrieve.

        Returns:
            dict: The thread object.
        """
        return await self.client.beta.threads.retrieve(thread_id)
    
    async def list_threads(self):
        """
        Lists all threads.
        
        Returns:
            list: A list of thread objects.
        """
        return await self.client.beta.threads.list()

    async def modify_thread(self, thread_id, metadata):
        """
        Modifies a thread's metadata.
        
        Args:
            thread_id (str): The ID of the thread to modify.
            metadata (dict): The new metadata for the thread.

        Returns:
            dict: The modified thread object.
        """
        return await self.client.beta.threads.modify(thread_id, metadata=metadata)

    async def delete_thread(self, thread_id):
        """
        Deletes a thread by its ID.
        
        Args:
            thread_id (str): The ID of the thread to delete.

        Returns:
            dict: The deletion status.
        """
        return await self.client.beta.threads.delete(thread_id)

    async def delete_assistant(self, assistant_id):
        """
        Deletes an assistant by its ID.
        
        Args:
            assistant_id (str): The ID of the assistant to delete.
            
        Returns:
            The response from the API after deleting the assistant.
        """
        return await self.client.beta.assistants.delete(assistant_id)


    async def retrieve_assistant(self, assistant_id):
        """
        Retrieves details of a specific assistant by its ID.
        
        Args:
            assistant_id (str): The ID of the assistant to retrieve.
            
        Returns:
            The details of the specified assistant.
        """
        return await self.client.beta.assistants.retrieve(assistant_id)


    async def create_assistant_file(self, assistant_id, file_id):
        """
        Attaches a file to an assistant.
        
        Args:
            assistant_id (str): The ID of the assistant.
            file_id (str): The ID of the file to attach.

        Returns:
            The response from the API after attaching the file.
        """
        return await self.client.beta.assistants.files.create(assistant_id=assistant_id, file_id=file_id)

    async def delete_assistant_file(self, assistant_id, file_id):
        """
        Deletes a file attached to an assistant.
        
        Args:
            assistant_id (str): The ID of the assistant.
            file_id (str): The ID of the file to delete.

        Returns:
            The response from the API after deleting the file.
        """
        return await self.client.beta.assistants.files.delete(assistant_id, file_id)


    async def list_assistant_files(self, assistant_id):
        """
        Lists all files attached to an assistant.
        
        Args:
            assistant_id (str): The ID of the assistant.

        Returns:
            A list of files attached to the specified assistant.
        """
        return await self.client.beta.assistants.files.list(assistant_id)


    async def create_run(self, thread_id, assistant_id, model=None, instructions=None, tools=None):
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
        return await self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id, model=model, instructions=instructions, tools=tools)

    async def retrieve_run(self, thread_id, run_id):
        """
        Retrieves a specific run for a given thread.
        
        Args:
            thread_id (str): The ID of the thread.
            run_id (str): The ID of the run to retrieve.

        Returns:
            The specified run object.
        """
        return await self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

    async def cancel_run(self,thread_id, run_id):
        """
        Cancels an in-progress run.
        
        Args:
            thread_id (str): The ID of the thread.
            run_id (str): The ID of the run to cancel.

        Returns:
            The run object after cancellation.
        """
        return await self.client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)

    async def list_runs(self,thread_id):
        """
        Lists all runs for a given thread.
        
        Args:
            thread_id (str): The ID of the thread.

        Returns:
            A list of run objects for the specified thread.
        """
        return await self.client.beta.threads.runs.list(thread_id=thread_id)


    async def list_run_steps(self,thread_id, run_id):
        """
        Lists all steps for a specific run in a thread.
        
        Args:
            thread_id (str): The ID of the thread.
            run_id (str): The ID of the run.

        Returns:
            A list of run step objects for the specified run.
        """
        return await self.client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run_id)

    async def retrieve_run_step(self,thread_id, run_id, step_id):
        """
        Retrieves a specific run step.
        
        Args:
            thread_id (str): The ID of the thread.
            run_id (str): The ID of the run.
            step_id (str): The ID of the run step to retrieve.

        Returns:
            The specified run step object.
        """
        return await self.client.beta.threads.runs.steps.retrieve(thread_id=thread_id, run_id=run_id, step_id=step_id)


    async def submit_tool_outputs(self,thread_id, run_id, tool_outputs):
        """
        Submits the outputs from tool calls for a run that requires action.
        
        Args:
            thread_id (str): The ID of the thread.
            run_id (str): The ID of the run.
            tool_outputs (list): Outputs from the tool calls.

        Returns:
            The modified run object after submitting the tool outputs.
        """
        return await self.client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)


    def read_json(self, filename):
        try:
            with open(filename) as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return {}
        except json.decoder.JSONDecodeError:
            return {}
        

    def write_json(self, filename, data, append=False):
        mode = 'a' if append else 'w'
        with open(filename, mode) as file:
            json.dump(data, file, indent=4)

    async def get_or_create_thread(self,thread_name=None):
        """
        Get or create a thread of Messages/content.

        This function reads a JSON file to get the ID of an existing thread. If the thread ID is not found, a new thread is created
        using the `client.beta.threads.create()` method. The ID of the new thread is then returned.

        :return: The ID of the thread.
        :rtype: str
        """

        if thread_name is None:
            thread_name = "Deafult_Chat"
            
        data = self.read_json(self.json_file)
        #print(f"Data:   {data}")
        thread_id = data.get(thread_name)
        #print(f"Thread ID:   {thread_id}")

        if not thread_id:
            thread = await self.client.beta.threads.create()
            thread_id = thread.id
            # Save the thread ID to the JSON file
            data[thread_name] = thread_id
            self.write_json(self.json_file, data, append=False)

        return thread_id

    async def list_assistants(self):
        response = await self.client.beta.assistants.list()
        return {assistant.name: assistant.id for assistant in response.data}
    
    

    async def find_or_create_assistant(self, send_name, instructions, tools, model):
        assistants = await self.list_assistants()
        data = self.read_json(self.assistant_file)

        for assistant in assistants:
            data[assistant] = {
                'id': assistants[assistant],
            }

        if send_name in assistants:
            assistant_id = assistants[send_name]
            existing_assistant = await self.retrieve_assistant(assistant_id)

            if existing_assistant.instructions != instructions or existing_assistant.tools != tools or existing_assistant.model != model:
                # Update the assistant with new arguments
                await self.update_assistant(assistant_id, name=send_name, description=existing_assistant.description, instructions=instructions, tools=tools)

            # Update or confirm the assistant information in the JSON file
            data[send_name] = {
                'id': assistant_id,
                'instructions': instructions,
                'tools': tools,
                'model': model
            }
            self.write_json(self.assistant_file, data)
            return assistant_id
        else:
            # Create a new assistant
            assistant = await self.client.beta.assistants.create(
                instructions=instructions,
                name=send_name,
                tools=tools,
                model=model
            )
            assistant_id = assistant.id

            # Save the new assistant information in the JSON file
            data[send_name] = {
                'id': assistant_id,
                'instructions': instructions,
                'tools': tools,
                'model': model
            }
            self.write_json(self.assistant_file, data)
            return assistant_id



    async def update_assistant(self,assistant_id, name=None, description=None, instructions=None, tools=None):
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

        return await self.client.beta.assistants.update(assistant_id, **update_fields)

    def count_tokens(text):
        """
        Counts the number of tokens in a given text string using gpt3_tokenizer.

        Args:
            text (str): The text to be tokenized.

        Returns:
            int: The number of tokens in the text.
        """
        return gpt3_tokenizer.count_tokens(text)


    async def send_message(self,thread_id, content, role="user"):
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
        token_count = self.count_tokens(content)
        print(f"Tokens used in message: {token_count}")
        return await self.client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content)


    async def wait_for_assistant(self,thread_id, assistant_id):
        """
        Wait for the assistant to complete or fail a run in a given thread.

        Args:
            thread_id (str): The ID of the thread to check for runs.
            assistant_id (str): The ID of the assistant to wait for.

        Returns:
            None
        """
        while True:
            runs = await self.client.beta.threads.runs.list(thread_id)
            latest_run = runs.data[0]
            if latest_run.status in ["completed", "failed"]:
                break
            await asyncio.sleep(2) # Wait for 2 seconds before checking again

    def append_to_chat_history(self, thread_id, user_input):
        """
        Appends the user input to the chat history for the given thread ID.

        Args:
            thread_id (str): The ID of the thread to append the chat history to.
            user_input (str): The user's input to add to the chat history.

        Returns:
            None
        """
        data = self.read_json(self.json_file)
        if 'thread_id' not in data:
            data['thread_id'] = thread_id
            self.write_json(self.json_file, data)

    async def display_chat_history(self, thread_id):
        """
        Retrieves and displays the chat history for a given thread ID.

        Args:
            thread_id (str): The ID of the thread to retrieve chat history for.

        Returns:
            None
        """
        response = await self.client.beta.threads.messages.list(thread_id=thread_id)
        for message in reversed(response.data):
            role = message.role
            message_text = message.content[0].text.value
            #Fix this silly mistake
            print(f"{role}: {message_text}")

            
    # Function to get the latest response and handle the run
    async def get_latest_response(self,thread_id, assistant_id, user_input):
        # Send the user message
        await self.send_message(thread_id, user_input)

        # Create a new run for the assistant to respond
        await self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

        # Wait for the assistant's response
        await self.wait_for_assistant(thread_id, assistant_id)

        # Retrieve the latest response
        response = await self.client.beta.threads.messages.list(thread_id=thread_id)
        for message in response.data:
            if message.role == "assistant":
                return message.content[0].text.value, self.count_tokens(message.content[0].text.value)
        return None, 0
