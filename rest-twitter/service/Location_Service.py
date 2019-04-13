import sys

from geopy.geocoders import Nominatim
from pymongo import MongoClient
from pymongo import ASCENDING

from helpers.Cache_Dump import Cache_Dump

from models.Location_Country_Pair import LocationCountryPair

from constants.Constants import *
from config.mongo_config import MONGO

sys.path.append('../resources')


class LocationService:

    def __init__(self, cache_dump_interval):
        """
        Construct LocationService.
        Provide the time interval at which the current cache will be dumped to the database.

        See Location_Service_Test.py for usage.

        :param int cache_dump_interval: an integer to set the dump interval

        :return: LocationService Object
        """
        self.user_agent = USER_AGENT
        self.local_cache = dict()
        self.things_to_dump = dict()
        self.geocoder = Nominatim(user_agent=self.user_agent)

        # MongoDB setup
        self.client = MongoClient(MONGO["URI_CACHE"])
        self.cache_db = self.client["cache_db"]
        self.lat_lon_cache = self.cache_db["lat_lon_cache"]

        create_index_out = self.lat_lon_cache.create_index([('location_id', ASCENDING)], unique=True)

        self.load_from_database()

        self.cache_dump_interval = cache_dump_interval
        self.dump_thread = Cache_Dump(self.lat_lon_cache, self.things_to_dump, self.cache_dump_interval)
        self.dump_thread.setDaemon(True)
        self.dump_thread.setName("Coordinates cache dumping thread")
        self.dump_thread.start()

    def load_from_database(self):
        try:
            _all_item = self.lat_lon_cache.find()
            for item in _all_item:
                print(item)
                # location,country_code,lat,long
                _loc = item['location_id'].split('__')
                _cords = item['coords']
                _key = LocationCountryPair(_loc[0].strip(), _loc[1].strip())
                _val = {LAT: float(_cords[LAT]), LON: float(_cords[LON])}
                self.local_cache[_key] = _val
        except FileNotFoundError:
            print("Load file. File not found: " + file_location)

    def get_coordinates_for_city(self, query):
        """
        Method to get the geo coordinated for the query.

        :param dict query: the query must be a python type dict. It must contain keys - CITY and COUNTRY which are defined in Constants.py

        :return: A python type dict containing a LAT and LON as keys the each value is a floating point number.
        In case if the API fails to get the geo coordinates for some weird reason, it prints the reason and returns an empty dict.
        """

        _key = LocationCountryPair(query[CITY].strip().lower(), query[COUNTRY].strip().lower())
        if _key in self.local_cache.keys():
            print("Location service using Cached results")
            return self.local_cache.get(_key)
        else:
            try:
                response = self.geocoder.geocode(query)
                lat_lon = {}
                if response is not None:
                    lat_lon[LAT] = response.latitude
                    lat_lon[LON] = response.longitude
                    self.cache_lat_lon(_key, lat_lon)
                    return lat_lon
                else:
                    print("Can not find lat lon for query:" + str(query))
                    return lat_lon

            except Exception as ex:
                print(ex)
                return {}

    def get_city_boundary(self, query):
        """
        Method to get the geo coordinated for the query.

        :param dict query: the query must be a python type dict. It must contain keys - CITY and COUNTRY which are defined in Constant.py

        :return: A python type list containing a (LAT, LON) pairs at each index. The list is always of size 4. In case if the API
        fails to get bounding box for some weird reason, it prints the reason and return an empty list.
        """
        try:
            response = Nominatim(user_agent=self.user_agent, bounded=True).geocode(query)
            bounding_box = []
            if response is not None and response.raw is not None:
                return response.raw[BOUNDING_BOX]
            else:
                print("Can not find lat lon for query:" + str(query))
                return bounding_box

        except Exception as ex:
            print(ex)
            return []

    def cache_lat_lon(self, key, lat_lon):
        self.things_to_dump[key] = lat_lon
        self.local_cache[key] = lat_lon
