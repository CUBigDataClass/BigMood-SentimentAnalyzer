import os
from birdy.twitter import AppClient

class TweetRetriever:

    def __init__():
        '''Initialize TweetRetriever. For security, API keys associated with
            your Twitter app should be present in environment variables.'''

        # Load consumer keys from environment variables.
        self.consumer_key = os.environ.get('TWITTER_API_KEY')
        self.consumer_secret = os.environ.get('TWITTER_API_KEY_SECRET')
        # Ensure API keys are present in environment variables.
        if self.consumer_key == 'None' or self.consumer_secret == 'None'
            raise EnvironmentError('At least one Twitter API key is not present in the environment')
        else:
            print('Twitter API key and secret key loaded')
        self.client = _initialize_client()
        if client is not None:
            self.resource_search_tweets = self.client.api.search.tweets
        else:
            print('Failed to initialize TweetRetriever')

    def _initialize_client():
        '''Initialize the birdy API client'''

        try:
            # Initialize our client object with consumer keys.
            client = AppClient(consumer_key, consumer_secret)
            # Obtain the OAuth2 access token using our consumer keys.
            access_token = client.get_access_token()
            # Re-initialize our client object that stores the access token for later use.
            client = AppClient(consumer_key, consumer_secret, access_token)
        except TwitterClientError as ex:
            print('Connection or access token retrievel error:' + str(ex))
            client = None
        return client

    def get_tweets(trend, latitude, longitude, radius='25mi')
        '''Returns tweets from Twitter's search/trends endpoint; there may be zero tweets!'''

        # Enclose trend in double-quotes for exact matching unless it's a hashtag
        trend = '"' + trend + '"' if trend[0] == '#' else trend
        # Set up filters to ignore retweets (and replies, if desired)
        filters = '-filter:retweets' #AND -filter:replies'
        # Set up query and geocode strings according to Twitter's API specification
        query_str = '{:s} AND {:s}'.format(trend, filters)
        geocode_str = '{:s},{:s},{:s}'.format(str(latitude), str(longitude), radius)
        # Get response from Twitter!
        #   * result_mode 'recent' returns all recent tweets (not just popular ones)
        #   * tweet_mode 'extended' prevents tweet text from being truncated
        #   * include_entities 'false' prevents Twitter from giving us extra unnecessary info
        response = self.resource_search_tweets.get(q=query_str,
                                                   geocode=geocode_str,
                                                   lang='en',
                                                   result_type='recent',
                                                   tweet_mode='extended',
                                                   count=100,
                                                   include_entities='false')
        # Extract only the tweet text from the response
        tweets = [s.full_text for s in response.data.statuses]
        return tweets
