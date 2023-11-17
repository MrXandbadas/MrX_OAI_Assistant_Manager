from yfinance import Ticker

def get_stock_price(stock):
    stock = Ticker(stock)
    price = stock.history(period='1d')['Close'].iloc[0]
    return price

from yfinance import Ticker
from assistant_manager import OAI_Assistant

def get_stock_price(stock):
    stock = Ticker(stock)
    price = stock.history(period='1d')['Close'].iloc[0]
    return price


def generate_image(assistant: OAI_Assistant, prompt, model='dall-e-2', n=1, size='1024x1024', quality='standard', style='vivid', response_format='url' or 'b64_json'):
    """
    Creates an image given a prompt using OpenAI's image generation API.

    :param client: OpenAI client instance configured with API key.
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
def edit_image(assistant: OAI_Assistant, image_path, mask_path, prompt, n=1, size='1024x1024'):
    """
    Creates an edited or extended image given an original image and a prompt.

    :param client: OpenAI client instance configured with API key.
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
def create_image_variation(assistant: OAI_Assistant, image_path, n=1, size='1024x1024'):
    """
    Creates a variation of a given image using OpenAI's image variation API.

    :param client: OpenAI client instance configured with API key.
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
