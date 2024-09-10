# Design Document

### System Architecture

The system is composed of multiple replica nodes managed by a replication manager. Each node is an instance of the `ReplicaNode` class, which handles individual operations such as read, write, and delete. The `ReplicationManager` class manages these nodes and ensures data replication across them.

- ## Directory Descriptions
The project structure of the application is organized into the following directories:
```plaintext
Distributed-Key-Value-Store-with-Fault-Tolerance/
├── app/    
│   ├── __init__.py  
│   ├── routes.py  
│   ├── models.py 
    ├── consistent_hash.py
├── tests/  
│   ├── db/
│   ├── test_fault_tolerance.py  
│   ├── test_performance.py   
├── db/
│   ├── replica_0.db
│   ├── replica_1.db
│   ├── replica_2.db
├── README.md  
├── requirements.txt
├── run.py
├── client.py
```
### Directory Structure
### `app/`
This directory contains the main application code, including initialization, routing, and models.  
- **`__init__.py/`**: Initializes the Flask application and sets up configurations.
- **`routes.py`**: Defines the API endpoints and their corresponding request handlers.
- **`model.py`**: Contains the data models and business logic for the key-value store.
- **`consistent_hash.py`**: This subdirectory contains the implementation of the consistent hashing algorithm used for data distribution.
### `test/`
This directory contains the test cases for the application.  
- **`db/-`**: Contains test databases used during testing.
- **`test_fault_tolerance.py`**: Contains test cases to verify the fault tolerance capabilities of the system.
- **`test_performance.py`**: Contains test cases to measure the performance of the system under different conditions.
### `db/`
This directory contains the database files for the replicas.  
- **`replica_0.db`**: Database file for the first replica node.
- **`replica_1.db`**: Database file for the second replica node.
- **`replica_2.db`**: Database file for the third replica node.
### `README.md/`
Provides an overview of the project, including setup instructions, usage, and API documentation.
### `requirements.txt`
Lists the Python dependencies required to run the application.
### `run.py`
The main entry point for starting the Flask application.
### `client.py`
A command-line interface (CLI) for interacting with the key-value store, allowing users to perform operations like setting replication strategies, writing, reading, and deleting key-value pairs, and simulating node failures and recoveries.
A command-line interface (CLI) for interacting with the key-value store, allowing users to perform operations like setting replication strategies, writing, reading, and deleting key-value pairs, and simulating node failures and recoveries.
- ## Components

- **ReplicaNode**: Handles operations on individual replicas such as reading, writing, and deleting key-value pairs. It ensures that each replica can independently manage its data.
- **ReplicationManager**: Manages multiple replicas and handles the replication factor.It ensures that data is consistently replicated across nodes and manages node failures and recoveries.
- **Flask Application**: Provides RESTful API endpoints for interacting with the key-value store. It allows users to perform operations via HTTP requests, such as writing, reading, and deleting key-value pairs, as well as managing node failures and recoveries.

- ## Consistency Model

The system uses eventual consistency, where updates to a key-value pair are propagated to all replicas eventually. This model balances consistency and availability, ensuring that the system remains available even if some nodes fail.

- ## Replication Strategies

The system supports two replication strategies to ensure availability and fault tolerance:

### Full Replication

- **Description**: Each node contains a complete copy of all data. This model ensures maximum availability and fault tolerance, as any node can respond to any read or write request.
- **Advantages**: Maximum availability and fault tolerance.
- **Disadvantages**: Inefficient in terms of storage usage and higher write latency due to the need to update all replicas.

### Consistent Hashing

- **Description**: Data is distributed among nodes using a consistent hashing algorithm. This model balances the load among nodes and ensures that each node contains only a portion of the data, improving storage efficiency.
- **Advantages**: Better storage efficiency and load balancing among nodes.
- **Disadvantages**: Increased complexity in managing replicas and potential read latency if the requested data is not present on the current node.

The distributed key-value store with fault tolerance uses eventual consistency to balance data consistency and availability. The full replication and consistent hashing strategies ensure that data remains available even in the event of node failures, improving the system's efficiency and fault tolerance.

- ## Fault Tolerance Strategies

- **Replication**: Data is replicated across multiple nodes to ensure availability.
- **Node Failure Handling**: The system can simulate node failures and recoveries. When a node recovers, it synchronizes its data with active nodes to ensure consistency.

 ### Future Implementations

- **Advanced Consistency Models**: Implement stronger consistency models like linearizability or causal consistency.
- **Dynamic Replication Factor**: Allow dynamic adjustment of the replication factor based on load and performance.
- **Distributed Transactions**: Support for distributed transactions to ensure atomicity across multiple operations.

- ## Experiments

- **Fault Tolerance Testing**: Simulate server failures and recoveries to test the system's fault tolerance.
- **Performance Measurement**: Measure the performance differences between various replication strategies.

- ## Conclusion

This project demonstrates a basic implementation of a distributed key-value store with fault tolerance. It provides a foundation for further enhancements and experiments in distributed systems and fault-tolerant architectures.