# 分布式爬虫系统设计
<p align="center">
    <br> 中文 | <a href="Distributed_Web_Crawler_Design.md">English</a>
</p>
    使用Kafka和Cassandra


## 1. 在Cassandra和Kafka中创建资源
### Cassandra：
#### 创建 Keyspace:
在Cassandra中，你可以使用CQL (Cassandra Query Language) 来创建keyspace和table。

首先, 启动Cassandra的CQL shell:
```bash
cqlsh
```

创建keyspace:
```cql
CREATE KEYSPACE IF NOT EXISTS spider_data WITH REPLICATION = {
    'class' : 'SimpleStrategy', 
    'replication_factor' : 1 
};
```
这里，我们创建了一个名为spider_data的keyspace。SimpleStrategy和replication_factor定义了数据如何在集群中复制。在生产环境中，你可能需要使用NetworkTopologyStrategy并为每个数据中心设置一个复制因子。

#### 创建 Table:
确保你已经选择了刚才创建的keyspace:
```cql
USE spider_data;
```

然后创建table:
```cql
CREATE TABLE IF NOT EXISTS web_content (
    url TEXT PRIMARY KEY,
    app_name TEXT,
    download_count TEXT,
    app_description TEXT,
    rating_score TEXT,
    similar_apps_info TEXT  -- 存储为JSON字符串
);
```
这里, 我们创建了一个名为web_content的table，其中url作为主键。

### Kafka：
#### 创建 Topic:
在Kafka中创建一个topic相对简单。假设你已经启动了Kafka broker和Zookeeper。

使用kafka-topics.sh脚本来创建一个新的topic：
```bash
kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic spider_urls
```
在这里, 我们创建了一个名为spider_urls的topic。确保Zookeeper的地址（在这里是localhost:2181）与你的环境相匹配。--replication-factor和--partitions参数可以根据你的具体需求进行调整。

## 2. 系统组件

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

## 3. 工作流

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

## 4. 优势与特性

### 分布式和可扩展性
   - 增加消费者处理更多任务

### 容错性
   - Kafka和Cassandra设计为高可用性

### 去重
   - 使用布隆过滤器避免重复爬取

## 5. 可能的改进

### Kafka流处理
   - 使用Kafka Streams处理数据

### 数据清洗
   - 在存储前清洗数据

### Cassandra数据模型
   - 使用次级索引和材化视图

