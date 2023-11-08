
# README for Customer Inquiry Assistant Script

## Overview
OpenAI Chat Assistant Script

This script demonstrates a sophisticated example of handling customer inquiries, leveraging OpenAI's latest API features to create a robust and interactive chat experience. Primarily designed for terminal-based user interactions, the script showcases the capability to create, manage, and persist chat threads, ensuring seamless continuity in conversations.

Key features of the script include:

    Asynchronous Handling of Inquiries: The script processes customer inquiries asynchronously, enabling efficient and real-time interaction with the AI assistant.

    Thread Management: It adeptly manages chat threads, saving thread IDs and other relevant information to maintain context and continuity in conversations.

    Assistant Customization: Users can create and configure multiple AI assistants, tailoring them to specific needs or roles, and the script will save all relevant information for future reference and modification.

    Multi-Thread Support: The script supports handling multiple chat threads, allowing users to switch between different conversation contexts seamlessly.

    Persistent Storage: All thread and assistant data are stored persistently, ensuring that the conversation history and assistant configurations are retained across sessions.

This script serves as a practical example of how OpenAI's API can be used to build sophisticated, real-time chat applications, suitable for a wide range of interaction scenarios.


## Note - I had to uninstall and reinstall the openai python package to use the new Assistant and Beta featureset
```bash
pip uninstall openai
```

## Prerequisites
- Python 3.7 or higher
- OpenAI API key
- OpenAI organization ID (optional i think??)

## Installation
1. Ensure Python 3.7 or higher is installed on your system.
2. Install the `openai` Python package: 
   ```bash
   pip install openai
   ```

### Dont forget to cd into the folder!
## Usage
1. Replace `YOUR_API_KEY` and `YOUR_ORG_ID` with your actual OpenAI API key and organization ID in the script.
2. Run the script in your Python environment:
   ```bash
   python customer_inquiry_assistant.py
   ```
3. Interact with the script by typing customer inquiries. Use 'exit', 'quit', or 'bye' to end the session.

## Additional Notes
- The script saves the thread ID in a JSON file (`thread_data.json`) for reusing the same thread in subsequent sessions.
- The script displays the chat history at the beginning of each session.
- Ensure your API key and organization ID are kept secure and not shared publicly.
