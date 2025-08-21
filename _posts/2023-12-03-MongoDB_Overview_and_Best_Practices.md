---
layout: post
title:  "MongoDB Overview and Best Practices"
date:   2023-12-03
categories: jekyll update
tags: 
  - MongoDB
  - Database
lang: en
---

MongoDB is a popular NoSQL database known for its flexibility and scalability. This document covers the basics of MongoDB, including creation, CRUD operations, optimization techniques, and practical application scenarios.

## Creating a MongoDB Database

- **Automatic Creation**: MongoDB creates a database when you first store data in that database (such as creating a new collection).
- **Using a Database**: Use the `use` command to switch to a specific database. If it doesn't exist, MongoDB creates it when you first store data.

    ```bash
    use myNewDatabase
    ```

- **Inserting Data**: Use `insertOne` or `insertMany` to insert data.

    ```javascript
    db.collectionName.insertOne({ name: "John Doe", age: 30 })
    db.collectionName.insertMany([{ name: "Alice", age: 25 }, { name: "Bob", age: 27 }])
    ```

## CRUD Operations

### Create

- `insertOne`: Inserts a single document into a collection.

    ```javascript
    db.collectionName.insertOne({ name: "John Doe", age: 30 })
    ```

- `insertMany`: Inserts multiple documents into a collection.

    ```javascript
    db.collectionName.insertMany([{ name: "Alice", age: 25 }, { name: "Bob", age: 27 }])
    ```

### Read

- `findOne`: Finds the first document that matches the query.

    ```javascript
    db.collectionName.findOne({ name: "John Doe" })
    ```

- `find`: Finds all documents that match the query.

    ```javascript
    db.collectionName.find({ age: { $gt: 25 } })
    ```

### Update

- `updateOne`: Updates the first document that matches the query.

    ```javascript
    db.collectionName.updateOne({ name: "John Doe" }, { $set: { age: 31 } })
    ```

- `updateMany`: Updates all documents that match the query.

    ```javascript
    db.collectionName.updateMany({ age: { $gt: 25 } }, { $set: { isActive: true } })
    ```

### Delete

- `deleteOne`: Deletes the first document that matches the query.

    ```javascript
    db.collectionName.deleteOne({ name: "Alice" })
    ```

- `deleteMany`: Deletes all documents that match the query.

    ```javascript
    db.collectionName.deleteMany({ age: { $lt: 30 } })
    ```

## Aggregation

- Aggregations process data records and return computed results.
- `$match`: Filters the documents to pass only those that match the specified condition(s) to the next pipeline stage.
- `$group`: Groups input documents by a specified identifier expression and applies the accumulator expression(s), such as `$sum`, to each group.

    ```javascript
    db.collectionName.aggregate([
      { $match: { isActive: true } },
      { $group: { _id: "$age", count: { $sum: 1 } } }
    ])
    ```

## Indexing

- **Why Indexing**: Indexes support the efficient execution of queries. Without indexes, MongoDB must perform a collection scan.
- **Creating an Index**: Use `createIndex` to create an index on a field or fields.

    ```javascript
    db.collectionName.createIndex({ name: 1 })
    ```

- **When to Use Indexing**: Indexing is critical for read-heavy databases or collections with large amounts of data and complex query patterns.

### Different Types of Indexes in MongoDB

MongoDB offers various types of indexes to optimize query performance. Choosing the right type of index can significantly improve the efficiency of database operations.

#### Single Field Index

- Index on a single field of a document.

    ```javascript
    db.collectionName.createIndex({ fieldName: 1 }) // 1 for ascending order, -1 for descending
    ```

#### Compound Index (Composite Index)

- Index on multiple fields of a document.

    ```javascript
    db.collectionName.createIndex({ field1: 1, field2: -1 })
    ```

#### Multikey Index

- Index on an array field. MongoDB creates separate index entries for each element of the array.

    ```javascript
    db.collectionName.createIndex({ arrayField: 1 })
    ```

#### Text Index

- For efficient searching of string content. It supports searching for words and phrases.

    ```javascript
    db.collectionName.createIndex({ textField: "text" })
    ```

#### Geospatial Index

- Indexes for storing geospatial data (e.g., 2D coordinates or spherical surface data).
- Two types: `2d` for two-dimensional planes and `2dsphere` for spherical surfaces.

    ```javascript
    // For 2D coordinates
    db.collectionName.createIndex({ locationField: "2d" })
    
    // For spherical surfaces
    db.collectionName.createIndex({ locationField: "2dsphere" })
    ```

#### Hashed Index

- Indexes field values using a hash function. Useful for sharding and random access patterns.

    ```javascript
    db.collectionName.createIndex({ fieldToHash: "hashed" })
    ```

Each index type has its specific use case and performance characteristics. Understanding when and how to use these indexes can greatly enhance the performance of MongoDB operations.

## Sharding for Horizontal Scaling

- Sharding is used for distributing data across multiple machines. It is a method for handling data sets that are too large for a single server.

### Practical Application Scenarios

#### E-commerce Website

- **Scenario**: A large e-commerce site with a massive amount of transactions.
- **Use of Sharding**: Shard on `customerId` or `transactionDate` to distribute data and balance load.

#### Social Media Analytics

- **Scenario**: A social media analytics platform dealing with real-time data.
- **Use of Sharding**: Shard on `postId` or `channelId` for efficient real-time data processing.

## Performance Monitoring with explain()

- The `explain()` method provides information about how MongoDB executes a query.
- It can be used to understand the query execution plan, including whether indexes were used.

    ```javascript
    db.collectionName.find({ age: { $gt: 30 } }).explain("executionStats")
    ```

- **Example Use**: If a query is running slower than expected, `explain()` can help identify whether the query is using an index or performing a full collection scan, allowing for appropriate optimization strategies to be applied.

MongoDB offers a flexible and powerful platform for a variety of applications, emphasizing scalability and performance optimization.

