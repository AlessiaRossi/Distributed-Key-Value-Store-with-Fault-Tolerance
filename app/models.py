import sqlite3
import os

class ReplicaNode:
    def __init__(self, node_id, port):
        # Initializes a replica node with a unique identifier and a port.
        self.node_id = node_id
        self.port = port
        self.name_db = f'replica_{node_id}.db'  # Name of the database file for this node.
        self.db_path = os.path.join('db', self.name_db)  # Path to the database file for this node.
        self.alive = True  # Initial state of the node is active.
        self.create_db_directory() # Creates the 'db' directory if it does not exist.
        self._initialize_db()  # Initializes the database if it does not exist.

    def create_db_directory(self):
        # Creates the 'db' directory if it does not already exist.
        if not os.path.exists('db'):
            os.makedirs('db')  # Creates the directory.

    def _initialize_db(self):
        # Creates the 'kv_store' table if it does not already exist in the database.
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)  # Connects to the database.
            cursor = conn.cursor()  # Creates a cursor to execute SQL commands.
            cursor.execute('''CREATE TABLE IF NOT EXISTS kv_store (key TEXT PRIMARY KEY, value TEXT)''')  # Creates the table.
            conn.commit()  # Commits the changes to the database.
            conn.close()  # Closes the connection to the database.

    def write(self, key, value):
        # Writes a key-value pair to the database only if the node is active.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Connects to the database.
            cursor = conn.cursor()  # Creates a cursor to execute SQL commands.
            cursor.execute('''INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)''', (key, value))  # Inserts or updates the data.
            conn.commit()  # Commits the changes to the database.
            conn.close()  # Closes the connection to the database.

    def read(self, key):
        # Reads the value associated with a key from the database only if the node is active.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Connects to the database.
            cursor = conn.cursor()  # Creates a cursor to execute SQL commands.
            cursor.execute('''SELECT value FROM kv_store WHERE key=?''', (key,))  # Selects the value for the key.
            result = cursor.fetchone()  # Retrieves the result of the query.
            conn.close()  # Closes the connection to the database.
            return result[0] if result else None  # Returns the value if found, otherwise None.

    def delete(self, key):
        # Deletes the key-value pair from the database only if the node is active.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Connects to the database.
            cursor = conn.cursor()  # Creates a cursor to execute SQL commands.
            cursor.execute('''DELETE FROM kv_store WHERE key=?''', (key,))  # Deletes the data associated with the key.
            conn.commit()  # Commits the changes to the database.
            conn.close()  # Closes the connection to the database.

    def key_exists(self, key):
        # Checks if a key exists in the database only if the node is active.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Connects to the database.
            cursor = conn.cursor()  # Creates a cursor to execute SQL commands.
            cursor.execute('''SELECT 1 FROM kv_store WHERE key=?''', (key,))  # Checks if the key exists.
            exists = cursor.fetchone() is not None  # Checks if at least one row was found.
            conn.close()  # Closes the connection to the database.
            return exists  # Returns True if the key exists, otherwise False.

    def fail(self):
        # Simulates the failure of the node by setting its state to inactive.
        self.alive = False

    def recover(self, active_nodes):
        # Recovers the node and synchronizes data with other active nodes.
        if not self.alive:
            self.alive = True  # Sets the node's state to active.
            self.sync_with_active_nodes(active_nodes)  # Synchronizes with other active nodes.

    def is_alive(self):
        # Returns the current state of the node.
        return self.alive

    def sync_with_active_nodes(self, active_nodes):
        # Synchronizes the node's data with other active nodes.
        for node in active_nodes:
            if node.is_alive() and node.node_id != self.node_id:
                conn = sqlite3.connect(node.db_path)  # Connects to the other node's database.
                cursor = conn.cursor()  # Creates a cursor to execute SQL commands.
                cursor.execute('''SELECT key, value FROM kv_store''')  # Selects all key-value pairs.
                rows = cursor.fetchall()  # Retrieves all rows.
                conn.close()  # Closes the connection to the database.
                for key, value in rows:
                    self.write(key, value)  # Writes each key-value pair to the current node's database.

class ReplicationManager:
    def __init__(self, replication_factor):
        # Initializes the replication manager with a specified replication factor.
        self.replication_factor = replication_factor
        # Creates a list of replica nodes with unique identifiers and ports.
        self.nodes = [ReplicaNode(i, 5000 + i) for i in range(replication_factor)]

    def write_to_replicas(self, key, value):
        # Writes a key-value pair to all active replica nodes.
        for node in self.nodes:
            if node.is_alive():  # Checks if the node is active.
                node.write(key, value)  # Writes the data to the node.

    def read_from_replicas(self, key):
        # Reads the value associated with a key from active replica nodes.
        for node in self.nodes:
            if node.is_alive():  # Checks if the node is active.
                result = node.read(key)  # Reads the value from the node.
                if result is not None:  # If the result is not None, returns the value and a message.
                    return {'value': result, 'message': f'Read from replica {node.node_id}'}
        # If no node returned a value, returns an error message.
        return {'value': None, 'message': 'All replicas failed or key not found'}

    def delete_from_replicas(self, key):
        # Deletes a key from all replica nodes.
        for node in self.nodes:
            node.delete(key)  # Calls the delete method on each node.

    def key_exists_in_replicas(self, key):
        # Checks if a key exists in at least one of the active replica nodes.
        for node in self.nodes:
            if node.is_alive() and node.key_exists(key):  # Checks if the key exists in the active node.
                return True  # Returns True if the key exists.
        return False  # Returns False if the key was not found in any active node.

    def fail_node(self, node_id):
        # Simulates the failure of a specific node identified by node_id.
        if 0 <= node_id < len(self.nodes):  # Checks if the node ID is valid.
            self.nodes[node_id].fail()  # Calls the fail method of the node.

    def recover_node(self, node_id):
        # Recovers a specific node and synchronizes data with other active nodes.
        if 0 <= node_id < len(self.nodes):  # Checks if the node ID is valid.
            self.nodes[node_id].recover(self.nodes)  # Calls the recover method of the node.

    def get_nodes_status(self):
        # Returns the status of all nodes in a list of dictionaries.
        return [
            {
                'node_id': node.node_id,  # ID of the node.
                'status': 'alive' if node.is_alive() else 'dead',  # Status of the node (active or inactive).
                'port': node.port  # Port of the node.
            }
            for node in self.nodes
        ]
