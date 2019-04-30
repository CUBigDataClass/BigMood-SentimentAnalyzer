[![Build Status](https://travis-ci.com/CUBigDataClass/BigMood-SentimentAnalyzer.svg?branch=master)](https://travis-ci.com/CUBigDataClass/BigMood-SentimentAnalyzer)
<br />
# BigMood-SentimentAnalyzer
This repository contains Sentiment Analyzer for the project Big Mood. Using the currently trending topics on twitter, we display the general mood of a location. This is done by retrieving tweets for trending hashtags and performing sentiment analysis using VADER sentiment analysis tool. 

The steps given below will expose the trendsentiment endpoint which gets trending hashtags from BigMood-API. The sentiment for the trends is calculated and updated JSON schema is published to kafka and inserted to MongoDB. Logs can be viewed on Kibana. In addition to the steps below, we have setup CI-CD using TravisCI. <br>

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

A lexicon and rule based sentiment analysis tool  called VADER is used to calculate sentiment scores. It has been known to be successful specifically when dealing with social media text and is fast to be used with streaming data. It also performs well with emojis, exclamation marks, slangs etc.  <br> 

The `SentimentAnalyzer` class has functions that call the location service to get latitude and longitude for a city and uses the `TweetRetriver` get tweets for a city. In case of a country, tweets are retrieved using the twitter streaming api with the help of bounding boxes. The tweets are passed to the `polarity_scores()` method and polarity indices of the tweets are obtained. The compund score metric has been used to represent the overall sentiment of the tweet. This score varies from -1 (extremely negative) to +1 (extremely positive). <br>

The reason for choosing this library over others was that it not just tells whether the text is positive or negative but also tells how positive or negative the text is. 


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

Implementing the Elastic Stack (Elasticsearch, Logstash, and Kibana) for distributed logging and analysis has proven incredibly useful. All three services run on a single AWS or GCP instance. To set up these services, we first follow the tutorial at https://logz.io/learn/complete-guide-elk-stack/#installing-elk. Note that RAM becomes a limitation when running all three services in parallel. Approximately 4GB RAM is required. The smallest instance size we were able to successfully run on without encountering memory issues on GCP was 1 vCPU (3.75 GB memory). We used Ubuntu 16.04 LTS, and the instance has 20GB persistent disk.

BigMood-SentimentAnalyzer is written in Python and writes logs directly to Logstash using a TCP connection to port 9123. BigMood-API is written in Node.js and writes logs directly to Logstash using HTTP requests to port 9214. This is accomplished by various 3rd-party Logstash client libraries available in each language's package ecosystem. We tag each incoming message based on its architecture component, and then route it to Logstash with the following Logstash configuration file. Note that by adding port-based tags, we are able to differentiate between our services when viewing logs in Kibana.

`sudo vim /etc/logstash/conf.d/BigMood.conf`
```input {
  tcp {
    port => 9123
    codec => json
    tags => ["BigMood-SentimentAnalyzer"]
  }
  http {
    port => 9124
    codec => json
    tags => ["BigMood-API"]
  }
}
output {
  elasticsearch {
    hosts => ["localhost:9200"]
  }
}
```

Remember that once the configuration file has been changed, the service must be restarted (`sudo service logstash restart)` for changes to take effect.

Finally, to make the Kibana UI accessible to our 5-person group without exposing it to the entire internet, we no *not* expose the Kibana server's web interface port to the world. Instead, we install `haproxy` with `sudo apt install haproxy`, and expose a tiny HTTP server on port 80 that verifies login credentials and then forwards all port 80 traffic to the Kibana UI's port.

The `haproxy` configuration file that facilitates this is as follows:

```global
        log /dev/log    local0
        log /dev/log    local1 notice
        chroot /var/lib/haproxy
        stats socket /run/haproxy/admin.sock mode 660 level admin
        stats timeout 30s
        user haproxy
        group haproxy
        daemon

        # Default SSL material locations
        ca-base /etc/ssl/certs
        crt-base /etc/ssl/private

        # Default ciphers to use on SSL-enabled listening sockets.
        # For more information, see ciphers(1SSL). This list is from:
        #  https://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/
        ssl-default-bind-ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS
        ssl-default-bind-options no-sslv3

defaults
        log     global
        mode    http
        option  httplog
        option  dontlognull
        timeout connect 1m
        timeout client  50000
        timeout server  50000
        errorfile 400 /etc/haproxy/errors/400.http
        errorfile 403 /etc/haproxy/errors/403.http
        errorfile 408 /etc/haproxy/errors/408.http
        errorfile 500 /etc/haproxy/errors/500.http
        errorfile 502 /etc/haproxy/errors/502.http
        errorfile 503 /etc/haproxy/errors/503.http
        errorfile 504 /etc/haproxy/errors/504.http

userlist UsersFor_Kibana
    user kibana insecure-password MY-SUPER-SECRET-PASSWORD

frontend localnodes
     bind *:80
     mode http
     default_backend nodes
     
backend nodes
     acl AuthOkay_Kibana http_auth(UsersFor_Kibana)
     http-request auth realm Kibana if !AuthOkay_Kibana
     mode http
     balance roundrobin
     option forwardfor
     http-request set-header X-Forwarded-Port %[dst_port]
     http-request add-header X-Forwarded-Proto https if { ssl_fc }
     option httpchk HEAD / HTTP/1.1\r\nHost:localhost
     server server1 127.0.0.1:5601 check
     ```
