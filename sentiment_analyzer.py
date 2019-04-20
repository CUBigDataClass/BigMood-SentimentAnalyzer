from TweetRetriever import TweetRetriever
from config.conf import DUMP_INTERVAL
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from Location_Service import *

# Logging setup
import logging
import logstash
from config.conf import logstash_host, logstash_port
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logstash.TCPLogstashHandler(logstash_host, logstash_port, version=1))


class SentimentAnalyzer:
    def __init__(self):
        log.info('Initializing SentimentAnalyzer')
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

        log.debug('computing sentiment for ({:s}, {:s}, {:s})'.format(country, city, hashtag))
        coords = self.ls.get_coordinates_for_city({'city': city, 'country': country})
        tweets = self.tr.get_tweets(hashtag, coords[LAT], coords[LON])
        compound_sum = 0
        num_tweets = len(tweets)
        if num_tweets == 0:
            log.warning('No tweets found! Returning 0 sentiment - country/city/hashtag/lat/lon : {:s}, {:s}, {:s}, {:s}, {:s}'.format(country, city, hashtag, coords[LAT],coords[LON]))
            return 0
        for tweet in tweets:
            compound_score = self.sentiment_analyzer(tweet)
            compound_sum += compound_score
        return compound_sum / num_tweets
