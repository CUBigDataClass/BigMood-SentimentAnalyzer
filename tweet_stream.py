# Tweet Stream Class 
import os
import sys
import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

# Logging setup
import logging
import logstash
from config.conf import logstash_host, logstash_port

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logstash.TCPLogstashHandler(logstash_host, logstash_port, version=1))

# global variables for the listener
this = sys.modules[__name__]
this.count = 0
this.num_tweets = 100
this.tweets = []
this.trends = ["#"]


class listener(StreamListener):
    def on_data(self, data):

        # How many tweets you want to find, could change to time based
        if this.count <= this.num_tweets:
            data = json.loads(data)

            if data is not None and 'text' in data and [trend in data['text'] for trend in this.trends]:
                tweet = data["text"]

                this.tweets.append(tweet)

                this.count += 1
            return True
        else:
            return False

    def on_error(self, status):
        log.error(status)


class TweetStream:
    '''Initialize TweetStream. For security, API keys associated with
            your Twitter app should be present in environment variables.
            num_tweets = number of tweets you want to get back from calling statuses/filter Twitter endpoint'''

    def __init__(self, streamConsumerKey, streamConsumerSecret, streamAccessTokenKey, streamAccessTokenSecret,
                 num_tweets=this.num_tweets):
        log.info(f'Initializing {__name__} with "{num_tweets}" as number of tweets to search')
        self.num_tweets = num_tweets
        self.tweets = this.tweets
        # Load consumer keys from imported configuration.
        log.info('Loading comsumer keys from configuration file')
        self.consumer_key = streamConsumerKey
        self.consumer_secret = streamConsumerSecret
        self.access_token = streamAccessTokenKey
        self.access_secret = streamAccessTokenSecret
        # Ensure API keys are present.
        if 0 in [len(self.consumer_key), len(self.consumer_secret)]:
            raise EnvironmentError('At least one Twitter API key is not defined in config.conf')
        else:
            log.info('Twitter API key and secret key loaded')
        log.info('Initializing Twitter client')
        self.client = self._initialize_client()
        if self.client is None:
            raise Exception('Failed to initialize TweetStream')

    def _initialize_client(self):
        '''Initialize the tweepy API client'''

        try:
            # Initialize our client object with consumer keys.
            # Obtain the OAuth2 access token using our consumer keys.
            # Re-initialize our client object that stores the access token for later use.
            auth = OAuthHandler(self.consumer_key, self.consumer_secret)
            auth.set_access_token(self.access_token, self.access_secret)
            client = Stream(auth, listener())
            log.info('Successfully initialized Twitter client')
        except Exception as ex:
            log.error(f'Connection or access token retrievel error: {ex}')
            client = None
        return client

    def get_tweets(self, bounding_boxes, trends, num_tweets):
        this.num_tweets = num_tweets
        this.trends = trends
        self.trends = this.trends
        self.bounding_boxes = bounding_boxes
        log.info(
            f"Calling statuses/filter with bounding box location {self.bounding_boxes} and tracks (trends) {this.trends}")
        try:
            this.count = 0
            self.client.filter(locations=self.bounding_boxes, track=self.trends)
        except Exception as ex:
            log.error(f'No tweets extracted; suppressing error: {ex}')
            this.tweets = []
        return this.tweets
