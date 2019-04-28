[![Build Status](https://travis-ci.com/CUBigDataClass/BigMood-SentimentAnalyzer.svg?branch=master)](https://travis-ci.com/CUBigDataClass/BigMood-SentimentAnalyzer)
<br />
# BigMood-SentimentAnalyzer
This repository contains Sentiment Analyzer for the project Big Mood. Using the currently trending topics on twitter, we display the general mood of a location. This is done by retrieving tweets for trending hashtags and performing sentiment analysis using VADER sentiment analysis tool.

The steps given below will expose the trendsentiment endpoint which gets trending hashtags from BigMood-API. The sentiment for the trends is calculated and updated JSON schema is published to kafka and inserted to MongoDB. Logs can be viewed on Kibana. In addition to the steps below, we have setup CI-CD using TravisCI. <br>
Read more about VADER [here](https://github.com/cjhutto/vaderSentiment)

## Getting Started

Step 1: <br>
Deploy the following services on GCP. Note the credentials for each and use them in Step 2. 
1. MongoDB
2. RedisCache
3. Kafka
4. Logstash

Step 2: <br>
In the config folder, add a file conf.py containing the following configurations :
```
UN = "XXX"                          		# MongoDB username for trends
PW = "XXX"                          		# MongoDB password for trends
HOST = "XXX.XX.XXX.XXX"             		# MongoDB hostname for trends
MONGO = {
	"URI" : "mongodb://"+UN+":"+PW+"@"+HOST
}
DUMP_INTERVAL = {
	'dump_interval': XXX		    	# Cache dump interval in seconds
}
logstash_host = "XX.XX.XXX.XXX"	    		# Logstash hostname
logstash_port = XXXX				# Logstash port
app_port = XXXX					# App's port number
kafka_host = "XX.XXX.XXX.XXX:XXXX"		# Kafka hostname and port
kafka_topic = "XXXX"				# Kafka topic 
consumer_sleep_time = XX			# Kafka consumer sleep time in seconds
twitter_keys = [{				# Twitter keys
	'streamConsumerKey': "XXXX",
    	'streamConsumerSecret': "XXXX",
    	'streamAccessTokenKey': "XXXX",
    	'streamAccessTokenSecret': "XXXX"
    },
    {
        'streamConsumerKey': "XXXX",
        'streamConsumerSecret': "XXXX",
        'streamAccessTokenKey': "XXXX",
        'streamAccessTokenSecret': "XXXX"
    }]
```
Step 3: <br>
Build the docker container (replace path with the project folder name) : <br>
```docker build PATH .``` <br>
Run the docker container (replace image with the image name built above) : <br>
```docker run IMAGE```


## Sentiment Analysis

## Tweet Retrieval for City and Country

### City

Retrieving tweets on a per-city basis is covered by the `TweetRetriever` class, which uses the `birdy` library to abstract the Twitter API. Initialize a `TweetRetriever` with the development environment name to be used for the 30-day search endpoint associated with your Twitter API keys stored in the configuration file.

Once a `TweetRetriever` object is successfully initialized, the instance method `get_tweets(trend, latitude, longitude, radius='25mi', endpoint='7day')` will return Tweets using the `birdy` library. Because we do not have access to Twitter's premium APIs, we often find that the free 7-day search endpoint returns more tweets than the sandbox 30-day search endpoint. No matter which endpoint is chosen, tweets are queried within the given radius of a `(latitude, longitude)` coordinate pair. The 7-day endpoint explicitly excludes retweets from the search query.

Because querying tweets by city requires only a simple GET request to the Twitter API, requests can be made simply and without the additional complexity of a tweet stream.

### Country

## REST API Specifications
(GET, POST, etc)

## Kafka Producer

## Elastic Stack Setup
