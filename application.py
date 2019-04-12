from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from datetime import datetime, timedelta
import json 
from sentiment_service.sentiment_analyzer import SentimentAnalyzer
from config.mongo_config import MONGO

# MongoDB setup
client = MongoClient(MONGO["URI"])
# Use tweets database
db = client.sentiments_db 

# Use sentiment collection for storing purposes
sentiments = db.sentiments_collection 
sentiment_analyzer = SentimentAnalyzer()

# Elastic Beanstalk application setup
# EB looks for an 'application' callable by default
application = Flask(__name__)


# function to get current timestamp used for get endpoint query parameters
def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


# Decorator for index page of endpoint
@application.route('/')
def home():
    return '''<h1>Go to /trendsentiment</h1>'''



# Main function for handling GET request
@application.route('/trendsentiment', methods=['GET'])
def get_trend_sentiment():

    # GET request check for query parameters
    try:
        if request.method == 'GET':
            if request.args.get('startDate') is None and request.args.get('endDate') is None:
                # return tweets from one day ago
                trends = [json.loads(dumps(trend)) for trend in sentiments.find({
                    'timestamp': {'$gte': (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')}
                }, {"_id": 0})]
                return jsonify(trends = trends), 200
            # store GET query parameters
            start = datetime.strptime(request.args.get('startDate'), "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(request.args.get('endDate'), "%Y-%m-%d %H:%M:%S")

            # query mongo for trend sentiment greater than or equal to start date
            # and less than or equal to end date
            trends = [json.loads(dumps(trend)) for trend in sentiments.find(
                {
                    '$and': [
                        {'timestamp': {'$gte': start.strftime('%Y-%m-%d %H:%M:%S')}},
                        {'timestamp': {'$lte': end.strftime('%Y-%m-%d %H:%M:%S')}}
                    ]
                },
                {'_id': 0}
            )]
            return jsonify(trends = trends), 200
    except Exception as e:
        return dumps({'error': str(e)})

@application.route("/trendsentiment", methods=['POST'])
def post_trend_sentiment():
    # POST request with json, filter json for info we want to store
    if request.method == 'POST':
        data = request.get_json()

        analyzed_tweets = []
        
        # make lambda function to filter for when there is no city
        for trend_info in data['trends']:
            schema = {
                'country': trend_info['country'],
                'countryCode': trend_info['countryCode'],
                'locationType': trend_info['locationType'],
                'city': trend_info.get('city', None),
                'trends': [{
                    'name' : tweet['name'],
                    'sentiment': sentiment_analyzer.compute_sentiment(trend_info['country'], trend_info['city'], tweet['name']),
                    'rank': tweet['rank'],
                    'tweetVolume': tweet['tweetVolume']
                    } for tweet in trend_info['twitterTrendInfo']],
                'timestamp': get_timestamp()
            }
            analyzed_tweets.append(schema)
        try:
        # store all tweets that we have analyzed for sentiment in mongo
            sentiments.insert_many(analyzed_tweets)
            return dumps({'message': 'Succesfully created'})
        except Exception as e:
            return dumps({'error': str(e)})

# run the app 
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app
    application.debug = True
    application.run()
