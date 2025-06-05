import time
import json
import yaml
import argparse
import hashlib
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from proxy_manager import ProxyManager
from url_fetcher import URLFetcher
from zookeeper_service import ZookeeperService

logging.basicConfig(level=logging.INFO)


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            self.config_data = yaml.safe_load(file)
        # 1. 服务启动时：注册到Zookeeper
        self.zk_service = ZookeeperService("localhost:2181")

    @property
    def spider_config(self):
        return self.config_data.get('spider', {})

    @property
    def kafka_config(self):
        return self.config_data.get('kafka', {})

    @property
    def cassandra_config(self):
        return self.config_data.get('cassandra', {})

    @property
    def proxy_pool(self):
        return self.config_data.get('proxy_pool', [])


from kafka import KafkaProducer, KafkaConsumer
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra.policies import DowngradingConsistencyRetryPolicy


class DataProcessor:
    def __init__(self, kafka_config, cassandra_config, fetcher, config):
        self.kafka_config = kafka_config
        self.cassandra_config = cassandra_config
        self.fetcher = fetcher
        self.config = config

        # Set up KafkaProducer with settings
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            retries=kafka_config.get('retries', 5),
            compression_type='gzip'
        )

        # Set up Cassandra with retry policy
        self.cluster = Cluster(
            cassandra_config['hosts'],
            port=cassandra_config['port'],
            default_retry_policy=DowngradingConsistencyRetryPolicy()
        )
        self.session = self.cluster.connect(cassandra_config['keyspace'])

    def send_urls_to_kafka(self, urls):
        # Check if the Kafka service is online
        kafka_service = self.config.zk_service.discover_service('kafka_service_name')
        if not kafka_service:
            logging.error("Kafka service is not online or not registered.")
            return

        # Send fetched URLs to Kafka
        for url in urls:
            hash_key = hashlib.md5(url.encode()).hexdigest()
            try:
                # Send message to Kafka with a partition key
                self.producer.send(self.kafka_config['topic_name'], key=hash_key, value=url)
            except Exception as e:
                logging.error(f"Failed to send URL {url} to Kafka. Error: {e}")

    def store_data_in_cassandra(self, url, data):
        # Check if the Cassandra service is online
        cassandra_service = self.config.zk_service.discover_service('cassandra_service_name')
        if not cassandra_service:
            logging.error("Cassandra service is not online or not registered.")
            return

        # Dynamically generate the CQL query string
        column_names = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))

        # Create the INSERT query including the URL
        query = f"INSERT INTO {self.cassandra_config['table']} (url, {column_names}) VALUES (%s, {placeholders})"

        # Execute the CQL query
        try:
            params = [url] + list(data.values())
            self.session.execute(query, params)
        except Exception as e:
            logging.error(f"Failed to store data for URL {url} in Cassandra. Error: {e}")

    # def process(self, url):
    #     fetched_data, new_urls = self.fetcher.fetch(url)
    #     self.send_urls_to_kafka(new_urls)
    #     self.store_data_in_cassandra(url, fetched_data)
    #
    #     return f"Processed and stored data for {url}"

    # def handle_url(self, url):
    #     # This method is run in a new thread for each URL consumed from Kafka
    #     fetched_data, new_urls = self.fetcher.fetch(url)
    #     self.send_urls_to_kafka(new_urls)
    #     self.store_data_in_cassandra(url, fetched_data)

    def handle_url(self, url):
        # This method is run in a new thread for each URL consumed from Kafka
        fetched_data, new_urls = self.fetcher.fetch(url)
        if fetched_data is None:
            logging.error(f"Failed to fetch and process {url} after retries.")
            return
        self.send_urls_to_kafka(new_urls)
        self.store_data_in_cassandra(url, fetched_data)

    def consume_urls_from_kafka(self, max_threads=10):
        # Consume URLs from Kafka and process them
        consumer = KafkaConsumer(
            self.kafka_config['topic_name'],
            bootstrap_servers=self.kafka_config['bootstrap_servers'],
            group_id=self.kafka_config.get('group_id', None),
            # Using group_id, partitions can be automatically balanced across multiple consumers
            auto_offset_reset='earliest'
        )
        # 1. Urls are processed using thread pools
        with ThreadPoolExecutor(max_threads) as executor:
            for message in consumer:
                url = message.value
                executor.submit(self.handle_url, url)
        # 2. threading.Thread(target=self.handle_url, args=(url,)).start()  # Use threading to handle urls


import atexit

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Web scraper and data processor for Google Play store apps.")
    parser.add_argument("config_file", help="Path to the configuration file in YAML format.")
    args = parser.parse_args()

    # Initialize configuration
    config = Config(args.config_file)

    # Register our service to ZooKeeper when the program starts
    service_path = "spider"  # Change to an appropriate service path
    service_value = "Service for web scraping Google Play store apps"
    service_identifier = config.zk_service.register_service(service_path, service_value)

    # Use atexit to ensure our service is deregistered when the program stops or crashes
    atexit.register(config.zk_service.remove_service, service_path, service_identifier)

    # Discover dependent services (like Kafka or Cassandra) from ZooKeeper
    kafka_service = config.zk_service.discover_service('kafka_service_name')
    cassandra_service = config.zk_service.discover_service('cassandra_service_name')

    # Ensure both services are discovered before proceeding
    if not kafka_service:
        logging.error("Kafka service is not online or not registered.")
        exit(1)

    if not cassandra_service:
        logging.error("Cassandra service is not online or not registered.")
        exit(1)

    # If both services are discovered, proceed with the normal logic
    proxy_manager = ProxyManager(config.proxy_pool)
    fetcher = URLFetcher(config.spider_config['user_agent'], proxy_manager)

    # Start periodic validation in a separate thread
    threading.Thread(target=proxy_manager.run_periodic_validation).start()

    processor = DataProcessor(config.kafka_config, config.cassandra_config, fetcher, config)
    processor.consume_urls_from_kafka(max_threads=config.spider_config['max_threads'])
