import time
from threading import Thread

from constants.Constants import *

# Logging setup
import logging
import logstash
from config.conf import logstash_host, logstash_port
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logstash.TCPLogstashHandler(logstash_host, logstash_port, version=1))


class Cache_Dump(Thread):
    """
    This class extends the python Thread class. The purpose of this class to dump the cache to a database collection after a fixed time interval.

    :param string collection: mongodb collection name.

    :param dict cache: A cache which needs to be dumped at the provided location. The cache key must be of type LocationCountryPair.py.
    The value must be a python type dict containing a LAT and LON(Constants.py) keys and each value is a floating point number.

    :param int cache_dump_interval: an integer to set the dump interval

    """

    def __init__(self, collection, things_to_dump, cache_dump_interval):
        Thread.__init__(self)
        self.db_collection = collection
        self.things_to_dump = things_to_dump
        self.cache_dump_interval = cache_dump_interval
        self.DELIM = "__"

    def run(self):
        """
        As soon as the thread starts it sleeps for the defined dumped_interval.
        The dumping logic:
        1. if there is anything to dump, dump it using bunk insert
        2. clear the things to dump if dump was a success.
        3. Sleep again. :)
        """

        while True:
            log.info(self.getName() + " is running!")
            time.sleep(self.cache_dump_interval)
            log.info(self.getName() + " woke up and ready to dump cache in database!")
            try:
                if(len(self.things_to_dump)>0):
                    log.info("Calling bulk insert on mongodb. Total document to insert: " + len(self.things_to_dump))
                    self.db_collection.insert_many(self.convert_to_json(self.things_to_dump), ordered=False)
                    self.things_to_dump.clear()
                else:
                    log.info("Nothing to insert in the database.")
                log.info("Cache dump successful!")
            except Exception as ex:
                log.info("failed to save cache" + str(ex))
                break
        log.info(self.getName() + " is exiting due to an error, Bye!")


    def convert_to_json(self, cache):
        acc = []
        for key, val in cache.items():
            schema = {
                "location_id": key.get_location() + self.DELIM + key.get_country(),
                "coords": {
                    LAT: val[LAT],
                    LON: val[LON]
                }
            }
            acc.append(schema)
        return acc
