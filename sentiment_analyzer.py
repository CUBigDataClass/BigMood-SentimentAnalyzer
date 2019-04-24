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
    def __init__(self, tr, ts):
        log.info('Initializing SentimentAnalyzer')
        self.ls = LocationService(DUMP_INTERVAL['dump_interval'])
        self.ag = Aggregator(csv_location='data/worldcities.csv', bb_location='data/bounding_box.json')
        self.tr = tr
        self.ts = ts

    def sentiment_analyzer(self, sentence):
        # returns score for a sentence usign vader sentiment analyzer
        analyser = SentimentIntensityAnalyzer()
        score = analyser.polarity_scores(sentence)
        return score['compound']

    def compute_sentiment(self, country, city, hashtag):
        ''' calls Location Service to obtain LAT LON for a coutnry, city
        calls Tweet retriver to retrive tweets for a hashtag
        computes avg score '''
        log.debug(f"computing sentiment for Country {country}, Hashtag {hashtag} pair")
        coords = self.ls.get_coordinates_for_city({'city': city, 'country': country})
        tweets = self.tr.get_tweets(hashtag, coords[LAT], coords[LON])

        compound_sum = 0
        if tweets is not None:
            num_tweets = len(tweets)
            if num_tweets == 0:
                log.warning(f'No tweets found! Returning 0 sentiment for Country {country}, Hashtag {hashtag} pair')
                return 0
            for tweet in tweets:
                compound_score = self.sentiment_analyzer(tweet)
                compound_sum += compound_score
            return compound_sum / num_tweets
        else:
            log.warning(f'No tweets found! Returning 0 sentiment for Country {country}, Hashtag {hashtag} pair')
            return 0

    def compute_sentiment_for_country(self, country_code, hashtag, city="Boulder", using_n_tweets=100):
        ''' calls Location Service to obtain LAT LON for a coutnry, city
        calls Tweet retriver to retrive tweets for a hashtag
        computes avg score '''
        log.debug(f"computing sentiment for Country {country_code}, Hashtag {hashtag} pair")
        country_bounding_box = self.ag.get_country_bb(country_code)
        tweets = self.ts.get_tweets(bounding_boxes=country_bounding_box, trends=[hashtag], num_tweets=using_n_tweets)
        compound_sum = 0
        if tweets is not None:
            num_tweets = len(tweets)
            if num_tweets == 0:
                log.warning(f'[compute_sentiment_for_country] - No tweets found! Returning 0 sentiment for Country {country_code}, Hashtag {hashtag} pair')
                return 0
            for tweet in tweets:
                compound_score = self.sentiment_analyzer(tweet)
                compound_sum += compound_score
            return compound_sum / num_tweets
        else:
            log.error("[compute_sentiment_for_country] - no tweets from twitter")
            return 0

