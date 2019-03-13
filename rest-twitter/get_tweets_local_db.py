from pymongo import MongoClient
from bson.json_util import dumps
import json

client = MongoClient()

db = client.tweet_store

tweets = db.tweets

# create a handler for our read (GET) tweets
def read():
    """
    This function responds to a request for /api/tweets
    with the complete lists of tweets

    :return:    list of tweets
    """
    return [dumps(tweet) for tweet in tweets.find()]