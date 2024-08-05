import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
        self.ring = dict()
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    # Hash function to generate a hash key for a given input key
    def _hash(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    # Add a node to the ring
    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f'{node.node_id}:{i}')
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    # Remove a node from the ring
    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f'{node.node_id}:{i}')
            del self.ring[key]
            self.sorted_keys.remove(key)

    # Get the node responsible for the given key
    def get_node(self, key):
        if not self.ring:
            return None
        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]