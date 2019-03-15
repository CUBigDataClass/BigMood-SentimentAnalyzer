import time
from config.location_service_config import CACHE
from service.Location_Service import *
import os

path = os.path.join(os.path.curdir, CACHE['location'])
ls = LocationService(path, CACHE['dump_interval'])

print(ls.get_coordinates_for_city({'city': 'denver', 'country': 'US'}))
time.sleep(5)
print(ls.get_coordinates_for_city({'city': 'new delhi', 'country': 'IN'}))
time.sleep(4)
print(ls.get_coordinates_for_city({'city': 'boulder', 'country': 'US'}))
print(ls.get_coordinates_for_city({'city': 'blahblahblah', 'country': 'US'}))
time.sleep(4)
