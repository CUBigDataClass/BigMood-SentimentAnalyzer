import time
import os
import csv
from threading import Thread

from sentiment_service.constants.Constants import *

class Cache_Dump(Thread):
    """
    This class extends the python Thread class. The purpose of this class to dump the cache to a csv file after a fixed time interval.

    :param string file_path: canonical path of cache dump file.

    :param dict cache: A cache which needs to be dumped at the provided location. The cache key must be of type LocationCountryPair.py.
    The value must be a python type dict containing a LAT and LON(Constants.py) keys and each value is a floating point number.

    :param int cache_dump_interval: an integer to set the dump interval

    :return: A python type list containing a (LAT, LON) pairs. The list is always of size 4. In case if the API
    fails to get bounding box for some reason, it prints the error and return an empty list.
    """
    def __init__(self, file_path, cache, cache_dump_interval):
        Thread.__init__(self)
        self.file_path = file_path
        self.cache = cache
        self.cache_dump_interval = cache_dump_interval

    def run(self):
        """
        As soon as the thread starts it sleeps for the defined dumped_interval.
        The dumping logic:
        1. Create a temp filename.
        2. Make a copy of the current cache and dump it.
        3. If the dump was successful, rename original dump file(if present) as old.
        4. Make the current dump filename as the new dump file.
        5. Sleep again. :)
        """

        while True:
            print(self.getName() + " is running!")
            time.sleep(self.cache_dump_interval)
            temp_file_name = self.file_path + str(int(time.time()*1000))
            try:
                self.dump_to_csv(temp_file_name, self.cache.copy())
                if os.path.isfile(self.file_path):
                    os.rename(self.file_path, self.file_path + 'old')
                os.rename(temp_file_name, self.file_path)
                print("Cache dump successful!")
            except Exception as ex:
                print("failed to save cache" + str(ex))
                break
        print(self.getName() + " is exiting!")

    def dump_to_csv(self, filename, cache):

        with open(filename, mode='w') as file:
            writer = csv.writer(file, delimiter=CSV_DELIM)
            for k, v in cache.items():
                writer.writerow([k.get_location(), k.get_country(), v[LAT], v[LON]])
