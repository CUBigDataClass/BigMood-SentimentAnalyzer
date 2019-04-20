import time
import sys
import os

sys.path.append(os.getcwd())

from config.conf import DUMP_INTERVAL
from Location_Service import *

ls = LocationService(DUMP_INTERVAL['dump_interval'])

print(ls.get_coordinates_for_city({'city': 'denver', 'country': 'US'}))
time.sleep(5)
print(ls.get_coordinates_for_city({'city': 'new delhi', 'country': 'IN'}))
time.sleep(4)
print(ls.get_coordinates_for_city({'city': 'boulder', 'country': 'US'}))
print(ls.get_coordinates_for_city({'city': 'blahblahblah', 'country': 'US'}))
time.sleep(4)
