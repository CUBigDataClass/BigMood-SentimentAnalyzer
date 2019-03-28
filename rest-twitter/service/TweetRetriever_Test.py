#!/usr/bin/env python

from TweetRetriever import TweetRetriever
import logging

logging.basicConfig(level=logging.DEBUG)

tr = TweetRetriever(dev_env_name_30d='myDevEnv')

query_str = 'pupper'
coordinates = ('39.7392358', '-104.990251') # Denver, CO

tweets_7d  = tr.get_tweets(query_str, *coordinates, endpoint='7day')
tweets_30d = tr.get_tweets(query_str, *coordinates, endpoint='30day')

for txt, tweets in zip(('7d', '30d'), (tweets_7d, tweets_30d)):
    print('******************************************************************')
    print('******************************************************************')
    print('******* {:s} number of tweets for query "{:s}" = {:d}'.format(txt, query_str, len(tweets)))
    print('******************************************************************')
    print('******************************************************************')
    for each in tweets:
        print(repr(each))
