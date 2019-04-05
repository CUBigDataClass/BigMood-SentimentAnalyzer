import sys
import csv

from constants.Constants import *
from queue import PriorityQueue

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
                        #"city","city_ascii","lat","lng","country","iso2","iso3","admin_name","capital","population","id"
                        city_name = None
                        country_id = None
                        state_name = None
                        if(len(_line)>0):
                            city_name = _line[0].strip().lower()
                        if(len(_line)>4):
                            country_id = _line[4].strip().lower()
                        if(len(_line)>7):
                            state_name = _line[7].strip().lower()
                        
                        if(city_name is not None and state_name is not None):
                            city_state[city_name] = state_name
                        if(city_name is not None and country_id is not None):
                            city_country[city_name] = country_id
                        if(state_name is not None and country_id is not None):
                            state_country[state_name] = country_id
                self.city_state = city_state
                self.city_country = city_country
                self.state_country = state_country
                print("city_state: " + str(len(self.city_state)))
                print("city_country: " + str(len(self.city_country)))
                print("state_country: " + str(len(self.state_country)))
            except FileNotFoundError:
                print("Load file. File not found: " + file_location)

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

    def aggr_city_country(self, tweets):
        # A dictionary containing 
        # key as country code
        # value as twt in priorityQueue sorted with rank of the trends
        country_trends = dict()
        for twt in tweets:
            if twt.countryCode.lower() in country_trends.keys():
                country_trends[twt.countryCode.lower()].put(twt.trends.rank, twt)
            else:
                pq = PriorityQueue()
                pq.put(twt.trends.rank, twt)
                country_trends[twt.countryCode.lower()] = pq
        return country_trends
    
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
                    pq.put(twt.trends.rank, twt)
                    state_trends[self.city_state[_city]] = pq
        return state_trends