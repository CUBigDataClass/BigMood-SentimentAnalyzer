from TweetRetriever import TweetRetriever
from config.mongo_config import DUMP_INTERVAL
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from Location_Service import *


class SentimentAnalyzer:
    def __init__(self):
        self.ls = LocationService(DUMP_INTERVAL['dump_interval'])
        self.tr = TweetRetriever()

    def sentiment_analyzer(self, sentence):
        # returns score for a sentence usign vader sentiment analyzer
        analyser = SentimentIntensityAnalyzer()
        score = analyser.polarity_scores(sentence)
        return score['compound']

    def compute_sentiment(self, country, city, hashtag):
        ''' calls Location Service to obtain LAT LON for a coutnry, city
        calls Tweet retriver to retrive tweets for a hashtag
        computes avg score '''

        coords = self.ls.get_coordinates_for_city({'city': city, 'country': country})
        tweets = self.tr.get_tweets(hashtag, coords[LAT], coords[LON])
        compound_sum = 0
        num_tweets = len(tweets)
        if num_tweets == 0:
            return "No tweets found"
        for tweet in tweets:
            compound_score = self.sentiment_analyzer(tweet)
            compound_sum += compound_score
        return compound_sum / num_tweets
