---
layout: post
title:  "Distributed Web Crawler Design"
date:   2023-08-14
categories: jekyll update
tags: 
  - System Design 
---

## Introduction

In an era abundant with digital content, web crawlers have become pivotal for data retrieval and aggregation. However, traditional crawlers often face scalability, resilience, and efficiency challenges. The distributed web crawler system detailed in this article addresses these challenges by leveraging the capabilities of distributed databases and message brokers, facilitating the process of extracting app details from the Google Play store, transmitting them to Apache Kafka, and ultimately storing them in the Apache Cassandra database.

<p align="center">
    <br> English | <a href="Distributed_Web_Crawler_Design-CN.md">中文</a>
</p>
    Using Kafka and Cassandra
    
## Design Goals

1. Employ multi-threading for faster crawling.
2. Use randomized user-agents and a proxy pool to circumvent bans.
3. Implement Apache Kafka as a mid-level data storage mechanism, offering a buffering system ensuring no data loss.
4. Store the scraped data in the Apache Cassandra database, ensuring high availability and scalability for voluminous data.

## Code Link
Click here to access the code [https://github.com/AstroMen/AstroMen.github.io/tree/main/Distributed_Web_Crawler_Design](https://github.com/AstroMen/AstroMen.github.io/tree/main/Distributed_Web_Crawler_Design)

## Sample Configuration File (config.yaml)

```yaml
spider:
  user_agent: ["Mozilla/5.0 ...", "Mozilla/5.0 ..."]
  max_threads: 10
kafka:
  bootstrap_servers: ["kafka-server1:9092", "kafka-server2:9092"]
  retries: 5
  topic_name: "webpage-urls"
  group_id: "google-play-crawlers"
cassandra:
  hosts: ["cassandra-node1", "cassandra-node2"]
  port: 9042
  keyspace: "spider_data"
  table: "app_data"
proxy_pool: ["http://proxy1.com:8080", "http://proxy2.com:8080", ...]
```
All configurations, including user-agent, Kafka, Cassandra, and proxy pool, are read from the configuration file by the script.

## How to Run

To execute the script, ensure that the necessary libraries are installed and use the following command:
```bash
$ python spider.py config.yaml
```
Ensure the path to the configuration file is correct and adjust as per your setup.

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
    app_name TEXT,
    download_count TEXT,
    app_description TEXT,
    rating_score TEXT,
    similar_apps_info TEXT  -- Store as JSON string
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
   - Consumes URLs from Kafka's "webpage-urls" topic
   - Responsible for web page scraping

### Data Processor
   - Processes raw web page data
   - Transforms it into the desired format

### Data Storage
   - Stores the transformed data in Cassandra

### URL Distributor
   - Discovers new URLs from the scraped web pages
   - Pushes them back to Kafka's "webpage-urls" topic

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
   - Pushes new URLs back into Kafka's "webpage-urls" topic

## 4. Advantages and Features

### Distributed and Scalability
   - Adding more consumers to handle increased workloads

### Fault Tolerance
   - Both Kafka and Cassandra are designed for high availability

### Resilience
   - With the inherent fault tolerance of distributed systems, your web crawler is less likely to suffer from outages.

### Deduplication
   - Using Bloom filters or similar to avoid re-crawling the same URLs

### Cost Efficiency
   - With distributed systems, you can harness the power of multiple machines, often leading to cost savings.

## 5. Possible Improvements

### Kafka Stream Processing
   - Utilizing Kafka Streams or ksqlDB for additional data handling

### Data Cleansing
   - Cleaning and preprocessing data before storing

### Enhanced Cassandra Data Model
   - Incorporating secondary indexes, materialized views, etc.

### Rate Limiting
   - Incorporate a more sophisticated rate-limiting system to prevent IP bans or respect the robots.txt file.

### Parallel Processing
   - Improve the crawler's speed by implementing more advanced parallel processing techniques or algorithms.

### Data Enrichment
   - Enhancing the stored data by integrating with third-party services or databases.

### Monitoring and Alerts
   - Implement monitoring for system health, and set up alerts for potential issues or anomalies.

