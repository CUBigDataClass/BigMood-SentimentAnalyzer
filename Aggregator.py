import csv
import itertools

from constants.Constants import *
from queue import PriorityQueue

# Logging setup
import logging
import logstash
from config.conf import logstash_host, logstash_port
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logstash.TCPLogstashHandler(logstash_host, logstash_port, version=1))

class Aggregator:

    def __init__(self, csv_location):
        self.csv_location = csv_location
        self.load_file(csv_location)

    def load_file(self, file_location):
        try:
            city_state = dict()
            city_country = dict()
            state_country = dict()
            with open(file_location) as file:
                readcsv = csv.reader(file, delimiter=CSV_DELIM)
                for _line in readcsv:
                    # Data format
                    # "city","city_ascii","lat","lng","country","iso2","iso3","admin_name","capital","population","id"
                    city_name = None
                    country_id = None
                    state_name = None
                    if (len(_line) > 0):
                        city_name = _line[0].strip().lower()
                    if (len(_line) > 4):
                        country_id = _line[4].strip().lower()
                    if (len(_line) > 7):
                        state_name = _line[7].strip().lower()

                    if (city_name is not None and state_name is not None):
                        city_state[city_name] = state_name
                    if (city_name is not None and country_id is not None):
                        city_country[city_name] = country_id
                    if (state_name is not None and country_id is not None):
                        state_country[state_name] = country_id
            self.city_state = city_state
            self.city_country = city_country
            self.state_country = state_country
            log.info("city_state: " + str(len(self.city_state)))
            log.info("city_country: " + str(len(self.city_country)))
            log.info("state_country: " + str(len(self.state_country)))
        except FileNotFoundError:
            log.error("Load file. File not found: " + file_location)

    def get_state(self, city):
        _city = city.lower()
        if _city in self.city_state.keys():
            return self.city_state[_city]
        return None

    def get_country(self, city):
        _city = city.lower()
        if _city in self.city_country.keys():
            return self.city_country[_city]
        return None

    def get_state_country(self, state):
        _state = state.lower()
        if _state in self.state_country.keys():
            return self.state_country[_state]
        return None

    def aggr_city_state(self, tweets):
        # A dictionary containing 
        # key as state_name
        # value as twt in priorityQueue sorted with rank of the trends

        state_trends = dict()
        for twt in tweets:
            _city = twt.city.lower()
            if _city in self.city_state.keys():
                if self.city_state[_city] in state_trends.keys():
                    state_trends[self.city_state[_city]].put(twt.trends.rank, twt)
                else:
                    pq = PriorityQueue()
                    pq.put(-1 * int(twt.trends.rank), twt)
                    state_trends[self.city_state[_city]] = pq
        return state_trends

    def aggr_city_country_from_all_tweets(self, tweets):
        country_type_trends = list(filter(lambda twt: twt['locationType'] == 'Country', tweets['trends']))
        city_trends = list(filter(lambda twt: twt['locationType'] == 'City', tweets['trends']))
        all_city_trends = list(
            itertools.chain(*list(map(lambda city_trend: city_trend['twitterTrendInfo'], city_trends))))

        for country in country_type_trends:
            for trend in country['twitterTrendInfo']:
                trends_match = list(filter(lambda c_trend: c_trend['name'] == trend['name'], all_city_trends))
                avg_score = 0
                if (len(trends_match) > 0):
                    total_score = sum(map(lambda x: int(x['sentiment']) * int(x['tweetVolume']), trends_match))
                    total_vol = sum(map(lambda x: int(x['tweetVolume']), trends_match))
                    avg_score = total_score / total_vol
                else:
                    log.warning("No matching trends found for cities in :" + trend['twitterTrendInfo'])
                trend['sentiment'] = avg_score

        return country_type_trends

    def aggr_city_country(self, country_type_trends, city_trends):
        log.info("aggr_city_country was called.")

        all_city_trends = list(
            itertools.chain(*list(map(lambda city_trend: city_trend['twitterTrendInfo'], city_trends))))

        for country in country_type_trends:
            for trend in country['twitterTrendInfo']:
                trends_match = list(filter(lambda c_trend: c_trend['name'] == trend['name'], all_city_trends))
                avg_score = 0
                if (len(trends_match) > 0):
                    total_score = sum(map(lambda x: int(x['sentiment']) * int(x['tweetVolume']), trends_match))
                    total_vol = sum(map(lambda x: int(x['tweetVolume']), trends_match))
                    avg_score = total_score / total_vol
                else:
                    log.warning("No matching trends found for cities in :" + trend['twitterTrendInfo'])
                trend['sentiment'] = avg_score

        return country_type_trends
