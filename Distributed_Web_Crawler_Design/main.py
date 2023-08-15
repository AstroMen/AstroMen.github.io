import yaml
import argparse
import hashlib
import logging
import threading


logging.basicConfig(level=logging.INFO)


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            self.config_data = yaml.safe_load(file)

    @property
    def spider_config(self):
        return self.config_data.get('spider', {})

    @property
    def kafka_config(self):
        return self.config_data.get('kafka', {})

    @property
    def cassandra_config(self):
        return self.config_data.get('cassandra', {})


from kafka import KafkaProducer
from kafka import KafkaConsumer
from cassandra.cluster import Cluster

class URLFetcher:
    def __init__(self, user_agent):
        self.user_agent = user_agent

    def fetch(self, url):
        # 使用 user_agent 去抓取网页数据
        # 伪代码：从网页中提取数据和新的URLs
        data = f"Data from {url}"
        new_urls = ["http://example.com/new1", "http://example.com/new2"]
        return data, new_urls


class DataProcessor:
    def __init__(self, kafka_config, cassandra_config):
        self.kafka_config = kafka_config
        self.cassandra_config = cassandra_config
        # self.producer = KafkaProducer(bootstrap_servers=kafka_config['bootstrap_servers'])
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            retries=kafka_config.get('retries', 5),  # Add retries
            compression_type='gzip'  # Use gzip compression
        )
        
        # 对于Cassandra的重试机制，可以考虑使用cassandra的RetryPolicy

        self.cluster = Cluster(cassandra_config['hosts'], port=cassandra_config['port'])
        self.session = self.cluster.connect(cassandra_config['keyspace'])

    def send_urls_to_kafka(self, urls):
    for url in urls:
        hash_key = hashlib.md5(url.encode()).hexdigest()
        try:
            # key: The partition in which messages are stored
            self.producer.send(self.kafka_config['topic_name'], key=hash_key, value=url)
            # self.producer.send(self.kafka_config['topic_name'], url)
        except Exception as e:
            logging.error(f"Failed to send URL {url} to Kafka: {e}")
            
    def store_data_in_cassandra(self, url, data):
        query = f"INSERT INTO {self.cassandra_config['table']} (url, data) VALUES (%s, %s)"
        try:
            self.session.execute(query, (url, data))
        except Exception as e:
            logging.error(f"Failed to store data for URL {url} in Cassandra: {e}")

    def process(self, url):
        fetcher = URLFetcher(config.spider_config['user_agent'])
        fetched_data, new_urls = fetcher.fetch(url)

        self.send_urls_to_kafka(new_urls)
        self.store_data_in_cassandra(url, fetched_data)

        return f"Processed and stored data for {url}"

    def handle_url(self, url):
        # 这个方法会在一个新线程中运行，用于处理从Kafka消费的每一个URL
        fetched_data, new_urls = self.fetcher.fetch(url)
        self.send_urls_to_kafka(new_urls)
        self.store_data_in_cassandra(url, fetched_data)

    def consume_urls_from_kafka(self):
        consumer = KafkaConsumer(
            self.kafka_config['topic_name'],
            bootstrap_servers=self.kafka_config['bootstrap_servers'],
            auto_offset_reset='earliest',  # 从最早的消息开始消费
            group_id='crawler-group'  # 使用group_id，可以在多个消费者之间自动均衡分区
        )

        for message in consumer:
            url = message.value
            # 使用线程处理URL
            threading.Thread(target=self.handle_url, args=(url,)).start()



def main():
    parser = argparse.ArgumentParser(description="Distributed Crawler using Kafka and Cassandra.")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to the config.yaml file.")
    args = parser.parse_args()

    config = Config(args.config)

    processor = DataProcessor(config.kafka_config, config.cassandra_config)
    result = processor.process("http://example.com")
    processor.consume_urls_from_kafka()

    print(result)


if __name__ == '__main__':
    main()
