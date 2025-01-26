# twitter_api_utils.py
import os
import tweepy
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any  # Add this line

# Always load environment variables
load_dotenv()

def create_twitter_api_client():
    """
    Create and return a Twitter API client using OAuth 2.0 authentication.
    
    Returns:
        tweepy.Client: Authenticated Twitter API client
    """
    try:
        # Retrieve credentials from environment variables
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        api_key = os.getenv('TWITTER_API_KEY')
        api_key_secret = os.getenv('TWITTER_API_KEY_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Validate that all required credentials are present
        if not all([bearer_token, api_key, api_key_secret, access_token, access_token_secret]):
            raise ValueError("Missing Twitter API credentials. Please check your .env file.")
        
        # Authentication using OAuth 2.0
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_key_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        return client
    
    except Exception as e:
        print(f"Error creating Twitter API client: {e}")
        return None

def post_tweet(client, message):
    """
    Post a tweet using the provided Twitter API client.
    
    Args:
        client (tweepy.Client): Authenticated Twitter API client
        message (str): Text of the tweet to be posted
    
    Returns:
        dict: Response from the Twitter API containing tweet details, or None if posting fails
    """
    try:
        # Validate tweet length (Twitter limit is 280 characters)
        if len(message) > 280:
            raise ValueError(f"Tweet is too long. Maximum 280 characters, current length: {len(message)}")
        
        # Post the tweet
        response = client.create_tweet(text=message)
        
        print("Tweet posted successfully!")
        print(f"Tweet ID: {response.data['id']}")
        print(f"Tweet Text: {message}")
        
        return response
    
    except tweepy.TweepError as e:
        print(f"Error posting tweet: {e}")
        return None
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return None


def fetch_user_tweets(
    client: tweepy.Client, 
    username: str, 
    max_tweets: int = 10, 
    exclude_replies: bool = False, 
    include_retweets: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch recent tweets from a specific user account.
    
    Args:
        client (tweepy.Client): Authenticated Twitter API client
        username (str): Twitter username to fetch tweets from (without '@')
        max_tweets (int, optional): Maximum number of tweets to retrieve. Defaults to 10.
        exclude_replies (bool, optional): Whether to exclude reply tweets. Defaults to False.
        include_retweets (bool, optional): Whether to include retweets. Defaults to False.
    
    Returns:
        List[Dict[str, Any]]: List of tweet dictionaries containing tweet details
    """
    try:
        # Validate input
        if max_tweets < 1 or max_tweets > 100:
            raise ValueError("max_tweets must be between 1 and 100")
        
        # First, get the user ID
        user_response = client.get_user(username=username)
        if not user_response or not user_response.data:
            raise ValueError(f"Could not find user with username: {username}")
        
        user_id = user_response.data.id
        
        # Configure tweet retrieval options
        tweet_fields = [
            'created_at', 'text', 'author_id', 'conversation_id', 
            'public_metrics', 'referenced_tweets'
        ]
        
        # Additional filtering
        excludes = []
        if exclude_replies:
            excludes.append('replies')
        if not include_retweets:
            excludes.append('retweets')
        
        # Fetch tweets
        tweets_response = client.get_users_tweets(
            id=user_id,
            max_results=max_tweets,
            tweet_fields=tweet_fields,
            exclude=excludes if excludes else None
        )
        
        # Check if tweets were retrieved
        if not tweets_response or not tweets_response.data:
            print(f"No tweets found for user: {username}")
            return []
        
        # Process and return tweets
        processed_tweets = []
        for tweet in tweets_response.data:
            tweet_info = {
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at,
                'likes': tweet.public_metrics.get('like_count', 0),
                'retweets': tweet.public_metrics.get('retweet_count', 0),
                'replies': tweet.public_metrics.get('reply_count', 0)
            }
            processed_tweets.append(tweet_info)
        
        return processed_tweets
    
    except Exception as e:
        print(f"Error fetching tweets for {username}: {e}")
        return []
