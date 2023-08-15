import time
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

    @property
    def spider_config(self):
        return self.config_data.get('spider', {})

    @property
    def kafka_config(self):
        return self.config_data.get('kafka', {})

    @property
    def cassandra_config(self):
        return self.config_data.get('cassandra', {})


from kafka import KafkaProducer, KafkaConsumer
from cassandra.cluster import Cluster

PROXY_POOL = ['http://proxy1.com:8080', 'http://proxy2.com:8080', ...]

import random
import re, requests
from bs4 import BeautifulSoup

# 添加一个User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
    # ... 可以添加更多 ...
]

class URLFetcher:
    def __init__(self, user_agent_list):
        self.user_agent_list = user_agent_list

    def fetch(self, url):
        # 从文件读取IDs并生成URLs
        with open('ids.txt', 'r') as file:
            ids = file.readlines()
            new_urls = [f"https://play.google.com/store/apps/details?id={id.strip()}" for id in ids]

        # 随机选择一个User-Agent
        user_agent = random.choice(self.user_agent_list)
        
        # 使用随机选择的User-Agent和代理抓取网页
        proxy = random.choice(PROXY_POOL)
        response = requests.get(url, proxies={"http": proxy, "https": proxy}, headers={'User-Agent': user_agent})

        # 如果收到403，更换代理再次尝试
        if response.status_code == 403:
            logging.info(f"Proxy {proxy} blocked. Retrying with a different proxy.")
            proxy = random.choice(PROXY_POOL)
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, headers={'User-Agent': user_agent})

        data = self.get_app_details(response)
        
        # 请求之间添加随机间隔，防止请求速度过快被封禁
        time.sleep(random.uniform(0.5, 1.5))
        
        return data, new_urls

    @staticmethod
    def get_app_details(response):
        soup = BeautifulSoup(response.text, 'html.parser')
    
        # App Name
        app_name = soup.find('h1', itemprop="name").span.text.strip()
    
        # Download Count
        download_section = soup.find_all('div')
        download_count = None
        for section in download_section:
            if "M+" in section.text or "K+" in section.text:
                download_count = section.text
                break
    
        # App Description
        app_description = soup.find('div', {'data-g-id': "description"}).text.strip()
    
        # Extracting the rating score using a more robust method:
        rating_div = soup.find('div', {'aria-label': re.compile(r"Rated")})
        if rating_div:
            potential_rating = rating_div.find_previous('div')
            if potential_rating:
                rating_score = potential_rating.get_text(strip=True)
            else:
                rating_score = "Not found"
        else:
            rating_score = "Not found"
    
        # Extracting similar apps names and IDs:
        similar_apps_links = soup.select('a[href*="/store/apps/details?"]')
        # Parsing the similar apps' IDs from the href attributes
        similar_apps_ids = [link.get('href').split('=')[-1] for link in similar_apps_links]
        similar_apps_names = [link.find('span', string=True).text for link in similar_apps_links if
                              link.find('span', string=True)]
    
        # Creating the dictionary of similar apps using app IDs as keys and app names as values:
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
        # KafkaProducer settings
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            retries=kafka_config.get('retries', 5),  # Add retries
            compression_type='gzip'  # Use gzip compression
        )
        # Cassandra settings with retry policy
        self.cluster = Cluster(
            cassandra_config['hosts'], 
            port=cassandra_config['port'],
            default_retry_policy=DowngradingConsistencyRetryPolicy()
        )
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
        # 动态生成CQL查询字符串
        column_names = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        
        # 注意，我在这里添加了url字段
        query = f"INSERT INTO {self.cassandra_config['table']} (url, {column_names}) VALUES (%s, {placeholders})"
        
        # 执行CQL查询
        try:
            # 这里需要将url加入参数列表
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
        # 这个方法会在一个新线程中运行，用于处理从Kafka消费的每一个URL
        # fetcher = URLFetcher(config.spider_config['user_agent'])    
        fetched_data, new_urls = self.fetcher.fetch(url)
        self.send_urls_to_kafka(new_urls)
        self.store_data_in_cassandra(url, fetched_data)

    def consume_urls_from_kafka(self, max_threads=10):
        consumer = KafkaConsumer(
            self.kafka_config['topic_name'],
            bootstrap_servers=self.kafka_config['bootstrap_servers'],
            auto_offset_reset='earliest',  # 从最早的消息开始消费
            group_id='crawler-group'  # 使用group_id，可以在多个消费者之间自动均衡分区
        )
        # threading.Thread(target=self.handle_url, args=(url,)).start()  # 使用线程处理URL
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for message in consumer:
                url = message.value
                # 使用线程池处理URL
                executor.submit(self.handle_url, url)
                

def main():
    parser = argparse.ArgumentParser(description="Distributed Crawler using Kafka and Cassandra.")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to the config.yaml file.")
    args = parser.parse_args()
    config = Config(args.config)

    # 初始化URLFetcher时，传入User-Agent列表
    fetcher = URLFetcher(USER_AGENTS)
    processor = DataProcessor(config.kafka_config, config.cassandra_config, fetcher)  # 传入 fetcher
    # result = processor.process("http://example.com")  # initialize to start crawler
    # print(result)
    processor.consume_urls_from_kafka()


if __name__ == '__main__':
    main()

