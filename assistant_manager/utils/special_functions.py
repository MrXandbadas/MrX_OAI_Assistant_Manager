import json
from yfinance import Ticker

def get_stock_price(symbol):
    symbol = Ticker(symbol)
    price = symbol.history(period='1d')['Close'].iloc[0]
    return price

#from assistant_manager.assistant_manager import OAI_Assistant

def analyze_image_with_vision(assistant,prompt, image_url, max_tokens=300):

    '''

    Analyzes an image using the GPT-4 vision model.



    :param OAI_Assistant: OAI_Assistant instance configured with API key.

    :param image_url: URL of the image to be analyzed.

    :param max_tokens: Maximum number of tokens for the response.

    :return: The analysis response from the model.

    '''

    response = assistant.open_ai.chat.completions.create(

        model="gpt-4-vision-preview",

        messages=[

            {

                "role": "user",

                "content": [

                    {"type": "text", "text": prompt},

                    {

                        "type": "image_url",

                        "image_url": {"url": image_url},

                    },

                ],

            }

        ],

        max_tokens=max_tokens,

    )



    return response.choices[0] if response.choices else None


def generate_image(assistant, prompt, model='dall-e-2', n=1, size='1024x1024', quality='standard', style='vivid', response_format='url' or 'b64_json'):
    """
    Creates an image given a prompt using OpenAI's image generation API.

    :param OAI_Assistant: OAI_Assistant instance configured with API key.
    :param prompt: A text description of the desired image(s).
    :param model: The model to use for image generation. Defaults to 'dall-e-2', can be changed to dall-e-3
    :param n: The number of images to generate. Defaults to 1.
    :param size: The size of the generated images. Defaults to '1024x1024'. Must be one of 256x256, 512x512, or 1024x1024 for dall-e-2. Must be one of 1024x1024, 1792x1024, or 1024x1792 for dall-e-3 models.
    :param quality: The quality of the image to be generated. Defaults to 'standard'.
    :param style: The style of the generated images. Defaults to 'vivid'.
    :return: A response object containing the generated images or an error message.
    """
    try:
        response = assistant.open_ai.images.generate(
            model=model,
            prompt=prompt,
            n=n,
            size=size,
            quality=quality,
            style=style,
            response_format=response_format
        )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Define the function to handle image editing
def edit_image(assistant, image_path, mask_path, prompt, n=1, size='1024x1024'):
    """
    Creates an edited or extended image given an original image and a prompt.

    :param OAI_Assistant: OAI_Assistant instance configured with API key.
    :param image_path: Path to the original PNG image to be edited.
    :param mask_path: Path to the mask PNG image defining areas to be edited.
    :param prompt: A text description of the changes to be made to the image.
    :param n: The number of images to generate. Defaults to 1.
    :param size: The size of the generated images. Defaults to '1024x1024'.
    :return: A response object containing the edited images or an error message.
    """
    try:
        with open(image_path, 'rb') as image, open(mask_path, 'rb') as mask:
            response = assistant.open_ai.images.edit(
                image=image,
                mask=mask,
                prompt=prompt,
                n=n,
                size=size
            )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Define the function to handle creating image variations
def create_image_variation(assistant, image_path, n=1, size='1024x1024'):
    """
    Creates a variation of a given image using OpenAI's image variation API.

    :param OAI_Assistant: OAI_Assistant instance configured with API key.
    :param image_path: Path to the source PNG image for creating variations.
    :param n: The number of variations to generate. Defaults to 1.
    :param size: The size of the generated images. Defaults to '1024x1024'.
    :return: A response object containing the image variations or an error message.
    """
    try:
        with open(image_path, 'rb') as image:
            response = assistant.open_ai.images.create_variation(
                image=image,
                n=n,
                size=size
            )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    # Function to append a new tool function and its metadata
def append_new_tool_function_and_metadata(function_name: str, function_code: str, metadata: dict, tool_meta_description: str):
    try:
        # Logic to append new function code to dynamic_functions.py
        with open('assistant_manager/functions/dynamic/dynamic_functions.py', 'a') as file:
            file.write(f'\n\n{function_code}')

        
        # Add the tool_meta_description to the metadata dict
        metadata['tool_meta_description'] = tool_meta_description

        # Logic to append new metadata to functions_metadata.json
        with open('assistant_manager/functions/dynamic/functions_metadata.json', 'r+') as file:
            existing_metadata = json.load(file)
            # Lets run a check to see if the read metadata is hiding in a dict wrapped around our dict
            
            existing_metadata[function_name] = metadata
            file.seek(0)  # Reset file position to the beginning.
            json.dump(existing_metadata, file, indent=4)
    except Exception as e:
        print(f"An error occurred while appending the new function: {e}")
        return False
    return True  # Indication that the function and metadata have been successfully appended
