---
layout: post
title:  "Understanding RESTful Principles with a Simple Demo"
date:   2023-08-11
categories: jekyll update
tags: 
  - RESTful 
---

RESTful principles are the foundation of many modern web services. In this blog, we will explore these principles using a simple demo of a book management system built with Python and Flask.

## What is REST?

Representational State Transfer (REST) is an architectural style that defines a set of constraints to be used for creating web services. These principles make the web service scalable, performant, and easy to use.

## 1. Statelessness

Every request from a client to a server must contain all the information needed to understand and process the request. There should be no session state stored on the server between requests.

**Demo Highlight**:
In our demo, each request (be it to add, update, or delete a book) is independent. The server doesn't maintain any session information about the client.

```python
# All state is handled on the client side. The server doesn't maintain any session about the individual clients.
```

## 2. Client-Server

This principle asserts a clear separation between the client and the server. The client is responsible for the user interface, while the server handles the backend and data storage.

**Demo Highlight**:
Our server-side implementation (Flask app) is independent of the client. Any HTTP client can interact with it.

```python
BASE_URL = 'http://127.0.0.1:5000'
```

## 3. Cacheable

Responses from the server should be explicitly labeled as cacheable or non-cacheable. This helps in improving the performance by reusing previous responses.

**Demo Highlight**:
In our demo, we use a `Cache-Control` header to indicate that the response can be cached for a specific duration.

```python
response.headers['Cache-Control'] = 'public, max-age=300'
```

## 4. Layered System

A client cannot ordinarily tell whether it is connected directly to the end server or to an intermediary along the way. This adds scalability since intermediaries can be introduced to improve performance.

**Demo Highlight**:
We introduced a `DatabaseLayer` class to simulate a separate layer handling the data, showcasing a separation of concerns.

```python
class DatabaseLayer:
    ...
```

## 5. Uniform Interface

Having a consistent and uniform interface simplifies and decouples the architecture, making the system more scalable and modular.

**Demo Highlight**:
Our API endpoints have a consistent structure (e.g., `/book/<book_id>`), and the operations on the data are uniform (using HTTP methods like GET, POST, PUT, DELETE).

```python
api.add_resource(Book, '/book/<int:book_id>')
api.add_resource(BookList, '/books')
```

## 6. Code on Demand (Optional)

Servers can extend the functionality of a client by transferring executable code.

**Note**: This principle is optional and was not showcased in our demo.

## Conclusion

Understanding and implementing RESTful principles can lead to more robust and scalable web services. Our book management system demo showcases these principles in a simple and comprehensible way. As you delve deeper into building web services, always keep these principles in mind to create efficient and user-friendly APIs.

### Demo
#### Server Code (with Layered System and Client-Server principles)
```python
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api, abort

app = Flask(__name__)
api = Api(app)

# --- Layered System ---
# Simple "database" layer for demonstration purposes.
class DatabaseLayer:
    def __init__(self):
        self.data = {}
    
    def get_book(self, book_id):
        return self.data.get(book_id)

    def save_book(self, book_id, book_info):
        self.data[book_id] = book_info
    
    def delete_book(self, book_id):
        if book_id in self.data:
            del self.data[book_id]
    
    def get_all_books(self):
        return self.data

# Initialize our mock database layer
db = DatabaseLayer()

class Book(Resource):
    def get(self, book_id):
        book = db.get_book(book_id)
        if not book:
            abort(404, message=f"Book {book_id} doesn't exist.")
        return {book_id: book}

    def put(self, book_id):
        if 'title' not in request.json or 'author' not in request.json:
            abort(400, message="Both 'title' and 'author' fields are required.")
        
        db.save_book(book_id, {'title': request.json['title'], 'author': request.json['author']})
        return {book_id: db.get_book(book_id)}

    def delete(self, book_id):
        db.delete_book(book_id)
        return {"message": f"Book {book_id} deleted."}

class BookList(Resource):
    def get(self):
        response = make_response(jsonify(db.get_all_books()))
        response.headers['Cache-Control'] = 'public, max-age=300'
        return response

    def post(self):
        book_id = max(db.get_all_books().keys(), default=0) + 1
        if 'title' not in request.json or 'author' not in request.json:
            abort(400, message="Both 'title' and 'author' fields are required.")
        
        db.save_book(book_id, {'title': request.json['title'], 'author': request.json['author']})
        return {book_id: db.get_book(book_id)}, 201

api.add_resource(Book, '/book/<int:book_id>')
api.add_resource(BookList, '/books')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

#### Client Code
```python
import requests

BASE_URL = 'http://127.0.0.1:5000'

# Get list of books
response = requests.get(f"{BASE_URL}/books")
print(response.json())

# Add a new book
new_book = {'title': 'New Book Title', 'author': 'New Book Author'}
response = requests.post(f"{BASE_URL}/books", json=new_book)
print(response.json())

# Get a specific book (assuming the new book got the ID of 1)
response = requests.get(f"{BASE_URL}/book/1")
print(response.json())
```
