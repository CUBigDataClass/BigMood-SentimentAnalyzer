from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from datetime import datetime, timedelta
import json
import os
from sentiment_analyzer import SentimentAnalyzer
from config.conf import MONGO
from Aggregator import Aggregator

# Logging setup
import logging
import logstash
from config.conf import logstash_host, logstash_port, app_port

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logstash.TCPLogstashHandler(logstash_host, logstash_port, version=1))

path = os.path.join(os.path.curdir, 'data/worldcities.csv')
# MongoDB setup
client = MongoClient(MONGO["URI"])
# Use sentiment database
db = client.sentiments_db

# Use sentiment collection for storing purposes
sentiments = db.sentiment_collection

sentiment_analyzer = SentimentAnalyzer()

aggregator = Aggregator(path)

# Elastic Beanstalk application setup
# EB looks for an 'application' callable by default
application = Flask(__name__)


# function to get current timestamp used for get endpoint query parameters
def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


# Decorator for index page of endpoint
@application.route('/')
def home():
    return '''<h1>Hello. Go to /trendsentiment</h1>'''


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
        country_type_trends = list(filter(lambda twt: twt['locationType'] == 'Country', data['trends']))
        city_type__trends = list(filter(lambda twt: twt['locationType'] == 'City', data['trends']))

        # process them independently.
        error = None
        for trend_info in city_type__trends:
            schema = compute_schema(trend_info)
            analyzed_tweets.append(schema)
        try:
            country_trends = aggregator.aggr_city_country(country_type_trends, city_type__trends)

            for trend_info in country_trends:
                schema = compute_schema_country(trend_info)
                analyzed_tweets.append(schema)

        except Exception as e:
            error = e
            log.error('[POST]/trendsentiment: Error in aggregaing the the tweets countrywise: ' + str(e))

        try:
            # store all tweets that we have analyzed for sentiment in mongo
            sentiments.insert_many(analyzed_tweets)
            if error is None:
                return dumps({'message': 'Succesfully created'})
            else:
                log.info("[POST]/trendsentiment: Successfully inserted data in mongo db, total :" + len(analyzed_tweets))
                return dumps({'message': 'Succesfully created', 'error in aggregating trends': str(error)})
        except Exception as e:
            log.error('[POST]/trendsentiment: Some error occurred:' + str(e))
            return dumps({'error': str(e)})


def compute_schema(trend_info):
    schema = {
        'country': trend_info['country'],
        'countryCode': trend_info['countryCode'],
        'locationType': trend_info['locationType'],
        'city': trend_info.get('city', None),
        'trends': [{
            'name': tweet['name'],
            'sentiment': sentiment_analyzer.compute_sentiment(trend_info['country'], trend_info['city'], tweet['name']),
            'rank': tweet['rank'],
            'tweetVolume': tweet['tweetVolume']
        } for tweet in trend_info['twitterTrendInfo']],
        'timestamp': get_timestamp()
    }
    return schema


def compute_schema_country(trend_info):
    schema = {
        'country': trend_info['country'],
        'countryCode': trend_info['countryCode'],
        'locationType': trend_info['locationType'],
        'city': trend_info.get('city', None),
        'trends': [{
            'name': tweet['name'],
            'sentiment': tweet['sentiment'],
            'rank': tweet['rank'],
            'tweetVolume': tweet['tweetVolume']
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
