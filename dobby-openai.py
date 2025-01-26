import openai
import json
import os
from dotenv import load_dotenv
from fireworks.client import Fireworks

# user defined functions
from twitter_functions import create_twitter_api_client, post_tweet, fetch_user_tweets

client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# Define the function tool for getting city population
tools = [
    {
        "type": "function",
        "function": {
            # The name of the function
            "name": "get_city_population",
            # A detailed description of what the function does
            "description": "Retrieve the current population data for a specified city.",
            # Define the JSON schema for the function parameters
            "parameters": {
                # Always declare a top-level object for parameters
                "type": "object",
                # Properties define the arguments for the function
                "properties": {
                    "city_name": {
                        # JSON Schema type
                        "type": "string",
                        # A detailed description of the property
                        "description": "The name of the city for which population data is needed, e.g., 'San Francisco'."
                    },
                },
                # Specify which properties are required
                "required": ["city_name"],
            },
        },
    }
]

# Define a comprehensive system prompt
prompt = f"""
You have access to the following function:

Function Name: '{tools[0]["function"]["name"]}'
Purpose: '{tools[0]["function"]["description"]}'
Parameters Schema: {json.dumps(tools[0]["function"]["parameters"], indent=4)}

Instructions for Using Functions:
1. Use the function '{tools[0]["function"]["name"]}' to retrieve population data when required.
2. If a function call is necessary, reply ONLY in the following format:
   <function={tools[0]["function"]["name"]}>{{"city_name": "example_city"}}</function>
3. Adhere strictly to the parameters schema. Ensure all required fields are provided.
4. Use the function only when you cannot directly answer using general knowledge.
5. If no function is necessary, respond to the query directly without mentioning the function.

Examples:
- For a query like "What is the population of Toronto?" respond with:
  <function=get_city_population>{{"city_name": "Toronto"}}</function>
- For "What is the population of the Earth?" respond with general knowledge and do NOT use the function.
"""

# Initial message context
messages = [
    {"role": "system", "content": prompt},
    {"role": "user", "content": "What is the population of San Francisco?"}
]

# Call the model
chat_completion = client.chat.completions.create(
    model="accounts/fireworks/models/qwen2p5-72b-instruct",
    messages=messages,
    tools=tools,
    temperature=0.1
)

# Print the model's response
print(chat_completion.choices[0].message.model_dump_json(indent=4))
