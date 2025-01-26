# Importing required libraries
import os
from dotenv import load_dotenv
from fireworks.client import Fireworks
from together import Together
import requests

# user defined functions
from twitter_functions import create_twitter_api_client, post_tweet, fetch_user_tweets

# Load environment variables from .env file
# This ensures that sensitive information like API keys are not hardcoded
load_dotenv()

# Retrieve the Fireworks API key from environment variables
# Using os.getenv() allows for a fallback if the key is not found
fireworks_api_key = os.getenv("FIREWORKS_API_KEY")

# Check if the API key is present
if not fireworks_api_key:
    raise ValueError(
        "FIREWORKS_API_KEY not found in environment variables. "
        "Please check your .env file."
    )


#twitter_client=create_twitter_api_client()
#target_tweets=fetch_user_tweets(twitter_client,"elonmusk",15, True, True)
#print(target_tweets)

# Create the Fireworks client using the retrieved API key
client = Fireworks(api_key=fireworks_api_key)

# Make an API call to create a chat completion
response = client.chat.completions.create(
    model="accounts/sentientfoundation/models/dobby-mini-unhinged-llama-3-1-8b#accounts/sentientfoundation/deployments/81e155fc",
    #model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    messages=[
        {
            "role": "system",
            "content": "You are a loyal guard dog named Dobby who will protect your master. You will be given tweets from other people directed to your owner. You are to roast the other person (NOT your owner) if the tweet is negative. If the tweet is positive, just say 'Dobby Approves'. Responses should never exceed 260 characters.",
        },
        {
            "role": "user",
            "content": "Elon says 'You don't have the money'",
        },
    ],
)

# Print the response content
print(response.choices[0].message.content)



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
    key=os.environ.get("TOGETHER_API_KEY")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    # Prepare request payload
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell-Free",
        "prompt": prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "n": n,
        "response_format": "url"
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
      

print(generate_image("Angry doberman on guard duty"))