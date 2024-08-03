# Distributed-Key-Value-Store-with-Fault-Tolerance

## Overview

This project implements a distributed key-value store with fault tolerance using replication. The system allows users to specify a replication factor and handles server failures and recoveries.

## Requirements

- Python
- Flask
- SQLite

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/AlessiaRossi/Teleassistance-Supervised-Clustering.git
    cd Distributed-Key-Value-Store-with-Fault-Tolerance
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

1. Start the Flask application:
    ```sh
    python run.py
    ```

2. The application will be available at `http://127.0.0.1:5000`.

## API Endpoints

- `POST /write`: Write a key-value pair.
- `GET /read/<key>`: Read a value by key.
- `DELETE /delete/<key>`: Delete a key-value pair.
- `POST /fail/<int:node_id>`: Simulate a node failure.
- `POST /recover/<int:node_id>`: Recover a failed node.
- `GET /nodes`: Get the status of all nodes.

