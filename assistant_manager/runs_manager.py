#oai base
import inspect
import json
import time
from assistant_manager.functions.dynamic import dynamic_functions
from assistant_manager.utils import file_operations, special_functions
from assistant_manager.utils.special_functions import append_new_tool_function_and_metadata
from assistant_manager.interface_base import InterfaceBase
from assistant_manager.a_m_threads import OAI_Threads

class Run_Manager(OAI_Threads):

    def __init__(self, api_key, organization, timeout, log_level) -> None:
        super().__init__(api_key, organization, timeout, log_level)


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
                    if action["function"]["name"] == "append_new_tool_function_and_metadata":
                        arguments = json.loads(action["function"]["arguments"])
                        # get the function name
                        function_name = arguments["function_name"]
                        # get the function code
                        function_code = arguments["function_code"]
                        # get the metadata dict
                        function_metadata = arguments["metadata_dict"]

                        function_meta_description = arguments["tool_meta_description"]
                        #Check if we need to json.loads the metadata
                        if isinstance(function_metadata, str):
                            function_metadata = json.loads(arguments["metadata_dict"])
                        #print(f"Function name: {function_name}")
                        self.logger.debug(f"Function code: {function_code}")
                        #print(f"Function metadata: {function_metadata}")
                        # append the function and metadata to the current assistant
                        function_output = append_new_tool_function_and_metadata(function_name, function_code, function_metadata, function_meta_description)
                        #function_output = append_new_tool_function_and_metadata(self, **(arguments))
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                        continue
                        
                    # Functions Dynamically registered in the utils/special_functions.py file    
                    elif action["function"]["name"] in dir(special_functions):
                        arguments = json.loads(action["function"]["arguments"])
                        function_name = action["function"]["name"]
                        function = getattr(special_functions, function_name)
                        #check if the arguments are a string and if so convert to dict
                        if isinstance(arguments, str):
                            arguments = json.loads(arguments)
                        # Does the function need self?
                        if "assistant" in inspect.getfullargspec(function).args:
                            function_output = function(self, **(arguments))
                        else:
                            function_output = function(**(arguments))
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})

                    # Functions Dynamically registered in the utils/file_operations.py file
                    elif action["function"]["name"] in dir(file_operations):
                        arguments = json.loads(action["function"]["arguments"])
                        if isinstance(arguments, str):
                            arguments = json.loads(arguments)
                        function_name = action["function"]["name"]
                        function = getattr(file_operations, function_name)
                        #check if the arguments are a string and if so convert to dict
                        function_output = function(**(arguments))
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})

                    #functions registerd on self
                    elif action["function"]["name"] in dir(self):
                        arguments = json.loads(action["function"]["arguments"])
                        function_name = action["function"]["name"]
                        function = getattr(self, function_name)
                        #check if the arguments are a string and if so convert to dict
                        print(f"ARGUMENTS {arguments}")
                        if isinstance(arguments, str):
                            arguments = json.loads(arguments)
                        function_output = function(**(arguments))
                        # give it time to process
                        time.sleep(2)
                        tools_output.append({"tool_call_id": action["id"], "output": str(function_output)})
                        
                    #functions registered in the dynamic_functions.py file
                    elif action["function"]["name"] in dir(dynamic_functions):
                        
                        arguments = json.loads(action["function"]["arguments"])
                        function_name = action["function"]["name"]
                        function = getattr(dynamic_functions, function_name)
                        #check if the arguments are a string and if so convert to dict
                        function_output = function(**(arguments))
                        # give it time to process
                        time.sleep(2)
                        
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

    def perform_run(self, thread_id, assistant_id=None or str):
        """
        Creates a run
        """

        if assistant_id is None:
            run = self.create_run(thread_id=thread_id, assistant_id=self.assistant_id)
        else:
            run = self.create_run(thread_id=thread_id, assistant_id=assistant_id)
        self.logger.debug(f"Run created: {run}")

        run_done = self.process_run(thread_id=thread_id, run_id=run.id)
        self.logger.debug(f"Run processed: {run_done}")
        #Wait for the run to complete
        if run_done is not None:
            print("Run Completed")
            message_list = self.list_thread_history()
            #check for a new message in the thread
            for message in message_list:
                    message_obj = self.retrieve_message(thread_id=thread_id, message_id=message)
                    if message_obj.id is None:
                        continue
                    if message_obj.id in self.chat_ids:
                        #print("Message already seen")
                        continue
                    else:
                        #message
                        self.message_user(f'assistant: {message_obj.content[0].text.value}')
                        # Put it in the chat_ids list so we don't repeat it
                        self.chat_ids.append(message_obj.id)
        else:
                self.logger.error(f"Run failed: {run}")

