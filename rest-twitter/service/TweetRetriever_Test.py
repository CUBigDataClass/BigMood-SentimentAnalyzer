#!/bin/python

# Make sure to run with e.g. "env TWITTER_API_KEY=xxx TWITTER_API_KEY_SECRET=xxx python TweetRetriever_Test.py"

from TweetRetriever import TweetRetriever

tr = TweetRetriever(dev_env_name_30d='myDevEnv')

tweets_7d  = tr.get_tweets('Barr','39.7392358','-104.990251', endpoint='7day')
tweets_30d = tr.get_tweets('Barr','39.7392358','-104.990251', endpoint='30day')

for txt, tweets in zip(('7d', '30d'), (tweets_7d, tweets_30d)):
    print('*********************************')
    print('*********************************')
    print('*******', txt, 'number of tweets =', len(tweets))
    print('*********************************')
    print('*********************************')
    for each in tweets:
        print(repr(each))
