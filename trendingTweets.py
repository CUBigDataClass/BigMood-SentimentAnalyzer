import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
from twitter import *
import sys
sys.path.append(".")
import config

class TwitterClient(object): 
    ''' 
    Generic Twitter Class for sentiment analysis. 
    '''
    def __init__(self): 
        ''' 
        Class constructor or initialization method. 
        '''
        # keys and tokens from the Twitter Dev Console 
        consumer_key = '6LbBmYGg6MbBmndImr5DR7rB7'
        consumer_secret = 'MI6tf0JmvaQK7B4a5UmL0RrpVZdjb5ArNJPugjhQTqOkFYBZyn'
        access_token = '341470846-ZkzgFqNRW1bsqM0fF6QbWRFtNRXHqgs8lHZyfldC'
        access_token_secret = 'wry0nBqaxWrJIevTPPZaQmr0t2TsIvKqlfhhmFgQ4VRyN'
  
        # attempt authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 

    def get_tweet_sentiment(self, tweet): 
        ''' 
        Utility function to classify sentiment of passed tweet 
        using textblob's sentiment method 
        '''
        # create TextBlob object of passed tweet text 
        analysis = TextBlob(self.clean_tweet(tweet)) 
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'

    def clean_tweet(self, tweet): 
        ''' 
        Utility function to clean tweet text by removing links, special characters 
        using simple regex statements. 
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 

    def get_tweets(self, query, count): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets 
        tweets = [] 
  
        try: 
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = query, count = count) 
            
  
            # parsing tweets one by one


            for tweet in fetched_tweets: 
                # empty dictionary to store required params of a tweet 
                
                	
	            parsed_tweet = {} 
	  
	            # saving text of tweet 
	            parsed_tweet['text'] = tweet.text 
	            # saving sentiment of tweet 
	            parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 
	  
	            # appending parsed tweet to tweets list 
	            if tweet.retweet_count > 0: 
	                # if tweet has retweets, ensure that it is appended only once 
	                if parsed_tweet not in tweets: 
	                    tweets.append(parsed_tweet) 
	            else: 
	                tweets.append(parsed_tweet) 
  
            # return pdotaarsed tweets 
            return tweets 
  
        except tweepy.TweepError as e: 
            # print error (if any) 
            print("Error : " + str(e)) 

def main(): 
    # creating object of TwitterClient Class 
	api = TwitterClient() 
	
	twitter = Twitter(auth = OAuth(config.access_key,
                  config.access_secret,
                  config.consumer_key,
				  config.consumer_secret))
	results = twitter.trends.place(_id = 23424977)

	trendsDict = {}

	trendsList = list()
	count = 0
	for location in results:
		for trend in location["trends"]:
			trendsDict[trend["name"]] = trend["tweet_volume"]

	for key in list(trendsDict.keys()):
		if(trendsDict[key] is None):
			del trendsDict[key]

	#print(trendsDict)

	sortedTrendsDict = sorted(trendsDict.items(),key=lambda kv:kv[1], reverse=True)
	#print(sortedTrendsDict)

	for eachTrend in sortedTrendsDict:
		if count <= 5:
			trendsList.append(eachTrend[0])
			count += 1


	# calling function to get tweets 
	for eachTrend in trendsList:
		tweets = api.get_tweets(query = eachTrend, count = 1000)
		print("Trend is", eachTrend)
		print("#########")
		for each in tweets:
			print(each['text'])

	# tweets = api.get_tweets(query = "People", count = 200)
	# print(tweets)

  
if __name__ == "__main__": 
    # calling main function 
    main() 