# 分布式爬虫系统设计
<p align="center">
    <br> 中文 | <a href="Distributed_Web_Crawler_Design.md">English</a>
</p>
    使用Kafka和Cassandra

## 1. 系统组件

### URL Fetcher
   - 从Kafka的"URL-to-crawl" topic中消费URLs
   - 负责网页抓取

### Data Processor
   - 处理原始网页数据
   - 转化为所需格式

### Data Storage
   - 存储到Cassandra数据库中

### URL Distributor
   - 发现新的URLs
   - 将它们发送到Kafka的"URL-to-crawl" topic

## 2. 工作流

### URL的初始化
   - 放入初始的待爬取URLs到Kafka

### URL Fetcher
   - 从Kafka获取URL
   - 抓取页面内容
   - 发送原始页面数据给Data Processor

### Data Processor
   - 解析页面数据
   - 存储数据到Cassandra
   - 将新URLs发送给URL Distributor

### URL Distributor
   - 将新URLs推送回Kafka的"URL-to-crawl" topic

## 3. 优势与特性

### 分布式和可扩展性
   - 增加消费者处理更多任务

### 容错性
   - Kafka和Cassandra设计为高可用性

### 去重
   - 使用布隆过滤器避免重复爬取

## 4. 可能的改进

### Kafka流处理
   - 使用Kafka Streams处理数据

### 数据清洗
   - 在存储前清洗数据

### Cassandra数据模型
   - 使用次级索引和材化视图

