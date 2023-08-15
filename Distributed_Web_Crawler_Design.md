# Distributed Web Crawler Design
<p align="center">
    <br> English | <a href="Distributed_Web_Crawler_Design-CN.md">中文</a>
</p>
    Using Kafka and Cassandra

## 1. System Components

### URL Fetcher
   - Consumes URLs from Kafka's "URL-to-crawl" topic
   - Responsible for web page scraping

### Data Processor
   - Processes raw web page data
   - Transforms it into the desired format

### Data Storage
   - Stores the transformed data in Cassandra

### URL Distributor
   - Discovers new URLs from the scraped web pages
   - Pushes them back to Kafka's "URL-to-crawl" topic

## 2. Workflow

### URL Initialization
   - Seeds the initial set of URLs to be crawled into Kafka

### URL Fetcher
   - Retrieves URLs from Kafka
   - Scrapes the web page content
   - Sends the raw page data to the Data Processor

### Data Processor
   - Parses the page data
   - Stores the structured data in Cassandra
   - Sends newly discovered URLs to the URL Distributor

### URL Distributor
   - Pushes new URLs back into Kafka's "URL-to-crawl" topic

## 3. Advantages and Features

### Distributed and Scalability
   - Adding more consumers to handle increased workloads

### Fault Tolerance
   - Both Kafka and Cassandra are designed for high availability

### Deduplication
   - Using Bloom filters or similar to avoid re-crawling the same URLs

## 4. Possible Improvements

### Kafka Stream Processing
   - Utilizing Kafka Streams or ksqlDB for additional data handling

### Data Cleansing
   - Cleaning and preprocessing data before storing

### Enhanced Cassandra Data Model
   - Incorporating secondary indexes, materialized views, etc.
