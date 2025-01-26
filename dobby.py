# Importing required libraries
import os
from dotenv import load_dotenv
from fireworks.client import Fireworks
from together import Together
import requests
from io import BytesIO
from requests_oauthlib import OAuth1

# user defined functions
from twitter_functions import create_twitter_api_client, post_tweet, fetch_user_tweets

# Load environment variables from .env file
# This ensures that sensitive information like API keys are not hardcoded
load_dotenv()


def generate_image(prompt="", width=1024, height=768, steps=1, n=1):
    """
    Generate an image using the Together.xyz API.

    Args:
        api_key (str): Your Together.xyz API key
        prompt (str, optional): Prompt for image generation. Defaults to empty string.
        width (int, optional): Image width. Defaults to 1024.
        height (int, optional): Image height. Defaults to 768.
        steps (int, optional): Number of generation steps. Defaults to 1.
        n (int, optional): Number of images to generate. Defaults to 1.

    Returns:
        dict: API response containing generated image(s)
    """
    # API endpoint for image generation
    url = "https://api.together.xyz/v1/images/generations"

    # Prepare headers for the request
    key = os.environ.get("TOGETHER_API_KEY")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    # Prepare request payload
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell-Free",
        "prompt": prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "n": n,
        "response_format": "url",
    }

    try:
        # Send POST request to the API
        response = requests.post(url, headers=headers, json=payload)

        # Raise an exception for bad responses
        response.raise_for_status()

        # Return the JSON response
        return response.json()

    except requests.RequestException as e:
        print(f"Error occurred during image generation: {e}")
        return None


def download_and_save_image(url, filename="temp_image.jpg"):
    """Download image from URL and save it locally"""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    return None


def post_tweet_with_image(client, text, image_results):
    # Download the image
    image_url = image_results["data"][0]["url"]
    image_path = download_and_save_image(image_url)

    if image_path:
        # Set up OAuth 1.0a authentication
        auth = OAuth1(
            os.getenv("TWITTER_API_KEY"),
            os.getenv("TWITTER_API_KEY_SECRET"),
            os.getenv("TWITTER_ACCESS_TOKEN"),
            os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        )

        # Upload the media using v1.1 endpoint
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"

        with open(image_path, "rb") as image_file:
            files = {"media": image_file}
            req = requests.post(upload_url, files=files, auth=auth)
            if req.status_code != 200:
                print(f"Failed to upload media: {req.text}")
                return None
            media_id = req.json()["media_id"]

        # Create tweet with media
        response = client.create_tweet(text=text, media_ids=[str(media_id)])

        # Clean up - remove the temporary image file
        os.remove(image_path)

        return response
    else:
        print("Failed to download image")
        return None


# Retrieve the Fireworks API key from environment variables
# Using os.getenv() allows for a fallback if the key is not found
fireworks_api_key = os.getenv("FIREWORKS_API_KEY")
# Check if the API key is present
if not fireworks_api_key:
    raise ValueError(
        "FIREWORKS_API_KEY not found in environment variables. "
        "Please check your .env file."
    )
# Create the Fireworks client using the retrieved API key
client = Fireworks(api_key=fireworks_api_key)

twitter_client = create_twitter_api_client()
# target_tweets=fetch_user_tweets(twitter_client,"sama",15, True, True)
target_tweets = [  # cached due to user limits
    {
        "id": 1883325347959378245,
        "text": "RT @klarnaseb: NOTE: Using OpenAi Operator at your bank in EU is illegal by law! Web access for assistants was banned years ago as part of…",
        "likes": 0,
        "retweets": 131,
        "replies": 0,
    },
    {
        "id": 1883305404089901269,
        "text": "fun watching people react to operator. reminds me of the chatgpt launch!",
        "likes": 3127,
        "retweets": 149,
        "replies": 503,
    },
]
print(target_tweets)

# Make an API call to create a chat completion
response = client.chat.completions.create(
    model="accounts/sentientfoundation/models/dobby-mini-unhinged-llama-3-1-8b#accounts/sentientfoundation/deployments/81e155fc",
    # model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    messages=[
        {
            "role": "system",
            "content": "You are a loyal guard dog named Dobby who will protect your master. You will be given tweets from other people directed to your owner. You are to roast the other person (NOT your owner) if the tweet is negative. If the tweet is positive, just say 'Dobby Approves'. Responses should never exceed 260 characters. Your master is Elon Musk.",
        },
        {
            "role": "user",
            "content": "Sam Altman says 'wrong, as you surely know. want to come visit the first site already under way? this is great for the country. i realize what is great for the country isn't always what's optimal for your companies but in your new role i hope you'll mostly put america first'",
        },
    ],
)

# Print the response content
tweet_text = response.choices[0].message.content
print(response.choices[0].message.content)

image_results = generate_image("Angry doberman on guard duty")
url = image_results["data"][0]["url"]
tweet_image = url

print(tweet_text)
print(tweet_image)

tweet = tweet_text + "\n" + tweet_image
first_275_chars = tweet_text[:275]
print(tweet)

post_tweet_with_image(twitter_client, first_275_chars, image_results)
post_tweet(twitter_client, tweet_text)  # due to some Twitter error in media upload
