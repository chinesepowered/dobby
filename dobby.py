# Importing required libraries
import os
from dotenv import load_dotenv
from fireworks.client import Fireworks

# Load environment variables from .env file
# This ensures that sensitive information like API keys are not hardcoded
load_dotenv()

# Retrieve the Fireworks API key from environment variables
# Using os.getenv() allows for a fallback if the key is not found
fireworks_api_key = os.getenv('FIREWORKS_API_KEY')

# Check if the API key is present
if not fireworks_api_key:
    raise ValueError("FIREWORKS_API_KEY not found in environment variables. "
                     "Please check your .env file.")

# Create the Fireworks client using the retrieved API key
client = Fireworks(api_key=fireworks_api_key)

# Make an API call to create a chat completion
response = client.chat.completions.create(
    model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    messages=[{
        "role": "user",
        "content": "Say this is a test",
    }],
)

# Print the response content
print(response.choices[0].message.content)