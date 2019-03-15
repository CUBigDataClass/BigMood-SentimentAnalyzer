#!/bin/python

# Make sure to run with e.g. "env TWITTER_API_KEY=xxx TWITTER_API_KEY_SECRET=xxx python TweetRetriever_Test.py"

from TweetRetriever import TweetRetriever

tr = TweetRetriever()

tweets = tr.get_tweets('cold','39.7392358','-104.990251')

print(tweets)
