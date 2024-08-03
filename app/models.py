import sqlite3
import os

class ReplicaNode:
    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port
        self.db_path = f'replica_{node_id}.db'
        self.alive = True
        self._initialize_db()

    def _initialize_db(self):
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS kv_store (key TEXT PRIMARY KEY, value TEXT)''')
            conn.commit()
            conn.close()

    def write(self, key, value):
        if self.alive:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)''', (key, value))
            conn.commit()
            conn.close()

    def read(self, key):
        if self.alive:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT value FROM kv_store WHERE key=?''', (key,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None

    def delete(self, key):
        if self.alive:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM kv_store WHERE key=?''', (key,))
            conn.commit()
            conn.close()

    def key_exists(self, key):
        if self.alive:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT 1 FROM kv_store WHERE key=?''', (key,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists

    def fail(self):
        self.alive = False

    def recover(self, active_nodes):
        if not self.alive:
            self.alive = True
            self.sync_with_active_nodes(active_nodes)

    def is_alive(self):
        return self.alive

    def sync_with_active_nodes(self, active_nodes):
        for node in active_nodes:
            if node.is_alive() and node.node_id != self.node_id:
                conn = sqlite3.connect(node.db_path)
                cursor = conn.cursor()
                cursor.execute('''SELECT key, value FROM kv_store''')
                rows = cursor.fetchall()
                conn.close()
                for key, value in rows:
                    self.write(key, value)


class ReplicationManager:
    def __init__(self, replication_factor):
        self.replication_factor = replication_factor
        self.nodes = [ReplicaNode(i, 5000 + i) for i in range(replication_factor)]

    def write_to_replicas(self, key, value):
        for node in self.nodes:
            if node.is_alive():
                node.write(key, value)

    def read_from_replicas(self, key):
        for node in self.nodes:
            if node.is_alive():
                result = node.read(key)
                if result is not None:
                    return {'value': result, 'message': f'Read from replica {node.node_id}'}
        return {'value': None, 'message': 'All replicas failed or key not found'}

    def delete_from_replicas(self, key):
        for node in self.nodes:
            node.delete(key)

    def key_exists_in_replicas(self, key):
        for node in self.nodes:
            if node.is_alive() and node.key_exists(key):
                return True
        return False

    def fail_node(self, node_id):
        if 0 <= node_id < len(self.nodes):
            self.nodes[node_id].fail()

    def recover_node(self, node_id):
        if 0 <= node_id < len(self.nodes):
            self.nodes[node_id].recover(self.nodes)

    def get_nodes_status(self):
        return [
            {
                'node_id': node.node_id,
                'status': 'alive' if node.is_alive() else 'dead',
                'port': node.port
            }
            for node in self.nodes
        ]
                    