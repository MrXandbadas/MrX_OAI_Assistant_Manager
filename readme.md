# OpenAI CMD Terminal Assistant Chat Manager 🤖
#### 🌟 Change threads, keep track of them, and continually chat on them. Swap assistants for different kinds of help on threads. Re-tool assistants on demand!

---
## 🚀 Updates
- **18th Nov 2023**: Old Personal Prompt was 315 words, 2,065 characters to enable on-demand Function Calling. Now, it's a FUNCTION CALL! A much smaller Instruction set is required (either at the assistant invocation level or the run invocation level).
My Prompt:
```
You are a helpful assistant that can complete the users requests
Never leave out code when writing statements.
You will write new function calls in Try statements (so we can catch the error and fix it) ; this enables us to use the functions written in the file. No placeholder code. We create the whole working code for the user along with the metadata.
###
EXAMPLE CORRECT FUNCTION CALLING METATDATA FORMAT:
{
    "tool_name": "read_file",
    "tool_required": "file_name",
    "tool_description": "Read the content of a file",
    "tool_properties": {
        "file_name": {
            "type": "string",
            "description": "The name of the file"
        }
    }
####
```
  
- **18th Nov 2023**: Added static functions for OpenAI image generation. 
- **13th Nov 2023**: Function Calling has been added! Assistants CAN write and call custom functions. 
---

## Overview 📖
This repository contains two Python scripts for interacting with OpenAI's API:
- `assistant_manager.py`: Manages API interactions. 
- `example_cmd_chat.py`: Demonstrates a command-line interface using the above class file. 

### Commands 💻
- `swapT` - Swap Thread
- `swapA` - Swap Assistant via Number selection
- `tool` - Give the agent you're chatting with some function tools. You'll want to do this when you start a chat with an assistant.

## Setup 🛠️
1. Clone the repository.
2. Set up your OpenAI credentials in your environments.

## Usage to Make Your Own App 🌈
- `assistant_manager.py`: Initialize with OpenAI credentials and use its methods.
- `example_cmd_chat.py`: Check this file out to see how you would use certain functions and lay out your code flow. Also demonstrates a command-line interface in action.

Start a chat. Select an Assistant from the available assistants on your account. (A way to create assistants is coming)
Select a thread (if you have previous ones saved locally via the script) 
Chat away!

### What is This Script? 🤔
- **Real-Time Interaction**: Experience seamless, real-time conversations with an AI-powered assistant that responds promptly to your queries.
- **Persistent Thread Management**: The script intelligently manages and saves conversation threads, ensuring no inquiry gets lost and every conversation flows smoothly from where it left off.
- **Customizable Assistants**: Tailor your chat assistant to fit specific roles or requirements, making it versatile for a wide array of customer service scenarios, tool them up and watch them go!
- **Hot-Swap Agents**: Swap out agents mid-thread by writing 'swapA'.
- **Change Threads**: Change threads/Start a new one by writing 'swapT'.
- **Function Calling**: You can use 'tool' to open a numbered menu of available function calls that can be assigned dynamically to the assistant.
- **D-I-Y FUNCTIONS**: Assistants CAN write their own functions now with the implemented append_new_tool_function_and_metadata tool. As long as they know how to write the metadata correctly and are reminded not to leave out any code they are usually okay at this.

### Share Any Uses! 🌍
We'd love to see how you use this script in your projects. Share your stories and applications with us!

### DCODE: Dynamic Function Calls On Demand

#### Engaging with the AI: The Chat Interface

The `example_cmd_chat.py` script is at the heart of user interaction. It serves as the gateway for users to communicate their needs and for the AI to respond with precision.

##### Starting the Chat
![Imagine a gif of a terminal chat like conversation](./screen_capture_demo1.gif)

Users begin by initiating a chat session with the AI assistant. This interaction is the starting point for requesting new functionalities or modifications.

```python
# Users inputs tool and confirms
User: "tool"
User: #Selection for Tools using Numbers, multiple separated by ','
User: #confirm with 1, cancel is 2
```

Now the assistant can use the aforementioned function!

```python
# User requests a new function to open Spotify
User: "Please add a function to open Spotify."

# Assistant acknowledges and processes the request
Assistant: "Function to open Spotify is now added."
```

#### System Updates: Dynamic Functions and Metadata

Upon receiving a user request, DCODE promptly updates `dynamic_functions.py` to include the new capability. Concurrently, `functions_metadata.json` is updated to reflect this addition, ensuring seamless integration and documentation.

```python
# User uses the tool command to select and confirm the new Spotify function
User: "tool"
User: #Select the number corresponding to the new function*
User: 1 #to confirm*
```

#### Seamless Integration *Coming* Please just Restart the python code.

Once the chat session ends and restarts, the AI assistant is fully equipped with the new Spotify functionality. This process exemplifies DCODE's ability to adapt and evolve in real-time, based on user input.

```python
# After restart, the assistant is ready to use the new Spotify function
User: "Open Spotify."
```

Spotify opens (or an error is returned). Spotify is just one example. All functions defined in the dynamic functions were written using the Assistants.

---

