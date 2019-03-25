from flask import Flask, request, jsonify
import pymongo
from bson.json_util import dumps
from datetime import datetime 
import json 
import computeSent

# Connect to Mongo Store
client = pymongo.MongoClient("mongodb://jpvm:jpvmtdb@18.191.169.163/tweets_db")


# Use tweets database
db = client.tweets_db 

# Use sentiment collection
sentiments = db.sentiment_collection 


# Elastic Beanstalk app setup

# EB looks for an 'application' callable by default
application = Flask(__name__)

# function to get current timestamp used for get endpoint query parameters
def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


# Decorator for index page of endpoint
@application.route('/')
def home():
    return '''<h1>Go to /trendsentiment</h1>'''



# Main function for handling GET and POST
@application.route('/trendsentiment', methods=['GET', 'POST'])
def trend_sentiment_handler():

    # GET request with or without query parameters
    if request.method == 'GET':
        if request.args.get('startDate') is None and request.args.get('endDate') is None:
            # return all available tweets
            trends = [json.loads(dumps(trend)) for trend in sentiments.find({}, {"_id": 0})]

            return jsonify(trends = trends)

        
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

        return jsonify(trends = trends)



    # POST request with json, filter json for info we want to store
    data = request.get_json()

    storing = []

    for d in data['data']:
        schema = {
            'country': d['country'],
            'countryCode': d['countryCode'],
            'locationType': d['locationType'],
            'city': d.get('city', None),
            'trends': [{
                'trend' : tweet['name'],
                'sentiment': computeSent.returnSent(d['country'], d['city'], tweet['name']),
                'rank': tweet['rank'],
                'tweetVolume': tweet['tweetVolume']
                } for tweet in d['trends']],
            'timestamp': get_timestamp()
        }
        storing.append(schema)

    # store in mongo
    sentiments.insert_many(storing)

    return "201"

# run the app 
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app
    application.debug = True
    application.run()

    

    
