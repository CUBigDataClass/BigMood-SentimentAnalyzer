from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from datetime import datetime, timedelta
import json
import os
from sentiment_analyzer import SentimentAnalyzer
from Aggregator import Aggregator
from json import dumps
from kafka import KafkaProducer

from TweetRetriever import TweetRetriever
from tweet_stream import TweetStream

# Logging setup
import logging
import logstash
from config.conf import *

from Utils import get_timestamp

import Producer_And_Consume
from multiprocessing import Queue

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logstash.TCPLogstashHandler(logstash_host, logstash_port, version=1))

paths = [os.path.join(os.path.curdir, 'data/worldcities.csv'), os.path.join(os.path.curdir, 'data/bounding_box.json')]

# MongoDB setup
client = MongoClient(MONGO["URI"])
# Use sentiment database
db = client.sentiments_db

# Use sentiment collection for storing purposes
sentiments = db.sentiments_collection

# connect to kafka producer
kafka_producer = KafkaProducer(bootstrap_servers=[kafka_host],
                               value_serializer=lambda x:
                               dumps(x).encode('utf-8'))

tr = TweetRetriever()

# shared object between consumer and producer.
queue = Queue(maxsize=20000)

producer = Producer_And_Consume.Producer("producer", queue)
trends_consumer = []
sentiment_analyzers = []
for i in range(no_of_config_key):
    sentiment_analyzer = SentimentAnalyzer(tr, [twitter_keys[i]['streamConsumerKey'],
                                                           twitter_keys[i]['streamConsumerSecret'],
                                                           twitter_keys[i]['streamAccessTokenKey'],
                                                           twitter_keys[i]['streamAccessTokenSecret']])
    try:
        log.info("Starting Producer_And_Consume.ConsumerThread")
        cr = Producer_And_Consume.ConsumerThread(str(i), queue, kafka_producer, sentiments, sentiment_analyzer,
                                                 consumer_sleep_time)
        trends_consumer.append(cr)
        sentiment_analyzers.append(sentiment_analyzer)
        cr.start()
    except Exception as ex:
        log.error("failed to start consumer threads." + str(ex))

aggregator = Aggregator(paths[0], paths[1])

# Elastic Beanstalk application setup
# EB looks for an 'application' callable by default
application = Flask(__name__)


# Decorator for index page of endpoint
@application.route('/')
def home():
    return '''<h1>Hello there. Go to /trendsentiment</h1>'''


# Main function for handling GET request
@application.route('/trendsentiment', methods=['GET'])
def get_trend_sentiment():
    # GET request check for query parameters
    try:
        if request.method == 'GET':
            if request.args.get('startDate') is None and request.args.get('endDate') is None:
                # return tweets from one day ago
                log.info('/trendsentiment called without start and end date')

                trends = [json.loads(dumps(trend)) for trend in sentiments.find({
                    'timestamp': {'$gte': (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')}
                }, {"_id": 0})]
                log.info('/trendsentiment : response' + str(trends))
                return jsonify(trends=trends), 200

            log.info('/trendsentiment called with start and end date')
            # store GET query parameters
            start = datetime.strptime(request.args.get('startDate'), "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(request.args.get('endDate'), "%Y-%m-%d %H:%M:%S")

            # query mongo for trend sentiment greater than or equal to start date
            # and less than or equal to end date
            log.info('/trendsentiment start:' + str(start) + ' and end date: ' + str(end))
            trends = [json.loads(dumps(trend)) for trend in sentiments.find(
                {
                    '$and': [
                        {'timestamp': {'$gte': start.strftime('%Y-%m-%d %H:%M:%S')}},
                        {'timestamp': {'$lte': end.strftime('%Y-%m-%d %H:%M:%S')}}
                    ]
                },
                {'_id': 0}
            )]
            return jsonify(trends=trends), 200
    except Exception as e:
        log.info('/trendsentiment error occurred' + str(e))
        return dumps({'error': str(e)})


@application.route("/trendsentiment", methods=['POST'])
def post_trend_sentiment():
    # POST request with json, filter json for info we want to store
    if request.method == 'POST':
        log.info('[POST]/trendsentiment request received')
        data = request.get_json()

        analyzed_tweets = []

        # filter trends with country type and city type.
        trends_with_locationType = list(filter(lambda twt: 'locationType' in twt, data['trends']))
        country_type_trends = list(filter(lambda twt: twt['locationType'] == 'Country', trends_with_locationType))
        city_type__trends = list(filter(lambda twt: twt['locationType'] == 'City', trends_with_locationType))

        # process them independently.
        error = None
        for trend_info in city_type__trends:
            schema = None
            try:
                schema = compute_schema(trend_info)

            except Exception as e:
                log.error("[POST]/trendsentiment: failed to get the sentiment for trend info:" + str(
                    trend_info) + "Error:" + str(e))
            if schema is not None:
                analyzed_tweets.append(schema)
        try:
            log.info("total country type trends:" + str(len(
                country_type_trends)) + " is sent for processing. Result will sent to kafka.")
            producer.produce(country_type_trends)
            # country_trends = aggregator.aggr_city_country(country_type_trends, city_type__trends)
            #
            # for trend_info in country_trends:
            #     schema = compute_schema_country(trend_info)
            #
            #     analyzed_tweets.append(schema)

        except Exception as e:
            error = e
            log.error('[POST]/trendsentiment: Error in aggregating the the tweets countrywise: ' + str(e))

        if len(analyzed_tweets) > 0:
            try:
                # publish the schema to kafka topic
                kafka_producer.send(kafka_topic, value=analyzed_tweets)
            except Exception as e:
                log.error('[POST]/trendsentiment: Failed to publish data to kafka topic' + str(e))

            try:
                # store all tweets that we have analyzed for sentiment in mongo
                log.debug(f"Inserting analyzed tweets {analyzed_tweets}")

                sentiments.insert_many(analyzed_tweets)
                if error is None:
                    log.info(
                        "[POST]/trendsentiment: Successfully inserted data in mongo db, total :" + str(
                            len(analyzed_tweets)))
                    return dumps({'message': 'Succesfully created'})
                else:
                    log.info("[POST]/trendsentiment: error in calling mongodb")
                    return dumps({'message': 'Succesfully created', 'error in aggregating trends': str(error)})
            except Exception as e:
                log.error('[POST]/trendsentiment: Some error occurred:' + str(e))
                return dumps({'error': str(e)})

        else:
            log.info("Nothing to publish on kafka or insert in mongo")
            return dumps({'message': 'Nothing to publish on kafka or insert in mongo'})


def compute_schema(trend_info):
    schema = {
        'country': trend_info['country'],
        'countryCode': trend_info['countryCode'],
        'locationType': trend_info['locationType'],
        'city': trend_info.get('city', None),
        'trends': [{
            'name': tweet['name'],
            'sentiment': sentiment_analyzers[0].compute_sentiment(trend_info['country'], trend_info['city'],
                                                                  tweet['name']),
            'rank': tweet['rank'],
            'tweetVolume': tweet['tweetVolume'],
            'url': tweet['url']
        } for tweet in trend_info['twitterTrendInfo']],
        'timestamp': get_timestamp()
    }
    return schema


# run the app
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app
    log.info('Starting application!')
    application.debug = False
    application.run(host='0.0.0.0', port=app_port)
