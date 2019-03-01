from datetime import datetime

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


# Data to serve with our API

TWEETS = {
    "Tweet-1": {
        "woeid": "2367231",
        "location": "Boulder, Colorado",
        "hashtag": "#GOCU",
        "sentiment": "positive",
        "timestamp": get_timestamp()
    },
    "Tweet-2": {
        "woeid": "2367231",
        "location": "Boulder, Colorado",
        "hashtag": "#SkoBUFFS",
        "sentiment": "positive",
        "timestamp": get_timestamp()
    },
    "Tweet-3": {
        "woeid": "2367231",
        "location": "Boulder, Colorado",
        "hashtag": "#FUCKCSU",
        "sentiment": "positive",
        "timestamp": get_timestamp()
    }     
}

# create a handler for our read (GET) tweets
def read():
    """
    This function responds to a request for /api/tweets
    with the complete lists of tweets

    :return:    list of tweets
    """
    return [TWEETS[tweet] for tweet in TWEETS.keys()]