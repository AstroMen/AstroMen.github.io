import yaml
import argparse

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
        self.producer = KafkaProducer(bootstrap_servers=kafka_config['bootstrap_servers'])
        self.cluster = Cluster(cassandra_config['hosts'], port=cassandra_config['port'])
        self.session = self.cluster.connect(cassandra_config['keyspace'])

    def send_urls_to_kafka(self, urls):
        for url in urls:
            self.producer.send(self.kafka_config['topic_name'], url)

    def store_data_in_cassandra(self, url, data):
        query = f"INSERT INTO {self.cassandra_config['table']} (url, data) VALUES (%s, %s)"
        self.session.execute(query, (url, data))

    def process(self, url):
        fetcher = URLFetcher(config.spider_config['user_agent'])
        fetched_data, new_urls = fetcher.fetch(url)

        self.send_urls_to_kafka(new_urls)
        self.store_data_in_cassandra(url, fetched_data)

        return f"Processed and stored data for {url}"


def main():
    parser = argparse.ArgumentParser(description="Distributed Crawler using Kafka and Cassandra.")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to the config.yaml file.")
    args = parser.parse_args()

    config = Config(args.config)

    processor = DataProcessor(config.kafka_config, config.cassandra_config)
    result = processor.process("http://example.com")

    print(result)


if __name__ == '__main__':
    main()
