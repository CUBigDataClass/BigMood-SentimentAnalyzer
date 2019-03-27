#!/bin/python

# Make sure to run with e.g. "env TWITTER_API_KEY=xxx TWITTER_API_KEY_SECRET=xxx python TweetRetriever_Test.py"

from TweetRetriever import TweetRetriever
from vaderSent import SentimentAnalyzer
import time
from config.location_service_config import CACHE
from service.Location_Service import *
import os

tr = TweetRetriever()
vs = SentimentAnalyzer()
path = os.path.join(os.path.curdir, CACHE['location'])
ls = LocationService(path, CACHE['dump_interval'])

coords = ls.get_coordinates_for_city({'city': 'denver', 'country': 'US'})
tweets = tr.get_tweets('#ClimateStrike','39.7392358','-104.990251')

for each in tweets:
    score = vs.sentimentAnalyzerScores(each)
    print(each, score)
    print("#####")
avgSent = vs.computeSentiment(tweets)
print(avgSent)
