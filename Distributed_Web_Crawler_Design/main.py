import time
import json
import yaml
import argparse
import hashlib
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            self.config_data = yaml.safe_load(file)

    # @property
    # def spider_config(self):
    #     return self.config_data.get('spider', {})

    @property
    def user_agent_list(self):
        return self.config_data.get('spider', {}).get('user_agent', [])


    @property
    def kafka_config(self):
        return self.config_data.get('kafka', {})

    @property
    def cassandra_config(self):
        return self.config_data.get('cassandra', {})


from kafka import KafkaProducer, KafkaConsumer
from cassandra.cluster import Cluster

# Pool of proxy servers
PROXY_POOL = ['http://proxy1.com:8080', 'http://proxy2.com:8080', ...]

import random
import re, requests
from bs4 import BeautifulSoup


class URLFetcher:
    def __init__(self, user_agent_list):
        self.user_agent_list = user_agent_list

    def fetch(self, url):
        # Read IDs from file and generate URLs
        with open('ids.txt', 'r') as file:
            ids = file.readlines()
            new_urls = [f"https://play.google.com/store/apps/details?id={id.strip()}" for id in ids]

        # Randomly select a User-Agent
        user_agent = random.choice(self.user_agent_list)
        
        # Fetch web page using randomly selected User-Agent and proxy
        proxy = random.choice(PROXY_POOL)
        response = requests.get(url, proxies={"http": proxy, "https": proxy}, headers={'User-Agent': user_agent})

        # If received a 403 error (Forbidden), change the proxy and try again
        if response.status_code == 403:
            logging.info(f"Proxy {proxy} blocked. Retrying with a different proxy.")
            proxy = random.choice(PROXY_POOL)
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, headers={'User-Agent': user_agent})

        data = self.get_app_details(response)
        
        # Serialize similar_apps_info into a JSON string
        data['similar_apps_info'] = json.dumps(data['similar_apps_info'])
        
        # Add a random delay between requests to avoid being banned for rapid requests
        time.sleep(random.uniform(0.5, 1.5))
        
        return data, new_urls

    @staticmethod
    def get_app_details(response):
        # Extract app details from the webpage content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
    
        # Extract App Name
        app_name = soup.find('h1', itemprop="name").span.text.strip()
    
        # Extract Download Count
        download_section = soup.find_all('div')
        download_count = None
        for section in download_section:
            if "M+" in section.text or "K+" in section.text:
                download_count = section.text
                break
    
        # Extract App Description
        app_description = soup.find('div', {'data-g-id': "description"}).text.strip()
    
        # Extract Rating Score
        rating_div = soup.find('div', {'aria-label': re.compile(r"Rated")})
        if rating_div:
            potential_rating = rating_div.find_previous('div')
            if potential_rating:
                rating_score = potential_rating.get_text(strip=True)
            else:
                rating_score = "Not found"
        else:
            rating_score = "Not found"
    
        # Extract similar apps names and IDs
        similar_apps_links = soup.select('a[href*="/store/apps/details?"]')
        similar_apps_ids = [link.get('href').split('=')[-1] for link in similar_apps_links]
        similar_apps_names = [link.find('span', string=True).text for link in similar_apps_links if
                              link.find('span', string=True)]
    
        # Create a dictionary of similar apps using app IDs as keys and app names as values
        similar_apps_dict = dict(zip(similar_apps_ids, similar_apps_names))
    
        return {
            'app_name': app_name,
            'download_count': download_count,
            'app_description': app_description,
            'rating_score': rating_score,
            'similar_apps_info': similar_apps_dict
        }


from cassandra.query import SimpleStatement
from cassandra.policies import DowngradingConsistencyRetryPolicy


class DataProcessor:
    def __init__(self, kafka_config, cassandra_config, fetcher):
        self.kafka_config = kafka_config
        self.cassandra_config = cassandra_config
        self.fetcher = fetcher
        
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
        # Send fetched URLs to Kafka
        for url in urls:
            hash_key = hashlib.md5(url.encode()).hexdigest()
            try:
                # Send message to Kafka with a partition key
                self.producer.send(self.kafka_config['topic_name'], key=hash_key, value=url)
            except Exception as e:
                logging.error(f"Failed to send URL {url} to Kafka: {e}")

    def store_data_in_cassandra(self, url, data):
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
            logging.error(f"Failed to store data for URL {url} in Cassandra: {e}")

    def process(self, url):
        fetched_data, new_urls = self.fetcher.fetch(url)
        
        self.send_urls_to_kafka(new_urls)
        self.store_data_in_cassandra(url, fetched_data)

        return f"Processed and stored data for {url}"

    def handle_url(self, url):
        # This method is run in a new thread for each URL consumed from Kafka
        fetched_data, new_urls = self.fetcher.fetch(url)
        self.send_urls_to_kafka(new_urls)
        self.store_data_in_cassandra(url, fetched_data)

    def consume_urls_from_kafka(self, max_threads=10):
        # Consume URLs from Kafka and process them
        consumer = KafkaConsumer(
            self.kafka_config['topic_name'],
            bootstrap_servers=self.kafka_config['bootstrap_servers'],
            group_id=self.kafka_config.get('group_id', None),  # Using group_id, partitions can be automatically balanced across multiple consumers
            auto_offset_reset='earliest'
        )
        # 1. Urls are processed using thread pools
        with ThreadPoolExecutor(max_threads) as executor:
            for message in consumer:
                url = message.value
                executor.submit(self.handle_url, url)
        # 2. threading.Thread(target=self.handle_url, args=(url,)).start()  # Use threading to handle urls


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Web scraper and data processor for Google Play store apps.")
    parser.add_argument("config_file", help="Path to the configuration file in YAML format.")
    args = parser.parse_args()

    config = Config(args.config_file)
    fetcher = URLFetcher(config.user_agent_list)
    processor = DataProcessor(config.kafka_config, config.cassandra_config, fetcher)

    processor.consume_urls_from_kafka(max_threads=config.spider_config['max_threads'])
