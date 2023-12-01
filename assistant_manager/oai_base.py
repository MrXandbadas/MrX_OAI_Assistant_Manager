import logging
from openai import OpenAI
from typing import List, Optional
from openai import OpenAI
from openai._types import NotGiven, NOT_GIVEN
from openai.types.beta.threads import ThreadMessage
from assistant_manager.interface_base import InterfaceBase



class OAI_Base(InterfaceBase):
    def __init__(self, api_key, organization, timeout, log_level) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.logger.info("Initializing AssistantManager")
        self.open_ai = OpenAI(api_key=api_key, organization=organization, timeout=timeout)
        self.client = self.open_ai.beta
        self.logger.debug(f"Initailized AssistantManager. self.client: {self.client}")

        # Set up some defaults to keep track of the current assistant, thread and run
        self.current_assistant = None
        self.assistants = self.list_assistants(limit=30)
        self.current_thread = None
        self.current_thread_history = None
        self.current_run = None
        self.assistant_id = None
        self.change_assistant_id = None
        self.update_queue = []
        self.assistant_files = {}
        self.assistant_file_ids = {}
        self.assistant_file_names = {}
        self.tool_metadata = {}
        self.threads = None
        self.runs = {}
        self.chat_ids = []
        

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
    
    def get_assistant_id_by_name(self, assistant_name, id=None):
        """
        Returns an assistant ID, when searched by name
        Takes a ID if given

        Args:
            assistant_name: The name of the assistant to search for.
            id: The ID of the assistant to search for if you dont have a name.

        Returns:
            assistant_id: The ID of the assistant.
        """
        
        if id is None:
            assistants = self.list_assistants(limit=30)
            for i, assistant in enumerate(assistants.data):
                if assistant.name == assistant_name:
                    assistant_id = assistant.id
                    self.logger.debug(f"Assistant ID found: {assistant_id}")
                    return assistant_id
            self.logger.error(f"Assistant ID not found: {assistant_name}")
            return None
        else:
            self.logger.debug(f"Assistant ID found: {id}")
            return id


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