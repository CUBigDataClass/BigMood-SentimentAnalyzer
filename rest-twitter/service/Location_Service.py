import sys
import csv

from geopy.geocoders import Nominatim

from service.helpers.Cache_Dump import Cache_Dump

from models.Location_Country_Pair import LocationCountryPair

from constants.Constants import *

sys.path.append('../resources')


class LocationService:

    def __init__(self, cache_location, cache_dump_interval):
        self.user_agent = USER_AGENT
        self.cache = dict()
        self.geocoder = Nominatim(user_agent=self.user_agent)
        self.addressfile = cache_location
        self.load_file(self.addressfile)
        self.cache_dump_interval = cache_dump_interval
        self.dump_thread = Cache_Dump(self.addressfile, self.cache, self.cache_dump_interval)
        self.dump_thread.setDaemon(True)
        self.dump_thread.setName("Coordinates cache dumping thread")
        self.dump_thread.start()

    def load_file(self, file_location):
        try:
            with open(file_location) as file:
                readcsv = csv.reader(file, delimiter=CSV_DELIM)
                for _line in readcsv:
                    # location,country_code,lat,long
                    _key = LocationCountryPair(_line[0].strip(), _line[1].strip())
                    _val = {LAT: float(_line[2]), LON: float(_line[3])}
                    self.cache[_key] = _val
        except FileNotFoundError:
            print("Load file. File not found: " + file_location)

    def getCordinatesforcity(self, query):
        _key = LocationCountryPair(query[CITY], query[COUNTRY])
        if _key in self.cache.keys():
            print("Cached results")
            return self.cache.get(_key)
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
                    print("Can not find lat lon for query:" + query)
                    return lat_lon

            except Exception as ex:
                print(ex)
                return {}

    def getcityboundry(self, query):
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
        self.cache[key] = lat_lon
