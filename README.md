
# Distributed-Key-Value-Store-with-Fault-Tolerance
To read the README.md in Italian, click [here](README_ita.md)

## Index

1. [Overview](#1-overview)
   - [Key Features](#key-features)
2. [Enviroment setup](#2-enviroment-setup)
3. [Installation](#3-installation)
4. [Running the Application](#4-running-the-application)
5. [API Endpoints](#5-api-endpoints)
6. [Project Architecture](#6-project-architecture)
7. [Performance Testing](#7-performance-testing)
8. [Report](#8-report)
9. [Conclusion](#9-conclusion)

## **1. Overview**

This project implements a distributed key-value store with fault tolerance using replication. The system allows users to specify a replication factor and handles server failures and recoveries.

### Key Features:
- **Fault Tolerance**: This system ensures that data remains accessible even when individual nodes fail.
- **Data Distribution**: Data is replicated across multiple nodes to guarantee availability.
- **Consistency**: Mechanisms in place prevent data discrepancies between nodes.
- **Scalability**: New nodes can be easily added to expand the system’s capacity.
- **CRUD Operations**: The system supports basic operations like creating, reading, updating, and deleting data.

## **2. Enviroment setup**

Before running the code, it's important to take some precautions and set up your environment properly. Follow these steps:

1. Create a Virtual Environment:
   - Open your terminal or command prompt.
   - Run the following command to create a virtual environment named "venv":
   ```bash
   python -m venv venv
   ```

2. Activate the Virtual Environment:
   - If you're using Windows:
   ```bash
   .\venv\Scripts\activate
   ```
   - If you're using Unix or MacOS:
   ```bash
   source ./venv/Scripts/activate
   ```

3. Deactivate the Environment (When Finished):
   - Use the following command to deactivate the virtual environment:
   ```bash
   deactivate
   ```

4. Install Dependencies:
   - After cloning the project and activating the virtual environment, install the required dependencies using:
   ```bash
   pip install -r requirements.txt
   ```

5. If your Python version used to generate the virtual environment doesn't contain an updated version of pip, update pip using:
   ```bash
   pip install --upgrade pip
   ```

### Requirements

- Python
- Flask
- SQLite

## **3. Installation**

1. Clone the repository:

```bash
git clone https://github.com/AlessiaRossi/Distributed-Key-Value-Store-with-Fault-Tolerance.git
cd Distributed-Key-Value-Store-with-Fault-Tolerance
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## **4. Running the Application**

1. Start the Flask application:
```bash
python run.py
```

2. The application will be available at `http://127.0.0.1:5000`.

3. Use the command-line interface (CLI) to interact with the application:
```bash
python client.py
```

4. Follow the on-screen options to perform various operations such as setting replication strategy, writing key-value pairs, reading values, deleting key-value pairs, failing nodes, recovering nodes, and demonstrating fail-recover behavior.

5. Run the test suite:
```bash
python -m unittest test_performance.py
```

## **5. API Endpoints**

- `POST /write`: Write a key-value pair.
- `GET /read/<key>`: Read a value by key.
- `DELETE /delete/<key>`: Delete a key-value pair.
- `POST /fail/<int:node_id>`: Simulate a node failure.
- `POST /recover/<int:node_id>`: Recover a failed node.
- `GET /nodes`: Get the status of all nodes.

---

## **6. Project Architecture**

The system operates using a distributed architecture where the data is replicated and stored across multiple nodes, ensuring redundancy and fault tolerance. Each node is designed to handle key-value pairs and can recover its state after a failure by syncing with other active nodes.

### ReplicaNode and ReplicationManager

#### ReplicaNode
Each `ReplicaNode` acts as a single node in the replication strategy. It stores key-value data in its local SQLite database and supports operations such as:
- Writing (`write`)
- Reading (`read`)
- Deleting (`delete`)
- Simulating a failure (`fail`)
- Recovery after failure (`recover`)

#### ReplicationManager
This component is responsible for managing the replication strategy across multiple `ReplicaNode`s.
- **Replication Strategies**: Supports two strategies for distributing data:
  1. **Full Replication**: Writes to all active nodes.
  2. **Consistent Hashing**: Distributes data based on consistent hashing to reduce load and balance data.
- Key functions include:
  - Writing to nodes (`write_to_replicas`)
  - Reading from nodes (`read_from_replicas`)
  - Simulating node failures (`fail_node`)
  - Recovering nodes (`recover_node`)
  
---

## **7. Performance Testing**

This project includes performance tests that measure the effectiveness of the system under different replication strategies. The tests evaluate key metrics, such as the time taken for write, read, fail, and recover operations.

#### Test Scenarios:
1. **Write Performance - Full Replication**: Measures the time required to write 100 key-value pairs across all nodes.
2. **Read Performance - Full Replication**: Measures the time required to read 100 key-value pairs.
3. **Node Failure and Recovery - Full Replication**: Simulates the failure and recovery of nodes and measures system recovery time.
4. **Write Performance - Consistent Hashing**: Measures the time taken to write 100 key-value pairs using consistent hashing.
5. **Read Performance - Consistent Hashing**: Measures the time taken to read 100 key-value pairs.
6. **Node Failure and Recovery - Consistent Hashing**: Simulates node failure and recovery under consistent hashing.

Run the performance tests with:
```bash
python -m unittest test_performance.py
```

### Experimental Results and Analysis
Refer to the [report.md](report.md) for the results and in-depth analysis of the experimental tests conducted on this system.

---

## **8. Report**

Refer to the [report.md](report.md) for experimental results and analysis.

---

## **9. Conclusion**

This distributed key-value store provides a robust solution for maintaining high data availability even during node failures. It leverages advanced replication strategies like consistent hashing to balance load and improve scalability. With flexible fault tolerance mechanisms, this project offers a reliable foundation for distributed systems.
