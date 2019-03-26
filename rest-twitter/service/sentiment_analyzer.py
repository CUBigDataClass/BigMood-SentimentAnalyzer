from TweetRetriever import TweetRetriever
from config.location_service_config import CACHE
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from Location_Service import *
import time
import os
import json
import requests



class SentimentAnalyzer:
        def sentiment_analyzer(self,sentence):
                #returns score for a sentence usign vader sentiment analyzer
                analyser = SentimentIntensityAnalyzer()
                score = analyser.polarity_scores(sentence)
                return score['compound']

        def compute_sentiment(self,country, city, hashtag):
                #calls Location Service to obtain LAT LON for a coutnry, city
                #calls Tweet retriver to retrive tweets for a hashtag
                #computes avg score
                tr = TweetRetriever()
                path = os.path.join(os.path.curdir, CACHE['location'])
                ls = LocationService(path, CACHE['dump_interval'])
                coords = ls.get_coordinates_for_city({'city': city, 'country': country})
                tweets = tr.get_tweets(hashtag,coords[LAT],coords[LON])
                compound_sum = 0
                num_tweets = len(tweets)
                if num_tweets == 0:
                        return "No tweets found"
                for tweet in tweets:
                        compound_score = self.sentiment_analyzer(tweet)
                        compound_sum += compound_score
                return compound_sum/num_tweets
