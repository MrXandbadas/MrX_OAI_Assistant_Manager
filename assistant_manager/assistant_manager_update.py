from assistant_manager.oai_base import OAI_Base

class Assistant_manager_update(OAI_Base):
    
    def __init__(self, api_key, organization, timeout, log_level) -> None:
        super().__init__(api_key, organization, timeout, log_level)



    def swap_assistant(self, new_assistant_id):
        """
        Takes the assistant ID and swaps the assistant
        """
        self.change_assistant_id = new_assistant_id
        # queue the update
        self.queue_update("change_assistant")
        return new_assistant_id
    
    def change_assistant(self):
        """
        Changes the assistant ID
        """
        self.assistant_id = self.change_assistant_id
        return self.assistant_id
    
    ###
    # Section for running Self updates qued by assistants.... ;)
    
    def queue_update(self, function_call, **kwargs):
        """
        Queues the assistant to update

        Args:
            function_call: The function to call holding information about the update required to the oai class
            kwargs: The arguments to pass to the function
        """
        self.update_queue.append((function_call, kwargs))

        return True
    
    def get_update_queue(self):
        """
        Returns the update queue

        Returns:
            list: The update queue
        """
        return self.update_queue
    

    def check_update_assistant(self):
        """
        Checks the update queue and runs the functions in the queue
        """
        output_results = {}
        # Check if the update queue is empty
        if len(self.update_queue) == 0:
            return None
            
        
        # Run the functions in the queue
        for function_name, kwargs in self.update_queue:
            function = getattr(self, function_name)
            function_output = function(**(kwargs))
            output_results[function_name] = function_output
            self.logger.debug(f"Function: {function_name} | Output: {function_output}")
        
        # Empty the queue
        self.update_queue = []
        if output_results is not None or {}:
            return output_results