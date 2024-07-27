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
                    