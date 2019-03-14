import sys
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import sys

sys.path.append('../config')
import location_service_config  # ignore IDE error here.

sys.path.append('../resources')

import concurrent.futures
from threading import Thread
import csv
import time
import os

LAT = 'lat'
LON = 'lon'


class LocationService:

    def __init__(self, key, params, cache_location):
        self.user_agent = "CUBoulder/BigData"
        self.cache = dict()
        self.geocoder = Nominatim(user_agent=self.user_agent)
        self.addressfile = cache_location
        self.params = params
        self.load_file(self.addressfile)
        self.dump_thread = Cache_Dump(self.addressfile, self.cache)
        self.dump_thread.setDaemon(True)
        self.dump_thread.setName("Coordinates cache dumping thread")
        self.dump_thread.start()

    def load_file(self, file_location):
        try:
            with open(file_location) as file:
                readcsv = csv.reader(file, delimiter=',')
                for _line in readcsv:
                    # location,country_code,lat,long
                    _key = LocationCountryPair(_line[0].strip(), _line[1].strip())
                    _val = {LAT: float(_line[2]), LON: float(_line[3])}
                    self.cache[_key] = _val
        except FileNotFoundError:
            print("Load file. File not found: " + file_location)

    def getCordinatesforcity(self, query):
        _key = LocationCountryPair(query['city'], query['country'])
        if _key in self.cache.keys():
            print("Cached results")
            return self.cache.get(_key)
        else:
            try:
                response = self.geocoder.geocode(query)
                # print(response)
                lat_lon = {}
                if (response is not None):
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
                return response.raw['boundingbox']
            else:
                print("Can not find lat lon for query:" + str(query))
                return bounding_box

        except Exception as ex:
            print(ex)
            return []

    def dump_cache(self, file_name):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(dump_to_csv, {'cache': self.cache, 'filename': file_name})

    def cache_lat_lon(self, key, lat_lon):
        self.cache[key] = lat_lon


def dump_to_csv(params):
    filename = params['filename']
    cache = params['cache']
    with open(filename, mode='w') as file:
        writer = csv.writer(file, delimiter=',')
        for k, v in cache.items():
            writer.writerow([k.get_location(), k.get_country, v[0], v[1]])


class LocationCountryPair:
    def __init__(self, location_name, country_name):
        self.location_name = location_name
        self.country_name = country_name

    def __hash__(self):
        return hash((self.location_name, self.country_name))

    def __eq__(self, other):
        return (self.location_name, self.country_name) == (other.location_name, other.country_name)

    def get_location(self):
        return self.location_name

    def get_country(self):
        return self.country_name


class Cache_Dump(Thread):
    def __init__(self, file_path, cache):
        Thread.__init__(self)
        self.file_path = file_path
        self.cache = cache

    def run(self):
        while True:
            print(self.getName() + " is running!")
            time.sleep(3)
            temp_file_name = self.file_path + str(time.time_ns())
            try:
                self.dump_to_csv(temp_file_name, self.cache.copy())
                if os.path.isfile(self.file_path):
                    os.rename(self.file_path, self.file_path + 'old')
                os.rename(temp_file_name, self.file_path)
                print("Cache dump successful!")
            except Exception as ex:
                print("failed to save cache" + ex)
                break
        print(self.getName() + " is exiting!")

    def dump_to_csv(self, filename, cache):

        with open(filename, mode='w') as file:
            writer = csv.writer(file, delimiter=',')
            for k, v in cache.items():
                writer.writerow([k.get_location(), k.get_country(), v[LAT], v[LON]])
            file.flush()
            file.close()


path = os.path.join(os.path.curdir,location_service_config.CACHE['location'] )
ls = LocationService(location_service_config.OPENCAGEKEY['key'], location_service_config.OPENCAGEPARAMS,
                     path)


print(ls.getCordinatesforcity({'city': 'denver', 'country': 'US'}))
time.sleep(5)
print(ls.getCordinatesforcity({'city': 'new delhi', 'country': 'IN'}))
time.sleep(4)
print(ls.getCordinatesforcity({'city': 'boulder', 'country': 'US'}))
time.sleep(4)

