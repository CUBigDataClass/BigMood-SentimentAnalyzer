from threading import Thread
import time

# Logging setup
import logging
import logstash
from config.conf import logstash_host, logstash_port, kafka_topic

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logstash.TCPLogstashHandler(logstash_host, logstash_port, version=1))

from Utils import get_timestamp


class Producer:
    def __init__(self, name, queue):
        self.name = name
        self.queue = queue

    def produce(self, trends):
        total = len(trends)
        if (trends is not None and total > 0):
            for trend in trends:
                if (not self.queue.full()):
                    self.queue.put(trend)
                else:
                    log.error("Queue was full. Rejecting!! Some bug here, consumer may have died or not consuming.")
        log.info("Total number of trends inserted for processing :" + str(total))


class ConsumerThread(Thread):

    def __init__(self, name, queue, kafka_producer, mongodb, sentiment_analyzer, sleep_time=10):
        Thread.__init__(self)
        self.setName(name)
        self.setDaemon(daemonic=True)
        self.sleep_time = sleep_time

        self.queue = queue
        self.kafka_producer = kafka_producer
        self.mongodb = mongodb
        self.sentiment_analyzer = sentiment_analyzer

    def run(self):
        log.info("Stream-Consumer thread starting Thread Name:" + self.getName())
        while True:
            if (self.queue.empty()):
                log.debug("Nothing to consume." + self.getName() + " Sleeping for seconds = " + str(self.sleep_time))
                time.sleep(self.sleep_time)
            else:
                log.info("Consumer tr: " + self.getName() + " - consuming countryType data:")
                try:
                    trend_info = self.queue.get()
                    analyzed_tweets = []
                    schema = self.compute_schema_country(trend_info, produce_on_kafka=self.kafka_producer)
                    analyzed_tweets.append(schema)

                    try:
                        # publish the schema to kafka topic
                        self.kafka_producer.send(kafka_topic, value=analyzed_tweets)
                        log.info(f"[CountryType]Thread {self.getName()} : sent :{trend_info} to kafka.")
                    except Exception as e:
                        log.error('[POST]/trendsentiment: Failed to publish data to kafka topic' + str(e))

                    try:
                        # store all tweets that we have analyzed for sentiment in mongo
                        log.debug(f"Inserting analyzed tweets {analyzed_tweets}")

                        self.mongodb.insert_many(analyzed_tweets)
                    except Exception as dbe:
                        log.error('[POST]/trendsentiment: Failed to insert data to mongo db' + str(dbe))
                    log.info("Consumer tr: " + self.getName() + " - Done consuming countryType")
                except Exception as err:
                    log.error(
                        '[POST]/trendsentiment: -> Consumer thread: ' + self.getName() + ' Failed to compute sentiment:' + str(
                            err))

    def compute_schema_country(self, trend_info, produce_on_kafka=None):
        schema = {
            'country': trend_info['country'],
            'countryCode': trend_info['countryCode'],
            'locationType': trend_info['locationType'],
            'city': trend_info.get('city', None),
            'trends': [{
                'name': tweet['name'],
                'sentiment': self.sentiment_analyzer.compute_sentiment_for_country(
                    country_code=trend_info['countryCode'], hashtag=tweet['name'], produce_on_kafka=produce_on_kafka),
            # tweet['sentiment'],
                'rank': tweet['rank'],
                'tweetVolume': tweet['tweetVolume'],
                'url': tweet['url']
            } for tweet in trend_info['twitterTrendInfo']],
            'timestamp': get_timestamp()
        }
        return schema
