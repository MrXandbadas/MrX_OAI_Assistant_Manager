
from typing import List, Optional
import requests
from openai import OpenAI
from openai._types import NotGiven, NOT_GIVEN
from openai.types.beta.threads import ThreadMessage
import logging
import json
import dynamic_functions
from utils.file_operations import read_file, write_file, exec_python, exec_sh
from utils.special_functions import get_stock_price, generate_image, create_image_variation, edit_image
class OAI_Assistant():
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
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.logger.info("Initializing AssistantManager")
        self.open_ai = OpenAI(api_key=api_key, organization=organization, timeout=timeout)
        self.client = self.open_ai.beta
        self.logger.debug(f"Initailized AssistantManager. self.client: {self.client}")
        
        #Set up some defaults to keep track of the current assistant, thread and run
        self.current_assistant = None or OAI_Assistant
        self.assistants = self.list_assistants(limit=30)
        self.current_thread = None
        self.current_thread_history = None
        self.current_run = None
        self.assistant_id = None

        #set up some things to handle the assistant files
        self.assistant_files = {}
        self.assistant_file_ids = {}
        self.assistant_file_names = {}
        self.tool_metadata = {}

        #set up some things to handle list of threads. We will store the thread id and give the thread a name that the user can set and see
        self.threads = None

        #Runs next
        self.runs = {}

        self.chat_ids = []


    def save_json(self, file_name, data):
        """
        Saves a JSON file.

        Args:
            file_name (str): The name of the file to save.
            data (dict): The data to save.

        Returns:
            None
        """
        with open(file_name, 'w') as outfile:
            json.dump(data, outfile)

    def read_json(self, file_name):
        """
        Reads a JSON file.

        Args:
            file_name (str): The name of the file to read.

        Returns:
            dict: The data from the file.
        """
        try:
            with open(file_name) as json_file:
                data = json.load(json_file)
                return data
        except FileNotFoundError:
            self.logger.debug(f"{file_name} not found.")
            return {}
        

    def list_threads(self):
        """
        Returns a dict of threads.

        Args:
            None

        Returns:
            dict: A dict of threads.
        """
        return self.threads
    
    def list_thread_history(self):
        """
        Returns a list of messages in the current thread.

        Args:
            None

        Returns:
            list: A list of messages.
        """
        if self.chat_ids == []:
            self.logger.debug(f"No messages in thread {self.current_thread}")
            return None
        else:
            return self.chat_ids
    
    
    
    def prepare_thread_history(self, thread_id):
        """
        Prepares the thread history for the current thread.

        Args:
            thread_id (str): The ID of the thread to prepare the history for.

        Returns:
            None
        """
        #get the thread history
        thread_history = self.list_messages(thread_id=thread_id)
        #save the thread history to the current thread history
        self.current_thread_history = thread_history
        #SyncCursorPage
        #get the list of messages
        messages = thread_history.data
        #loop through the messages and add them to the chat_ids list
        for message in messages:
            self.chat_ids.append(message.id)
        self.logger.debug(f"Prepared thread history for thread {thread_id}")
         
    def create_blank_thread(self):
        """
        Creates a blank thread.

        Args:
            None

        Returns:
            str: The ID of the blank thread.
        """
        #create a blank thread
        blank_thread = self.create_thread()
        #get the thread ID
        thread_id = blank_thread.id
        #add the thread to the list of threads
        self.threads[thread_id] = "Blank Thread"
        #save the thread ID to the thread_ids.json file
        self.add_thread("Blank Thread", thread_id)
        self.current_thread = thread_id
        #return the thread ID
        return thread_id

    def change_thread(self, thread_name: str or None = None, thread_id: str or None = None) -> int:
        """
        Changes the current thread.

        Args:
            thread_name (str): The name of the thread to change to.
            thread_id (str): The ID of the thread to change to.

        Returns:
            int: thread_id if the thread was changed successfully, False otherwise.
        """
        # A compact function that checks if the thread name or ID is None and handles it
        if thread_name is not None:
            #if the thread name is not None, get the thread ID from the thread_ids.json file
            threads = self.get_threads()

            if thread_name in threads:
                thread_id = threads[thread_name]
                #if we have seen this thread before, get the thread history
                self.prepare_thread_history(thread_id)
                self.current_thread = thread_id
                self.logger.debug(f"Thread {thread_name} found. Changing thread...")
                return thread_id

            else:
                self.logger.debug(f"Thread {thread_name} not found. Creating new thread...")
                #create a new thread
                new_thread = self.create_thread()
                #get the thread ID
                thread_id = new_thread.id
                #add the thread to the list of threads
                # Define thread_id before assigning a thread name to it
                #print(f"Thread ID: {thread_id}")
                #print(f"Thread Name: {thread_name}")
                #save the thread ID to the thread_ids.json file
                self.add_thread(thread_name, thread_id)
                self.current_thread = thread_id
        
            #get the thread history
            self.prepare_thread_history(thread_id)
            self.current_thread = thread_id
            self.logger.debug(f"Changed thread to {thread_id}")
            return thread_id
        elif thread_id is not None:
            #if the thread ID is not None, get the thread name from the thread_ids.json file
            print(f"Trying to change thread to ID {thread_id}")
            threads = self.get_threads()
            #Object with key as thread name and value as thread ID
            thread_name = None
            for key, value in threads.items():
                 if value == thread_id:
                    thread_name = key
                    break

            if thread_name is not None:
                #if we have seen this thread before, get the thread history
                self.prepare_thread_history(thread_id)
                self.current_thread = thread_id
                self.logger.debug(f"Thread {thread_name} found. Changing thread...")
                return thread_id
        else:
             #if both none, create a blank thread
            thread_id = self.create_blank_thread()
            print("Creating Blank Thread...")
            return thread_id
            

    def get_threads(self):
        """
        Returns a list of threads.

        Args:
            None

        Returns:
            list: A list of threads.
        """
        if self.threads is not None:
            return self.threads
        else:
             #attempt to read the thread_ids.json file
            thread_ids = self.read_json('thread_ids.json')
            #if the file is empty, return an empty dict
            if thread_ids is None:
                return {}
            else:
                #if the file is not empty, return the dict
                return thread_ids

    def add_thread(self, thread_name, thread_id):
        """
        Adds a thread to the list of threads json file

        Args:
            thread_name (str): The name of the thread to add.
            thread_id (str): The ID of the thread to add.
        """

        # Read the existing data from the file
        data = self.read_json('thread_ids.json')

        # Add the new entry to the data
        data[thread_name] = thread_id

        # Write the updated data back to the file
        self.save_json('thread_ids.json', data)


    def load_tool_metadata(self):
        """
        Loads the metadata from functions_metadata.json file

        Args:
            None

        Returns:
            dict: A dict of tool metadata.
        """
        #attempt to read the functions_metadata.json file
        tool_metadata_dict0 = self.read_json('default_functions_metadata.json')
        #print(tool_metadata_dict0)
        #print("------")
        tool_metadata_dict1 = self.read_json('functions_metadata.json')
        #print(tool_metadata_dict1)
        # Merge the two dicts into a new dict
        tool_metadata = {**tool_metadata_dict0, **tool_metadata_dict1}
        


        #if the file is empty, return an empty dict
        if tool_metadata is None:
            return {}
        else:
            #if the file is not empty, return the dict
            self.tool_metadata = tool_metadata
            return self.tool_metadata

    def save_tool_metadata(self, tool_name, tool_required, tool_description, tool_schema):
        """
         Save the metadata into functions_metadata.json file

            Args:
                tool_name (str): The name of the tool.
                tool_required (list): The list of required parameters for the tool.
                tool_description (str): The description of the tool.
                tool_schema (dict): The schema of the tool.

            Returns:
                None
        """
        # Read the existing data from the file
        data = self.read_json('functions_metadata.json')

        # Add the new entry to the data
        data[tool_name] = {
            "required": tool_required,
            "description": tool_description,
            "schema": tool_schema
        }

        # Write the updated data back to the file
        self.save_json('functions_metadata.json', data)
        #save to self
        self.tool_metadata = data

    def make_tool_metadata(self, tool_name, tool_required, tool_description, tool_properties):
        """
        Registers metadata for a tool.

        Args:
            tool_name (str): The name of the tool.
            tool_required (str): The ID of the tool.
            tool_description (str): The description of the tool.
            tool_schema (dict): The schema of the tool.

        Returns:
            None
        """
        # Define the metadata for the tool
        metadata = {
                "name": tool_name,
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_properties,
                    "required": [tool_required]
                }
        }
        # Return the metadata
        return metadata

        
    # Lets enable tool use for the assistant
    def enable_tools(self, assistant_id, tools_list):
        """
        Enables tools for the current assistant.

        Args:
            tools_list (list): A list of tools to enable.

        Returns:
            Assistant id or None
        """
        #enable the tools

        print(json.dumps(tools_list, indent=4))
        assistant = self.modify_assistant(assistant_id=assistant_id, tools=tools_list, )
        #save the assistant to the current assistant
        self.current_assistant = assistant
        self.assistant_id = assistant.id
        #return the assistant
        return assistant
    



    def create_assistant(self, model, instructions, name=None, tools=None, file_ids=None, metadata=None):
        """
        Create an assistant with a model and instructions.

        Args:
            model: ID of the model to use. You can use the
                [List models](https://platform.openai.com/docs/api-reference/models/list) API to
                see all of your available models, or see our
                [Model overview](https://platform.openai.com/docs/models/overview) for
                descriptions of them.

            instructions: The system instructions that the assistant uses. The maximum length is 32768
                characters.

            name: The name of the assistant. The maximum length is 256 characters.

            tools: A list of tool enabled on the assistant. There can be a maximum of 128 tools per
                assistant. Tools can be of types `code_interpreter`, `retrieval`, or `function`.

            file_ids: A list of [file](https://platform.openai.com/docs/api-reference/files) IDs
                attached to this assistant. There can be a maximum of 20 files attached to the
                assistant. Files are ordered by their creation date in ascending order.

            metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
                for storing additional information about the object in a structured format. Keys
                can be a maximum of 64 characters long and values can be a maxium of 512
                characters long.
        """
        return self.client.assistants.create(
            model=model, 
            instructions=instructions, 
            name=name, 
            tools=tools, 
            file_ids=file_ids, 
            metadata=metadata
        )


    def modify_assistant(
        self,
        assistant_id: str,
        *,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        file_ids: List[str] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        tools: List[object] | NotGiven = NOT_GIVEN,
    ):
        """
        Modifies an assistant.

        Args:
            assistant_id: The ID of the assistant to modify.
            description: The description of the assistant. The maximum length is 512 characters.
            file_ids: A list of [File](https://platform.openai.com/docs/api-reference/files) IDs
                attached to this assistant. There can be a maximum of 20 files attached to the
                assistant. Files are ordered by their creation date in ascending order. If a
                file was previosuly attached to the list but does not show up in the list, it
                will be deleted from the assistant.
            instructions: The system instructions that the assistant uses. The maximum length is 32768
                characters.
            metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
                for storing additional information about the object in a structured format. Keys
                can be a maximum of 64 characters long and values can be a maxium of 512
                characters long.
            model: ID of the model to use. You can use the
                [List models](https://platform.openai.com/docs/api-reference/models/list) API to
                see all of your available models, or see our
                [Model overview](https://platform.openai.com/docs/models/overview) for
                descriptions of them.
            name: The name of the assistant. The maximum length is 256 characters.
            tools: A list of tool enabled on the assistant. There can be a maximum of 128 tools per
                assistant. Tools can be of types `code_interpreter`, `retrieval`, or `function`.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
       
        return self.client.assistants.update(
            assistant_id=assistant_id,
            model=model,
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
            file_ids=file_ids,
            metadata=metadata,
        )

    def list_assistants(self, limit=20, order="desc", after=None, before=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
        """
        Returns a list of assistants.

        Args:
            limit: A limit on the number of objects to be returned. Limit can range between 1 and
                100, and the default is 20.
            order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
                order and `desc` for descending order.
            after: A cursor for use in pagination. `after` is an object ID that defines your place
                in the list. For instance, if you make a list request and receive 100 objects,
                ending with obj_foo, your subsequent call can include after=obj_foo in order to
                fetch the next page of the list.
            before: A cursor for use in pagination. `before` is an object ID that defines your place
                in the list. For instance, if you make a list request and receive 100 objects,
                ending with obj_foo, your subsequent call can include before=obj_foo in order to
                fetch the previous page of the list.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.client.assistants.list(
            limit=limit, 
            order=order, 
            after=after, 
            before=before, 
            extra_headers=extra_headers, 
            extra_query=extra_query, 
            extra_body=extra_body, 
            timeout=timeout
        )

    def create_assistant_file(self, assistant_id, file_id, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
        """
        Create an assistant file by attaching a
        [File](https://platform.openai.com/docs/api-reference/files) to an
        [assistant](https://platform.openai.com/docs/api-reference/assistants).

        Args:
            assistant_id: The ID of the assistant to which the file should be attached.
            file_id: A [File](https://platform.openai.com/docs/api-reference/files) ID (with
                `purpose="assistants"`) that the assistant should use. Useful for tools like
                `retrieval` and `code_interpreter` that can access files.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.client.assistants.files.create(
            assistant_id=assistant_id,
            file_id=file_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout
        )

    def retrieve_assistant_file(self, assistant_id, file_id, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Retrieves an AssistantFile.

            Args:
                assistant_id: The ID of the assistant from which the file should be retrieved.
                file_id: The ID of the file to retrieve.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.assistants.files.retrieve(
                    assistant_id=assistant_id,
                    file_id=file_id,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )

    def delete_assistant_file(self, assistant_id, file_id, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Delete an assistant file.

            Args:
                assistant_id: The ID of the assistant from which the file should be deleted.
                file_id: The ID of the file to delete.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.assistants.files.delete(
                    assistant_id=assistant_id,
                    file_id=file_id,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )

    def list_assistant_files(self, assistant_id, limit=20, order="desc", after=None, before=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
        """
        Returns a list of assistant files.

        Args:
            assistant_id: The ID of the assistant for which the files should be listed.
            after: A cursor for use in pagination. `after` is an object ID that defines your place
                in the list. For instance, if you make a list request and receive 100 objects,
                ending with obj_foo, your subsequent call can include after=obj_foo in order to
                fetch the next page of the list.
            before: A cursor for use in pagination. `before` is an object ID that defines your place
                in the list. For instance, if you make a list request and receive 100 objects,
                ending with obj_foo, your subsequent call can include before=obj_foo in order to
                fetch the previous page of the list.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and
                100, and the default is 20.
            order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
                order and `desc` for descending order.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.client.assistants.files.list(
            assistant_id=assistant_id,
            limit=limit,
            order=order,
            after=after,
            before=before,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout
        )


    def create_thread(self, messages=None, metadata=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
        """
        Create a thread.

        Args:
            messages: A list of [messages](https://platform.openai.com/docs/api-reference/messages) to
                start the thread with.
            metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
                for storing additional information about the object in a structured format. Keys
                can be a maximum of 64 characters long and values can be a maxium of 512
                characters long.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.client.threads.create(
            messages=messages, 
            metadata=metadata,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout
        )

    def retrieve_thread(self, thread_id, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Retrieves a thread.

            Args:
                thread_id: The ID of the thread to retrieve.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.threads.retrieve(
                    thread_id=thread_id,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )

    def modify_thread(self, thread_id, metadata=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
        """
        Modifies a thread.

        Args:
            thread_id: The ID of the thread to modify.
            metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
                for storing additional information about the object in a structured format. Keys
                can be a maximum of 64 characters long and values can be a maxium of 512
                characters long.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.client.threads.update(
            thread_id=thread_id,
            metadata=metadata,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout
        )

    def delete_thread(self, thread_id, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Delete a thread.

            Args:
                thread_id: The ID of the thread to delete.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.threads.delete(
                    thread_id=thread_id,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )


    def create_message(self, thread_id, role, content, file_ids=NotGiven, metadata=NotGiven, timeout=NotGiven) -> ThreadMessage:
        """
        Create a message.

        Args:
            thread_id: The ID of the thread to create a message in.
            role: The role of the entity that is creating the message. Currently only `user` is supported.
            content: The content of the message.
            file_ids: A list of [File](https://platform.openai.com/docs/api-reference/files) IDs that
                the message should use. There can be a maximum of 10 files attached to a
                message. Useful for tools like `retrieval` and `code_interpreter` that can
                access and use files.
            metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
                for storing additional information about the object in a structured format. Keys
                can be a maximum of 64 characters long and values can be a maxium of 512
                characters long.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.client.threads.messages.create(
            thread_id=thread_id, 
            role=role, 
            content=content
        )

    def retrieve_message(self, thread_id, message_id, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Retrieve a message.

            Args:
                thread_id: The ID of the thread the message belongs to.
                message_id: The ID of the message to retrieve.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            try:
                return self.client.threads.messages.retrieve(
                        thread_id=thread_id,
                        message_id=message_id,
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        extra_body=extra_body,
                        timeout=timeout
                )
            except Exception as e:
                print(f"Error retrieving message: {e}")
                return None

    def modify_message(self, thread_id, message_id, metadata=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
        """
        Modifies a message.

        Args:
            thread_id: The ID of the thread the message belongs to.
            message_id: The ID of the message to modify.
            metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
                for storing additional information about the object in a structured format. Keys
                can be a maximum of 64 characters long and values can be a maxium of 512
                characters long.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.client.threads.messages.update(
            thread_id=thread_id,
            message_id=message_id,
            metadata=metadata,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout
        )

    def list_messages(self, thread_id, limit=20, order="desc", after=None, before=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
        """
        Returns a list of messages for a given thread.

        Args:
            thread_id: The ID of the thread to list messages from.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and
                100, and the default is 20.
            order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
                order and `desc` for descending order.
            after: A cursor for use in pagination. `after` is an object ID that defines your place
                in the list. For instance, if you make a list request and receive 100 objects,
                ending with obj_foo, your subsequent call can include after=obj_foo in order to
                fetch the next page of the list.
            before: A cursor for use in pagination. `before` is an object ID that defines your place
                in the list. For instance, if you make a list request and receive 100 objects,
                ending with obj_foo, your subsequent call can include before=obj_foo in order to
                fetch the previous page of the list.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.client.threads.messages.list(
            thread_id=thread_id, 
            limit=limit, 
            order=order, 
            after=after, 
            before=before,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout
        )

    def retrieve_message_file(self, thread_id, message_id, file_id, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Retrieves a message file.

            Args:
                thread_id: The ID of the thread the message belongs to.
                message_id: The ID of the message the file is attached to.
                file_id: The ID of the file to retrieve.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.threads.messages.files.retrieve(
                    thread_id=thread_id,
                    message_id=message_id,
                    file_id=file_id,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )

    def list_message_files(self, thread_id, message_id, limit=20, order="desc", after=None, before=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
        """
        Returns a list of message files.

        Args:
            thread_id: The ID of the thread the message belongs to.
            message_id: The ID of the message to list files from.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and
                100, and the default is 20.
            order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
                order and `desc` for descending order.
            after: A cursor for use in pagination. `after` is an object ID that defines your place
                in the list. For instance, if you make a list request and receive 100 objects,
                ending with obj_foo, your subsequent call can include after=obj_foo in order to
                fetch the next page of the list.
            before: A cursor for use in pagination. `before` is an object ID that defines your place
                in the list. For instance, if you make a list request and receive 100 objects,
                ending with obj_foo, your subsequent call can include before=obj_foo in order to
                fetch the previous page of the list.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.client.threads.messages.files.list(
            thread_id=thread_id, 
            message_id=message_id, 
            limit=limit, 
            order=order, 
            after=after, 
            before=before,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout
        )

    def create_run(self, thread_id, assistant_id, model=None, instructions=None, tools=None, metadata=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Create a run.

            Args:
                thread_id: The ID of the thread to create a run in.
                assistant_id: The ID of the assistant to use to execute this run.
                model: The ID of the Model to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.
                instructions: Override the default system message of the assistant. This is useful for modifying the behavior on a per-run basis.
                tools: Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.
                metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.threads.runs.create(
                    thread_id=thread_id, 
                    assistant_id=assistant_id, 
                    model=model, 
                    instructions=instructions, 
                    tools=tools, 
                    metadata=metadata,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )

    def retrieve_run(self, thread_id, run_id, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Retrieves a run.

            Args:
                thread_id: The ID of the thread the run belongs to.
                run_id: The ID of the run to retrieve.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )

    def update_run(self, thread_id, run_id, metadata=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Modifies a run.

            Args:
                thread_id: The ID of the thread the run belongs to.
                run_id: The ID of the run to update.
                metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.threads.runs.update(
                    thread_id=thread_id,
                    run_id=run_id,
                    metadata=metadata,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )

    def list_runs(self, thread_id, limit=20, order="desc", after=None, before=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Returns a list of runs belonging to a thread.

            Args:
                thread_id: The ID of the thread to list runs from.
                limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.
                order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.
                after: A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.
                before: A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.threads.runs.list(
                    thread_id=thread_id, 
                    limit=limit, 
                    order=order, 
                    after=after, 
                    before=before,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )
    
    def cancel_run(self, thread_id, run_id, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
            """
            Cancels a run.

            Args:
                thread_id: The ID of the thread the run belongs to.
                run_id: The ID of the run to cancel.
                extra_headers: Send extra headers
                extra_query: Add additional query parameters to the request
                extra_body: Add additional JSON properties to the request
                timeout: Override the client-level default timeout for this request, in seconds
            """
            return self.client.threads.runs.cancel(
                    thread_id=thread_id,
                    run_id=run_id,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout
            )


    def submit_tool_outputs(self, thread_id, run_id, tool_outputs):
        """
        Submits tool outputs for a run.

        Args:
        thread_id: The ID of the thread the run belongs to.
        run_id: The ID of the run to submit tool outputs for.
        tool_outputs: A list of tool outputs to submit. Each output should be a dictionary with a 'tool_call_id' and an 'output'.

        Example:
        submit_tool_outputs(
            thread_id="thread_EdR8UvCDJ035LFEJZMt3AxCd",
            run_id="run_PHLyHQYIQn4F7JrSXslEYWwh",
            tool_outputs=[
                {
                    "tool_call_id": "call_MbELIQcB72cq35Yzo2MRw5qs",
                    "output": "28C"
                }
            ]
        )
        """
        run = self.client.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )
        self.logger.debug(f"Submitted tool outputs for run {run_id}")

        return run
    
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
                    if action["function"]["name"] == "get_stock_price":
                        arguments = json.loads(action["function"]["arguments"])
                        stock_price = get_stock_price(arguments["symbol"])
                        tools_output.append({"tool_call_id": action["id"], "output": stock_price})
                    #else if check if its in the dynamic tool code
                    elif action["function"]["name"] == "write_file":
                        arguments = json.loads(action["function"]["arguments"])
                        write_file(arguments["file_name"], arguments["content"])
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
                    elif action["function"]["name"] == "generate_image":
                        arguments = json.loads(action["function"]["arguments"])
                        function_output = generate_image(self, **arguments)
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                    elif action["function"]["name"] == "create_image_variation":
                        arguments = json.loads(action["function"]["arguments"])
                        function_output = create_image_variation(self, **arguments)
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                    elif action["function"]["name"] == "edit_image":
                        arguments = json.loads(action["function"]["arguments"])
                        function_output = edit_image(self, **arguments)
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                    elif action["function"]["name"] == "append_new_tool_function_and_metadata":
                        arguments = json.loads(action["function"]["arguments"])
                        # get the function name
                        function_name = arguments["function_name"]
                        # get the function code
                        function_code = arguments["function_code"]
                        # get the metadata dict
                        function_metadata = arguments["metadata_dict"]
                        #Check if we need to json.loads the metadata
                        if isinstance(function_metadata, str):
                            function_metadata = json.loads(arguments["metadata_dict"])
                        #print(f"Function name: {function_name}")

                        print(f"Function metadata: {function_metadata}")
                        # append the function and metadata to the current assistant

                    
                        function_output = append_new_tool_function_and_metadata(function_name, function_code, function_metadata)

                        #function_output = append_new_tool_function_and_metadata(self, **(arguments))
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                    elif action["function"]["name"] in dir(dynamic_functions):
                        
                        arguments = json.loads(action["function"]["arguments"])
                        function_name = action["function"]["name"]
                        function = getattr(dynamic_functions, function_name)
                        # Wrap the function call in a try except block so we can hand the error back to as an output
                        
                        #check if the arguments are a string and if so convert to dict
                        
                        function_output = function(**(arguments))
                    
                        
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
    def message_user(self, message):
        """Overwrite this function to change how the user is messaged"""
        print(message)

    def get_user_input(self):
        """Overwrite this function to change how the user is messaged"""
        # Get the input from the user
        return input("User: ")
    
    def get_multiple_choice_input(self, choices):
        """Overwrite this function to change how the user is messaged"""
        # Display the options with corresponding numbers
        options = [f"{i+1}. {choice}" for i, choice in enumerate(choices)]
        self.message_user(f"Please select one of the following options:\n{', '.join(options)}")
        
        # Validate the user's input
        while True:
            choice = input("User: ")
            if choice.isdigit() and 1 <= int(choice) <= len(choices):
                return choices[int(choice) - 1]
            else:
                self.message_user("Invalid choice. Please enter a valid number.")
    
    def setup_thread(self, input_thread_name=None, input_thread_id=None) -> int:
        # Create a new thread if thread_id is None
        
        if input_thread_name is not None:
            thread_id = self.change_thread(input_thread_name)
        elif input_thread_id is not None:
            #change the thread to the thread with the given ID
            thread_id = self.change_thread(thread_id=input_thread_id)
        else:
            #create a thread with the deafult name
            thread_id = self.change_thread(thread_name="Default_Thread")


        self.current_thread = thread_id
        self.prepare_thread_history(thread_id=thread_id)
        return thread_id
    
    def swap_Thread(self):
        #Ask the user for the thread name or ID
        options = ["Name", "ID", "Multiple Choice (Save Locally)"]
        selected = self.get_multiple_choice_input(options)
        # If the user selected name, ask for the name
        if selected == "Name":
            self.message_user("Please enter the name of the thread")
            thread_name = self.get_user_input
            thread_id = self.setup_thread(self, input_thread_name=thread_name)
            return thread_id
        # If the user selected ID, ask for the ID
        elif selected == "ID":
            self.message_user("Please enter the ID of the thread")
            thread_id = self.get_user_input()
            thread_id = self.setup_thread(self, input_thread_id=thread_id)
            return thread_id
        # If the user selected Multiple Choice, Provide a list of threads and ask the user to select one
        elif selected == "Multiple Choice (Save Locally)":
            #load the threads in teh json file
            with open('thread_ids.json') as json_file:
                data = json.load(json_file)
                local_threads = []
                for thread_name, thread_id in data.items():
                    local_threads.append(thread_name)

                selected = self.get_multiple_choice_input(local_threads)
                thread_id = data.get(selected)
                if thread_id is None:
                    self.message_user(f"No thread found with name {selected}")
                    return

                thread_id = self.setup_thread(self, input_thread_id=thread_id)

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

        return assistant_id

    def main_run(self, assistant_id,thread_id):
        while True:
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
                self.message_user("Enabling tools")
                #Grab the tools from the assistant function metadata
                tools = self.load_tool_metadata()
                choices = self.get_multiple_choice_input(tools)
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
                    tool_metadata = self.make_tool_metadata(tool_name=tool_name, tool_required=tool_required, tool_description=tool_description, tool_properties=tool_properties)
                    # add the tool to the metadata dict
                    correct_info = {
                    "type": "function",
                    "function": tool_metadata
                    }
                    #add the tool to the tools list
                    tools_list.append(correct_info)
                    
                #Check if the user wants to enable the tools
                self.message_user("Are you sure you want to enable these tools? (Y/N)")
                choice = self.get_multiple_choice_input(["Y", "N"])

                if choice == "Y":
                    #enable the tools
                    
                    assistant_new = self.enable_tools(assistant_id, tools_list)
                    self.assistant_id = assistant_new.id

                else:
                    self.message_user("Tools not enabled")
                
                continue
            elif message == "swapT":
                thread_swapped = self.swap_Thread()

                if thread_swapped is not None:
                    thread_id = thread_swapped
                    self.current_thread = thread_id
                continue

            elif message == "swapA":
                assistant_id = self.setup_assistant_chat()
                continue

            ThreadMessage = self.create_message(thread_id=thread_id, role="user", content=message)
            user_message_id = ThreadMessage.id
            self.chat_ids.append(user_message_id)
            run = self.create_run(thread_id=thread_id, assistant_id=assistant_id)
            run_done = self.process_run(thread_id=thread_id, run_id=run.id)
            #Wait for the run to complete
            if run_done is not None:
                print("Run Completed")
                message_list = self.list_thread_history()
                #check for a new message in the thread
                for message in message_list:
                        message_obj = self.retrieve_message(thread_id=thread_id, message_id=message)
                        if message_obj.id in self.chat_ids:
                            continue
                        else:
                            self.message_user(f'assistant: {message_obj.content[0].text.value}')
                            self.chat_ids.append(message_obj.id)

            else:
                print(f"Else out? {run.status}")
    
