---
layout: post
title:  "Working with GorillaMux in Go"
date:   2024-01-27
categories: jekyll update
tags: 
  - RESTful
  - Golang
---

## Introduction to gorilla/mux

`gorilla/mux` is a powerful HTTP router and dispatcher for Golang. It provides enhanced features for request routing based on URL paths, methods, headers, and query parameters. It's particularly useful for building RESTful APIs where precise control over request handling is required.

### Installation

To get started with `gorilla/mux`, you need to install the package in your Go workspace. This can be done using the `go get` command as follows:

```bash
go get -u github.com/gorilla/mux
```

## gorilla/mux vs Gin

While both `gorilla/mux` and Gin are popular choices for web development in Go, they serve slightly different purposes:

- **gorilla/mux**:
  - Focuses mainly on routing and dispatching.
  - Offers fine-grained control over request handling.
  - Works closer to the standard `net/http` package style.
  - Ideal for developers who prefer manual handling and more control.

- **Gin**:
  - A full-featured web framework.
  - High performance due to its use of httprouter.
  - Comes with a wide range of features out-of-the-box like parameter binding, validation, etc.
  - More beginner-friendly and easier to set up for a full application.

## REST API CRUD Example with gorilla/mux

In this section, we'll create a simple REST API using `gorilla/mux`. This API will demonstrate CRUD (Create, Read, Update, Delete) operations and incorporate goroutines for handling concurrent tasks efficiently.
We integrate Error Handling, Middleware Integration, and Data Validation into our REST API using `gorilla/mux`.

### Setting up the Project and Dependencies

First, ensure you have `gorilla/mux` installed:

```bash
go get -u github.com/gorilla/mux
```

Next, create a new Go file, for instance, `main.go`, and set up your basic imports and main function:

```go
package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
    "github.com/gorilla/mux"
    "strings"
    "sync"
)

type User struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

var users []User // This would typically be a database
```

### Middleware for Logging

Introduce middleware to log incoming requests:

```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        log.Printf("Request received: %s %s", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
    })
}
```

### CRUD Handlers with Integrated Error Handling and Data Validation

#### Create (POST) with Data Validation

Let's start by handling user creation:

```go
func createUser(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    var user User
    body, err := ioutil.ReadAll(r.Body)
    if err != nil || json.Unmarshal(body, &user) != nil || strings.TrimSpace(user.Name) == "" || strings.TrimSpace(user.Email) == "" {
        http.Error(w, "Invalid user data", http.StatusBadRequest)
        return
    }

    user.ID = fmt.Sprintf("%d", len(users)+1) // Generate a new ID
    users = append(users, user)
    json.NewEncoder(w).Encode(user)
}
```

#### Read (GET) with Error Handling

For reading user data, we'll implement two handlers: one for fetching a user by ID and one for fetching all users.

Fetch user by ID:

```go
func getUserByID(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    params := mux.Vars(r)
    for _, item := range users {
        if item.ID == params["id"] {
            json.NewEncoder(w).Encode(item)
            return
        }
    }
    http.Error(w, "User not found", http.StatusNotFound)
}
```

Fetch all users:

```go
func getAllUsers(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(users)
}
```

#### Update (PUT) with Error Handling and Data Validation

For updating user data:

```go
func updateUser(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    params := mux.Vars(r)
    for index, item := range users {
        if item.ID == params["id"] {
            users = append(users[:index], users[index+1:]...)
            var user User
            body, err := ioutil.ReadAll(r.Body)
            if err != nil || json.Unmarshal(body, &user) != nil || strings.TrimSpace(user.Name) == "" || strings.TrimSpace(user.Email) == "" {
                http.Error(w, "Invalid user data", http.StatusBadRequest)
                return
            }
            user.ID = params["id"]
            users = append(users, user)
            json.NewEncoder(w).Encode(user)
            return
        }
    }
    http.Error(w, "User not found", http.StatusNotFound)
}
```

#### Delete (DELETE) with Error Handling

For deleting a user:

```go
func deleteUser(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    params := mux.Vars(r)
    for index, item := range users {
        if item.ID == params["id"] {
            users = append(users[:index], users[index+1:]...)
            json.NewEncoder(w).Encode(item)
            return
        }
    }
    http.Error(w, "User not found", http.StatusNotFound)
}
```

### Handling Concurrency with Goroutines

Suppose you want to perform multiple tasks concurrently in a request, such as fetching data from different sources. Here's how you can use goroutines and `sync.WaitGroup`:

```go
func handleConcurrentTasks(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    var wg sync.WaitGroup

    tasks := 3
    wg.Add(tasks)

    for i := 1; i <= tasks; i++ {
        go func(taskID int) {
            defer wg.Done()
            log.Printf("Task %d is being processed\n", taskID)
            // Perform your concurrent task here
        }(i)
    }

    wg.Wait()
    json.NewEncoder(w).Encode("All tasks completed")
}
```

### Setting Up Routes, Middleware, and Starting the Server

Finally, set up your routes, apply middleware, and start the server:

```go
func main() {
    r := mux.NewRouter()

    // Apply middleware
    r.Use(loggingMiddleware)

    // CRUD routes
    r.HandleFunc("/users", getAllUsers).Methods("GET")
    r.HandleFunc("/user", createUser).Methods("POST")
    r.HandleFunc("/user/{id}", getUserByID).Methods("GET")
    r.HandleFunc("/user/{id}", updateUser).Methods("PUT")
    r.HandleFunc("/user/{id}", deleteUser).Methods("DELETE")
    r.HandleFunc("/tasks", handleConcurrentTasks).Methods("GET")

    log.Fatal(http.ListenAndServe(":8080", r))
}
```

By integrating logging middleware, error handling, and data validation directly into our handlers, we create a robust, maintainable, and scalable REST API.
