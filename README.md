[![Build Status](https://travis-ci.com/CUBigDataClass/BigMood-SentimentAnalyzer.svg?branch=master)](https://travis-ci.com/CUBigDataClass/BigMood-SentimentAnalyzer)
<br />
# BigMood-SentimentAnalyzer
This repository contains Sentiment Analyzer for the project Big Mood. Using the currently trending topics on twitter, we display the general mood of a location. This is done by retrieving tweets for trending hashtags and performing sentiment analysis using VADER sentiment analysis tool.

The steps given below will expose the trendsentiment endpoint which gets trending hashtags from BigMood-API. The sentiment for the trends is calculated and updated JSON schema is published to kafka and inserted to MongoDB. Logs can be viewed on Kibana. 
Read more about VADER [here](https://github.com/cjhutto/vaderSentiment)

## Getting Started

Step 1:
Deploy the following services on GCP. Note the credentials for each and use them in Step 2. 
1. MongoDB
2. RedisCache
3. Kafka
4. Logstash

Step 2: In the config folder, add a file conf.py containing the following configurations :
```
UN = "XXX"                          		# MongoDB username for trends
PW = "XXX"                          		# MongoDB password for trends
HOST = "XXX.XX.XXX.XXX"             		# MongoDB hostname for trends
CACHE_UN = "XXX"                    		# MongoDB username for cache
CACHE_PW = "XXX"                    		# MongoDB password for cache
CACHE_HOST= "XXX.XX.XX.XXX"         		# MongoDB host for the cache
MONGO = {
	"URI" : "mongodb://"+UN+":"+PW+"@"+HOST,
	"URI_CACHE" : "mongodb://"+CACHE_UN+":"+CACHE_PW+"@"+CACHE_HOST
}
DUMP_INTERVAL = {
	'dump_interval': XXX		    	# Cache dump interval in seconds
}
logstash_host = "XX.XX.XXX.XXX"	    		# Logstash hostname
logstash_port = XXXX				# Logstash port
app_port = XXXX					# App's port number
kafka_host = "XX.XXX.XXX.XXX:XXXX"		# Kafka hostname and port
consumerKey = "XXXXXX"				# Twitter consumer key
consumerSecret = "XXXXXX"			# Twitter consumer secret
accessKey = "XXXXX"				# Twitter access key
accessSecret = "XXXXX"				# Twitter access secret
```
Step 3: 
Build the docker container (replace path with the project folder name) :
```docker build PATH .```
Run the docker container (replace image with the image name built above) :
```docker run IMAGE```
