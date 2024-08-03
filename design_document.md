## Design Document

### System Architecture

The system is composed of multiple replica nodes managed by a replication manager. Each node is an instance of the `ReplicaNode` class, which handles individual operations such as read, write, and delete. The `ReplicationManager` class manages these nodes and ensures data replication across them.

#### Components

- **ReplicaNode**: Handles operations on individual replicas.
- **ReplicationManager**: Manages multiple replicas and handles the replication factor.
- **Flask Application**: Provides RESTful API endpoints for interacting with the key-value store.

### Consistency Model

The system uses eventual consistency, where updates to a key-value pair are propagated to all replicas eventually. This model balances consistency and availability, ensuring that the system remains available even if some nodes fail.

### Fault Tolerance Strategies

- **Replication**: Data is replicated across multiple nodes to ensure availability.
- **Node Failure Handling**: The system can simulate node failures and recoveries. When a node recovers, it synchronizes its data with active nodes to ensure consistency.

### Future Implementations

- **Advanced Consistency Models**: Implement stronger consistency models like linearizability or causal consistency.
- **Dynamic Replication Factor**: Allow dynamic adjustment of the replication factor based on load and performance.
- **Distributed Transactions**: Support for distributed transactions to ensure atomicity across multiple operations.

### Experiments

- **Fault Tolerance Testing**: Simulate server failures and recoveries to test the system's fault tolerance.
- **Performance Measurement**: Measure the performance differences between various replication strategies.

### Conclusion

This project demonstrates a basic implementation of a distributed key-value store with fault tolerance. It provides a foundation for further enhancements and experiments in distributed systems and fault-tolerant architectures.