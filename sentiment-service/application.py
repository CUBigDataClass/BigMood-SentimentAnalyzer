from flask import Flask, request
import pymongo
from bson.json_util import dumps
from datetime import datetime

client = pymongo.MongoClient("mongodb://jpvm:jpvmtdb@18.191.169.163/tweets_db")

db = client.tweets_db

sentiment = db.sentiment_collection

application = Flask(__name__)

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


@application.route('/')
def home():
    return '''<h1>Go to /trendsentiment</h1>'''

# application.add_url_rule('/', 'index', home)

@application.route('/trendsentiment', methods=['GET', 'POST'])
def trends_sentiment_handler():
    if request.method == 'GET':
        # return 'Todo...'
        return str([dumps(obj) for obj in sentiment.find()])

    req_data = request.get_json()
    
    new_tweet_with_sentiment = {
        "woeid": req_data['woeid'],
        "country": req_data['country'],
        "country_code": req_data['countryCode'],
        "hashtag": req_data['trends'][0]['name'],
        "sentiment": "positive", # future implementation will use get_sentiment()
        "timestamp": get_timestamp()
    }

    iid = sentiment.insert_one(new_tweet_with_sentiment)

    return '''Insert ID: {}'''.format(iid)

# application.add_url_rule('/trendsentiment', 'trendsentimet', trends_sentiment_handler, methods=['GET', 'POST'])

# run the app
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app
    application.debug = True
    application.run()