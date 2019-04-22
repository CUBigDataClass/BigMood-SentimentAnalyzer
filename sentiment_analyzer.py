from TweetRetriever import TweetRetriever
from tweet_stream import TweetStream

from config.conf import DUMP_INTERVAL
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from Location_Service import *
from Aggregator import Aggregator

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
        self.ag = Aggregator(csv_location='data/worldcities.csv', bb_location='data/bounding_box.json')
        self.tr = TweetRetriever()
        self.ts = TweetStream()

    def sentiment_analyzer(self, sentence):
        # returns score for a sentence usign vader sentiment analyzer
        analyser = SentimentIntensityAnalyzer()
        score = analyser.polarity_scores(sentence)
        return score['compound']

    def compute_sentiment(self, country_code, city, hashtag, using_n_tweets=100):
        ''' calls Location Service to obtain LAT LON for a coutnry, city
        calls Tweet retriver to retrive tweets for a hashtag
        computes avg score '''
        # log.debug('computing sentiment for ({:s}, {:s}, {:s})'.format(country, city, hashtag))
        log.debug(f"computing sentiment for Country {country_code}, Hashtag {hashtag} pair")
        # coords = self.ls.get_coordinates_for_city({'city': city, 'country': country})
        country_bounding_box = self.ag.get_country_bb(country_code)
        # tweets = self.tr.get_tweets(hashtag, coords[LAT], coords[LON])
        tweets = self.ts.get_tweets(bounding_boxes=country_bounding_box, trends=[hashtag], num_tweets=using_n_tweets)
        compound_sum = 0
        num_tweets = len(tweets)
        if num_tweets == 0:
            # log.warning('No tweets found! Returning 0 sentiment - country/city/hashtag/lat/lon : {:s}, {:s}, {:s}, {:s}, {:s}'.format(country, city, hashtag, coords[LAT],coords[LON]))
            log.warning('No tweets found! Returning 0 sentiment for Country {country_code}, Hashtag {hashtag} pair')
            return 0
        for tweet in tweets:
            compound_score = self.sentiment_analyzer(tweet)
            compound_sum += compound_score
        return compound_sum / num_tweets
