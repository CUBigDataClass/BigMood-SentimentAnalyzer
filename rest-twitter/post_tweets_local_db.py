from pymongo import MongoClient
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

client = MongoClient()

db = client.tweet_store

tweets = db.tweets

dummy_tweet_1 = {
        "woeid": "2367231",
        "location": "Boulder, Colorado",
        "hashtag": "#GOCU",
        "sentiment": "positive",
        "timestamp": get_timestamp()
    }

dummy_tweet_2 = {
        "woeid": "2367231",
        "location": "Boulder, Colorado",
        "hashtag": "#SkoBUFFS",
        "sentiment": "positive",
        "timestamp": get_timestamp()
    }

dummy_tweet_3 = {
        "woeid": "2367231",
        "location": "Boulder, Colorado",
        "hashtag": "#RALPHIE",
        "sentiment": "positive",
        "timestamp": get_timestamp()
    }     

dummy_data = tweets.insert_many([dummy_tweet_1,dummy_tweet_2, dummy_tweet_3])
print(f"Multiple tweets: {dummy_data.inserted_ids}")