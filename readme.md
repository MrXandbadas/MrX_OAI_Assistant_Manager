
# README for Customer Inquiry Assistant Script

## Overview
This script is designed to handle customer inquiries using OpenAI's new API features. It creates and manages a chat thread, saving the thread ID for continuous conversation. The script handles inquiries asynchronously, ensuring efficient and real-time interaction with the assistant.

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
