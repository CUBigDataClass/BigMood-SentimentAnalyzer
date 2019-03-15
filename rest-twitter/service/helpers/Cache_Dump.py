import time
import os
import csv
from threading import Thread

from constants.Constants import *

class Cache_Dump(Thread):
    def __init__(self, file_path, cache, cache_dump_interval):
        Thread.__init__(self)
        self.file_path = file_path
        self.cache = cache
        self.cache_dump_interval = cache_dump_interval

    def run(self):
        while True:
            print(self.getName() + " is running!")
            time.sleep(self.cache_dump_interval)
            temp_file_name = self.file_path + str(time.time_ns())
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
            writer = csv.writer(file, delimiter=',')
            for k, v in cache.items():
                writer.writerow([k.get_location(), k.get_country(), v[LAT], v[LON]])
