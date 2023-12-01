
class InterfaceBase():
    def message_user(self, message):
        """Overwrite this function to change how the user is messaged"""
        print(message)

    def get_user_input(self):
        """Overwrite this function to change how the user is messaged"""
        # Get the input from the user
        return input("User: ")

    def get_multiple_choice_multiple_input(self, options:dict):
        print('Please input Numbers only to select any of the following options or enter Q to leave:')
        for i, option in enumerate(options):
            print(f'{i+1}. {option}')
        while True:
            try:
                choice = input('>>> ')
                if choice.lower() in ["q", "quit", "exit"]:
                    return None
                if "," in choice:
                    choices = [int(i) - 1 for i in choice.split(",")]
                    if any(choice >= len(options) or choice < 0 for choice in choices):
                        raise ValueError
                    return [options[list(options.keys())[choice]] for choice in choices]
                else:
                    choice = int(choice) - 1
                    if choice >= len(options) or choice < 0:
                        raise ValueError
                    return [options[list(options.keys())[choice]]] # Modified line
            except ValueError:
                print('Please enter a valid option')


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