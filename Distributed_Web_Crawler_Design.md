# Distributed Web Crawler Design
<p align="center">
    <br> English | <a href="Distributed_Web_Crawler_Design-CN.md">中文</a>
</p>
    Using Kafka and Cassandra

## 1. Setting Up Resources in Cassandra and Kafka
### Cassandra:
#### Create Keyspace:
In Cassandra, you can utilize CQL (Cassandra Query Language) to set up a keyspace and a table.

First, launch the CQL shell:
```bash
cqlsh
```

To create a keyspace:
```cql
CREATE KEYSPACE IF NOT EXISTS spider_data WITH REPLICATION = {
    'class' : 'SimpleStrategy', 
    'replication_factor' : 1 
};
```
Here, we created a keyspace named spider_data. The SimpleStrategy and replication_factor decide how the data is replicated across the cluster. For production, you might want to use NetworkTopologyStrategy and set a replication factor for each data center.

#### Create Table:
Ensure you're in the keyspace we just created and switch to the keyspace:
```cql
USE spider_data;
```

Then, create the table:
```cql
CREATE TABLE IF NOT EXISTS web_content (
    url TEXT PRIMARY KEY,
    data TEXT
);
```
Here, we made a table named web_content with url as its primary key.

### Kafka:
#### Create Topic:
Setting up a topic in Kafka is straightforward, assuming your Kafka broker and Zookeeper are up and running.

Use the kafka-topics.sh script to initiate a new topic:
```bash
kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic spider_urls
```
In this instance, we established a topic named spider_urls. Ensure the Zookeeper address (localhost:2181 here) matches your setup. Adjust the --replication-factor and --partitions parameters according to your specific needs.

## 2. System Components

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

## 3. Workflow

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

## 4. Advantages and Features

### Distributed and Scalability
   - Adding more consumers to handle increased workloads

### Fault Tolerance
   - Both Kafka and Cassandra are designed for high availability

### Deduplication
   - Using Bloom filters or similar to avoid re-crawling the same URLs

## 5. Possible Improvements

### Kafka Stream Processing
   - Utilizing Kafka Streams or ksqlDB for additional data handling

### Data Cleansing
   - Cleaning and preprocessing data before storing

### Enhanced Cassandra Data Model
   - Incorporating secondary indexes, materialized views, etc.
