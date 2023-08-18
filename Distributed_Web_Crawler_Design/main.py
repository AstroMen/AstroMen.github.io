import time
import json
import yaml
import argparse
import hashlib
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
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

import random
import re, requests
from bs4 import BeautifulSoup


class URLFetcher:
    def __init__(self, user_agent_list, proxy_pool):
        self.user_agent_list = user_agent_list
        self.proxy_pool = proxy_pool
        self.base_url = 'https://play.google.com/store/apps/details?id={}'

    def fetch_single_url(self, url):
        # Randomly select a User-Agent
        user_agent = random.choice(self.user_agent_list)

        # Fetch web page using randomly selected User-Agent and proxy
        proxy = random.choice(self.proxy_pool)

        try:
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, headers={'User-Agent': user_agent})
            response.raise_for_status()  # This will raise an HTTPError for 4xx and 5xx status codes
        except requests.HTTPError as e:
            logging.error(f"Failed to fetch the URL {url} with error: {e}")
            proxy = random.choice(self.proxy_pool)
            logging.info(f"Retrying with a different proxy: {proxy}")
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, headers={'User-Agent': user_agent})

        data = self.get_app_details(response.text)

        # Serialize similar_apps_info into a JSON string
        data['similar_apps_info'] = json.dumps(data['similar_apps_info'])

        # Add a random delay between requests to avoid being banned for rapid requests
        time.sleep(random.uniform(0.5, 1.5))
        return data

    def fetch(self, max_threads=10):
        new_urls = []
        with open('ids.txt', 'r') as f:
            for line in f:
                new_urls.append(self.base_url.format(line.strip()))

        # 使用线程池来并发爬取
        with ThreadPoolExecutor(max_threads) as executor:
            results = list(executor.map(self.fetch_single_url, new_urls))

        return results

    @staticmethod
    def get_app_details(html_content):
        # Extract app details from the webpage content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # App Name
        app_name = soup.find('h1', itemprop="name").span.text.strip()

        # Download Count
        download_div = soup.find('div', string='Downloads')
        if download_div:
            # Finding the parent div
            parent_div = download_div.find_parent()
            if parent_div:
                # Extracting the nested div's text (i.e., "1B+")
                download_count = parent_div.find('div').text
            else:
                download_count = "Not found"
        else:
            download_count = "Not found"

        # App Description
        app_description = soup.find('div', {'data-g-id': "description"}).text.strip()

        # Rating Score (Modified as per requirement)
        rating_div = soup.find('div', itemprop="starRating")
        if rating_div:
            rating_score = rating_div.text.strip()
        else:
            rating_score = "Not found"

        # Extracting similar apps names and IDs:
        similar_apps_links = soup.select('a[href*="/store/apps/details?"]')
        similar_apps = {link.get('href').split('=')[-1]: link.find('span', string=True).text for link in
                        similar_apps_links
                        if link.find('span', string=True)}

        # Extracting App Category
        app_categories_links = soup.select('a[aria-label][href*="/store/apps/category/"]')
        app_categories = [link.get('aria-label') for link in app_categories_links]

        # Extracting Developer Name
        developer_div = soup.find('div', class_='Vbfug auoIOc')
        developer_name = developer_div.find('span').text if developer_div else "Not found"

        # Extracting Review Count
        review_count_div = soup.find('div', class_='g1rdde')
        review_count = review_count_div.text.strip() if review_count_div else "Not found"

        # Extract the relevant script tag
        script_tags = soup.find_all('script', type="application/ld+json")
        relevant_script_content = None
        for script in script_tags:
            json_data = json.loads(script.string)
            if json_data.get("@type") == "SoftwareApplication" and json_data.get("name") == app_name:
                relevant_script_content = json_data
                break
        # Extract the necessary details from the relevant script content
        if relevant_script_content:
            extracted_data = {
                "name": relevant_script_content.get("name", "N/A"),
                "url": relevant_script_content.get("url", "N/A"),
                "description": relevant_script_content.get("description", "N/A"),
                "operatingSystem": relevant_script_content.get("operatingSystem", "N/A"),
                "applicationCategory": relevant_script_content.get("applicationCategory", "N/A"),
                "contentRating": relevant_script_content.get("contentRating", "N/A"),
                "author": relevant_script_content.get("author", {}).get("name", "N/A"),
                "ratingValue": relevant_script_content.get("aggregateRating", {}).get("ratingValue", "N/A"),
                "ratingCount": relevant_script_content.get("aggregateRating", {}).get("ratingCount", "N/A"),
                "price": relevant_script_content.get("offers", [{}])[0].get("price", "N/A"),
                "priceCurrency": relevant_script_content.get("offers", [{}])[0].get("priceCurrency", "N/A"),
            }
        else:
            extracted_data = {}

        return {
            'App Name': app_name,
            'Download Count': download_count,
            'App Description': app_description,
            'Rating Score': rating_score,
            'Similar Apps': similar_apps,
            'App Categories': app_categories,
            'Developer Name': developer_name,
            'Review Count': review_count,
            'More App Data': extracted_data,
        }


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

    def handle_url(self, url):
        # This method is run in a new thread for each URL consumed from Kafka
        fetched_results = self.fetcher.fetch()
        for fetched_data, new_urls in fetched_results:
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
    fetcher = URLFetcher(config.spider_config['user_agent'], config.proxy_pool)
    processor = DataProcessor(config.kafka_config, config.cassandra_config, fetcher, config)
    processor.consume_urls_from_kafka(max_threads=config.spider_config['max_threads'])
