from TweetRetriever import TweetRetriever
from vaderSent import SentimentAnalyzer
from config.location_service_config import CACHE
from Location_Service import *
import time
import os
import json
import requests

def returnSent(country, city, hashtag):
    tr = TweetRetriever()
    vs = SentimentAnalyzer()
    path = os.path.join(os.path.curdir, CACHE['location'])
    ls = LocationService(path, CACHE['dump_interval'])
    coords = ls.get_coordinates_for_city({'city': city, 'country': country})
    print(coords)
    tweets = tr.get_tweets(hashtag,coords[LAT],coords[LON])
    print(tweets)
    avgSent = vs.computeSentiment(tweets)
    return avgSent