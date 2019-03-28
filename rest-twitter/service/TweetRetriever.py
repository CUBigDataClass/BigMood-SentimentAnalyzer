import os
from birdy.twitter import AppClient, TwitterClientError
from config.twitter_keys import consumer_key, consumer_secret
class TweetRetriever:

    def __init__(self, dev_env_name_30d='myDevEnv'):
        '''Initialize TweetRetriever. For security, API keys associated with
            your Twitter app should be present in environment variables.
            dev_env_name_30d = dev environment label for your app displayed on Twitter's developer page'''

        self.devenv_30d = dev_env_name_30d
        # Load consumer keys from environment variables.
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        # Ensure API keys are present in environment variables.
        if None in [self.consumer_key, self.consumer_secret]:
            raise EnvironmentError('At least one Twitter API key is not present in the environment')
        else:
            print('Twitter API key and secret key loaded')
        self.client = self._initialize_client()
        if self.client is not None:
            self.resource_search_7day = self.client.api.search.tweets
            self.resource_search_30day = self.client.api['tweets/search/30day/{:s}'.format(self.devenv_30d)]
        else:
            print('Failed to initialize TweetRetriever')

    def _initialize_client(self):
        '''Initialize the birdy API client'''

        try:
            # Initialize our client object with consumer keys.
            client = AppClient(self.consumer_key, self.consumer_secret)
            # Obtain the OAuth2 access token using our consumer keys.
            self.access_token = client.get_access_token()
            # Re-initialize our client object that stores the access token for later use.
            client = AppClient(self.consumer_key, self.consumer_secret, self.access_token)
        except TwitterClientError as ex:
            print('Connection or access token retrievel error:' + str(ex))
            client = None
        return client

    def get_tweets(self, trend, latitude, longitude, radius='25mi', endpoint='7day'):
        '''Returns tweets from Twitter's search/trends endpoint; there may be zero tweets!
            Valid endpoints are '7day' and '30day'.'''

        # Enclose trend in double-quotes for exact matching unless it's a hashtag
        trend = '"' + trend + '"' if trend[0] == '#' else trend

        if endpoint == '7day':
            # Twitter's 7-day search endpoint is preferred; high density of tweets, though incomplete

            # Set up filters to ignore retweets (and replies, if desired)
            filters = '-filter:retweets' #AND -filter:replies'
            # Set up query and geocode strings according to Twitter's API specification
            query_str = '{:s} AND {:s}'.format(trend, filters)
            geocode_str = '{:s},{:s},{:s}'.format(str(latitude), str(longitude), radius)
            # Get response from Twitter!
            #   * result_mode 'recent' returns all recent tweets (not just popular ones)
            #   * tweet_mode 'extended' prevents tweet text from being truncated
            #   * include_entities 'false' prevents Twitter from giving us extra unnecessary info
            try:
                response = self.resource_search_7day.get(q=query_str,
                                                           geocode=geocode_str,
                                                           lang='en',
                                                           result_type='recent',
                                                           tweet_mode='extended',
                                                           count=100,
                                                           include_entities='false')
                # Extract only the tweet text from the response
                tweets = [s.full_text for s in response.data.statuses]
            except Exception as ex:
                print('Error: {:s}'.format(str(ex)))
                tweets = None
            return tweets

        elif endpoint == '30day':
            # Twitter's 30-day search endpoint within a free sandbox environment is not preferred,
            #  since in testing it returns a very low temporal density of tweets (many fewer than 7-day)

            # Build the geocode and query strings for the 30-day endpoint (different format than 7-day)
            geocode_str = 'point_radius:[{:s} {:s} {:s}]'.format(str(longitude), str(latitude), radius)
            query_str = '{:s} lang:en {:s}'.format(trend, geocode_str)
            try:
                # Response is also slightly different than 7-day search response
                print(query_str)
                response = self.resource_search_30day.get(query=query_str)
                tweets = [result.text for result in response.data['results']]
            except Exception as ex:
                print('Error: {:s}'.format(str(ex)))
                tweets = None
            return tweets
        
        else:
            raise NotImplementedError('Requested Twitter endpoint must be 7day or 30day')
