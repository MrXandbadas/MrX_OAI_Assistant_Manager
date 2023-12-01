from assistant_manager.assistant_manager_update import Assistant_manager_update
from assistant_manager.utils.file_operations import save_json, read_json
import logging

class OAI_Threads(Assistant_manager_update):

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
        super().__init__(api_key=api_key, organization=organization, timeout=timeout, log_level=log_level)


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
            thread_ids = read_json('assistant_manager/thread_ids.json')
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
        data = read_json('assistant_manager/thread_ids.json')

        # Add the new entry to the data
        data[thread_name] = thread_id

        # Write the updated data back to the file
        save_json('assistant_manager/thread_ids.json', data)


    
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
