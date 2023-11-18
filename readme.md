# OpenAI CMD Terminal Assistant Chat Manager
#### Change threads, keep track of them and continually chat on them, swap assistants out for different kind of help on threads. Re-tool assistants on demand!

---
## Update 18th Nov 2023 -  Old Personal Prompt was - 315 words 2,065 characters to enable on-demand Function Calling. Now ITS A FUNCTION CALL! A much smaller Instruction set is required (either at the assistant invokation level or the run invokation level)
### Update 18th Nov 2023 - Added static functions for openAI image generation.
### update 13th Nov 2023 - Function Calling has been added! Assistants CAN write and call custom functions
---
## Overview
This repository contains two Python scripts for interacting with OpenAI's API:
- `assistant_manager.py`: Manages API interactions.
- `example_cmd_chat.py`: Demonstrates a command-line interface using the above class file.
### Commands
- swapT - Swap Thread
- swapA - Swap Assistant via Number selection
- tool - Give the agent your chatting to some function tools. Youll want to do this when you start a chat with an assistant.

## Setup
1. Clone the repository.
2. Set up your OpenAI credentials in your envs

## Usage to make your own app
- `assistant_manager.py`: Initialize with OpenAI credentials and use its methods.
- `example_cmd_chat.py`: Check this file out to see how you would use certain functions and lay out your code flow. Also demonstrates a command-line interface in action.

Start a chat. Select a Assistant from the avaliable assistants on your account. (A way to create assistants is comming)
Select a thread (if you have previous ones saved locally via the script) 
Chat away!

### What is This Script?
- **Real-Time Interaction**: Experience seamless, real-time conversations with an AI-powered assistant that responds promptly to your queries.
- **Persistent Thread Management**: The script intelligently manages and saves conversation threads, ensuring no inquiry gets lost and every conversation flows smoothly from where it left off.
- **Customizable Assistants**: Tailor your chat assistant to fit specific roles or requirements, making it versatile for a wide array of customer service scenarios, tool them up and watch them go!
- **Hot-Swap Agents**: Swap out agents mid - thread by writing 'swapA'
- **Change Threads**: Change threads/Start a new one by writing 'swapT'
- **Function Calling**: You can use 'tool' to open a numbered menu of avaliable function calls that can be assigned dynamically to the assistant.
- **D-I-Y FUNCTIONS**: Assistants CAN write their own functions with smart prompting and static tool use. I will incorporate a tooler_assistant that is conditioned to provide the correct tools for re-tooling assistants; I just want to make it a bit more robust in terms of re-writing. It likes to write over files and not replace the text all the time. As a tldr: You assistant needs read_file and write_to_file and to be told about dyanmic_functions.py and function_metadata.json and how the function metatdata handling works (specifically that it should always read the files before writing to them and always include the whole file in the rewrite)

### Share any uses!
