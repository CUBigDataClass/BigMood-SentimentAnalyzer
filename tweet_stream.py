# Tweet Stream Class 
import os
import sys
import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from config.conf import consumerKey, consumerSecret, accessTokenKey, accessTokenSecret


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

        #How many tweets you want to find, could change to time based
        if this.count <= this.num_tweets:
            json_data = json.loads(data)

            data = json_data
            if data is not None and [trend in data['text'] for trend in this.trends]:
               print(f"Filtering for tweets with {this.trends[0]}")
               tweet = data["text"]
    
               this.tweets.append(tweet)

               this.count += 1
            return True
        else:
            return False

    def on_error(self, status):
        print(status)


class TweetStream:
    '''Initialize TweetStream. For security, API keys associated with
            your Twitter app should be present in environment variables.
            num_tweets = number of tweets you want to get back from calling statuses/filter Twitter endpoint'''

    def __init__(self, num_tweets=this.num_tweets):
        log.debug(f'Initializing {__name__} with "{num_tweets}" as number of tweets to search')
        self.num_tweets = num_tweets
        self.tweets = this.tweets
        # Load consumer keys from imported configuration.
        log.debug('Loading comsumer keys from configuration file')
        self.consumer_key = consumerKey
        self.consumer_secret = consumerSecret
        self.access_token = accessTokenKey
        self.access_secret = accessTokenSecret
        # Ensure API keys are present.
        if 0 in [len(self.consumer_key), len(self.consumer_secret)]:
            raise EnvironmentError('At least one Twitter API key is not defined in config.conf')
        else:
            log.info('Twitter API key and secret key loaded')
        log.debug('Initializing Twitter client')
        self.client = self._initialize_client()
        if self.client is not None:
            return
        else:
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
            log.debug('Successfully initialized Twitter client')
        except Exception as ex:
            log.warning(f'Connection or access token retrievel error: {ex}')
            client = None
        return client
        
    def get_tweets(self, bounding_boxes, trends, num_tweets):
        this.num_tweets = num_tweets
        this.trends = trends
        self.trends = this.trends
        self.bounding_boxes = bounding_boxes
        log.debug(f"Calling statuses/filter with bounding box location {self.bounding_boxes} and tracks (trends) {this.trends}")
        try:
            self.client.filter(locations=self.bounding_boxes, track=self.trends)
        except Exception as ex:
            log.error(f'No tweets extracted; suppressing error: {ex}')
            this.tweets = None
        return this.tweets



    

    
