import os
import datetime
import tweepy
from dotenv import load_dotenv
load_dotenv()

client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

def post_to_twitter(message):
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        tweet = client.create_tweet(text=message)
        tweet_id = tweet.data["id"]

        user = client.get_me().data
        username = user.username

        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
        return {
            "id": tweet_id,
            "text": message,
            "url": tweet_url,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    except tweepy.TooManyRequests as e:
        print("Twitter rate limit hit. Skipping this tweet.")
        return {"error": "Rate limit hit: Too Many Requests"}
    except Exception as e:
        return {"error": str(e)}
