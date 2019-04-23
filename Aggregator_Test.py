import os
from Aggregator import Aggregator
import json

path = os.path.join(os.path.curdir, 'data/worldcities.csv')
bb = os.path.join(os.path.curdir, 'data/bounding_box.json')

aggregator = Aggregator(path, bb)

# Test for bounding box
assert [25.26, -22.27, 32.85, -15.51] == aggregator.get_country_bb('ZW'), 'Failed'
assert 'united states' == aggregator.get_country('New York'), 'Failed'
assert 'united states' == aggregator.get_country('New york'), 'Failed'
assert None == aggregator.get_country(' york'), 'Failed'

assert 'colorado' == aggregator.get_state('Denver'), 'Failed'
assert 'california' == aggregator.get_state('palo alto'), 'Failed'

assert 'united states' == aggregator.get_state_country('colorado'), 'Failed'
assert 'united states' == aggregator.get_state_country('california'), 'Failed'

data = {'trends': [{
    'country': 'Dominican Republic',
    'countryCode': 'DO',
    'locationType': 'City',
    'city': 'Santo Domingo',
    'twitterTrendInfo': [{
        'name': '#Mueller',
        'tweetVolume': 5000,
        'rank': 1,
        'sentiment': 90,
        'url': 'http://twitter.com/search?q=%23TwoOfUs'
    }, {
        'name': '#Dale',
        'tweetVolume': 938100,
        'rank': 2,
        'sentiment': 55,
        'url': 'http://twitter.com/search?q=%23TwoOfUs'
    }, {
        'name': '#DesusAndMero',
        'tweetVolume': 938000,
        'rank': 3,
        'sentiment': 99,
        'url': 'http://twitter.com/search?q=%23TwoOfUs'
    }]
},
    {
        'country': 'United States',
        'countryCode': 'US',
        'locationType': 'City',
        'city': 'Boulder',
        'twitterTrendInfo': [{
            'name': '#Mueller',
            'tweetVolume': 3000,
            'rank': 1,
            'sentiment': 32,
            'url': 'http://twitter.com/search?q=%23TwoOfUs'
        }, {
            'name': '#Staycation',
            'tweetVolume': 938109,
            'rank': 2,
            'sentiment': 13,
            'url': 'http://twitter.com/search?q=%23TwoOfUs'
        },
            {
                'name': '#Sunshine',
                'tweetVolume': 938009,
                'rank': 3,
                'sentiment': 88,
                'url': 'http://twitter.com/search?q=%23TwoOfUs'
            }]
    },
    {
        'country': 'United States',
        'countryCode': 'US',
        'locationType': 'Country',
        'twitterTrendInfo': [{
            'name': '#Mueller',
            'tweetVolume': 938119,
            'rank': 1,
            'url': 'http://twitter.com/search?q=%23TwoOfUs'
        }]
    }]}

res = aggregator.aggr_city_country_from_all_tweets(data)

assert int(res[0]['twitterTrendInfo'][0]['sentiment']) == 68, 'Failed aggregator'
country_type_trends = list(filter(lambda twt: twt['locationType'] == 'Country', data['trends']))
city_trends = list(filter(lambda twt: twt['locationType'] == 'City', data['trends']))

res = aggregator.aggr_city_country(country_type_trends, city_trends)
print(res)
assert int(res[0]['twitterTrendInfo'][0]['sentiment']) == 68, 'Failed aggregator'

print("all tests passed")
